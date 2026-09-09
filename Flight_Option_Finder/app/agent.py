import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from app.guards import call_tool
from app.memory import AgentMemory
from app.tools import REGISTRY, TOOL_SCHEMA


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(override=True)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the T10 Flight Option Finder Agent.

Your goal is:

Find and pick a flight within the user's budget.

You are a goal-based ReAct agent.

You have two tools:

1. search_flights
   Searches live flight options using SerpApi.

2. compare_price
   Ranks the returned flight options from cheapest
   to most expensive.

IMPORTANT AGENT BEHAVIOR:

1. For a new flight search, ALWAYS call search_flights first.

2. search_flights requires:
   - from_city
   - to_city
   - departure_date
   - passengers
   - cabin_class

3. NEVER invent a departure date.

4. If the user has not provided a departure date,
   ask the user for the date instead of searching.

5. After receiving search results, ALWAYS call
   compare_price.

6. After compare_price returns, reason over the results.

7. Apply the user's budget.

8. If the user has a preference such as:
   - morning
   - afternoon
   - evening
   - night
   - non-stop

   prefer a flight matching that preference,
   provided it fits the user's budget.

9. If multiple flights satisfy the budget and preference,
   choose the best/cheapest suitable option.

10. If no flight fits the budget:
    clearly say that no available flight fits the budget
    and identify the cheapest available option.

11. NEVER invent:
    - flight numbers
    - prices
    - availability
    - departure times
    - arrival times
    - airlines

12. Use information from the tool results.

13. Remember information from previous turns when
    AgentMemory provides it.

14. If the user asks something like:
    "What is the best option from my saved search?"

    use the previous conversation and memory.

15. Once enough information is available,
    STOP calling tools and provide the final answer.

16. Do not repeatedly call the same tool unnecessarily.
"""


# ============================================================
# MEMORY EXTRACTION
# ============================================================

def _extract_memory_facts(text):
    """
    Extract important flight constraints from the
    user's message.

    Returns:
        budget,
        preferences,
        route,
        departure_date
    """

    budget = None

    preferences = []

    route = None

    departure_date = None

    text_lower = text.lower()

    # --------------------------------------------------------
    # Budget
    # --------------------------------------------------------

    budget_match = re.search(
        r"(?:under|below|within|budget(?:\s+of)?|"
        r"less than)\s*(?:is\s*)*[₹rs.]*\s*([0-9][0-9,]*)",
        text_lower,
    )

    if budget_match:

        budget = int(
            budget_match.group(1).replace(",", "")
        )

    # --------------------------------------------------------
    # Route
    # --------------------------------------------------------

    route_match = re.search(
        r"from\s+([A-Za-z ]+?)\s+to\s+([A-Za-z ]+?)"
        r"(?:\s+on|\s+under|\s+below|\s+within|"
        r"\s+for|\s+with|[.,]|$)",
        text,
        re.I,
    )

    if route_match:

        route = (
            route_match.group(1).strip(),
            route_match.group(2).strip(),
        )

    # --------------------------------------------------------
    # ISO date
    # --------------------------------------------------------

    iso_date_match = re.search(
        r"\b(20\d{2}-\d{2}-\d{2})\b",
        text,
    )

    if iso_date_match:

        departure_date = (
            iso_date_match.group(1)
        )

    # --------------------------------------------------------
    # Month + day
    #
    # Example:
    # September 15
    # Sep 15
    # September 15th
    # --------------------------------------------------------

    month_date_match = re.search(
        r"\b("
        r"january|february|march|april|may|june|july|"
        r"august|september|october|november|december|"
        r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|"
        r"nov|dec"
        r")\s+"
        r"(\d{1,2})(?:st|nd|rd|th)?\b",
        text,
        re.I,
    )

    if month_date_match:

        month = month_date_match.group(1)

        day = int(
            month_date_match.group(2)
        )

        current_year = datetime.now().year

        try:

            parsed = datetime.strptime(
                f"{month} {day} {current_year}",
                "%B %d %Y",
            )

            departure_date = (
                parsed.strftime("%Y-%m-%d")
            )

        except ValueError:

            try:

                parsed = datetime.strptime(
                    f"{month} {day} {current_year}",
                    "%b %d %Y",
                )

                departure_date = (
                    parsed.strftime("%Y-%m-%d")
                )

            except ValueError:

                pass

    # --------------------------------------------------------
    # Preferences
    # --------------------------------------------------------

    preference_map = {
        "morning": "morning",
        "afternoon": "afternoon",
        "evening": "evening",
        "night": "night",
        "non-stop": "non-stop",
        "nonstop": "non-stop",
    }

    for keyword, value in preference_map.items():

        if keyword in text_lower:

            if value not in preferences:

                preferences.append(value)

    return (
        budget,
        preferences,
        route,
        departure_date,
    )


# ============================================================
# OPENAI-COMPATIBLE CLIENT
# ============================================================

def build_client():
    """
    Build the Groq client using the OpenAI-compatible API.
    """

    load_dotenv(override=True)

    key = os.getenv("GROQ_API_KEY")

    if not key:

        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Add it to your .env file."
        )

    return OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1",
    )


# ============================================================
# FLIGHT AGENT
# ============================================================

class FlightAgent:

    def __init__(
        self,
        client=None,
        model=None,
        memory=None,
    ):

        self.client = (
            client
            if client is not None
            else build_client()
        )

        self.model = (
            model
            or os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-120b",
            )
        )

        self.memory = (
            memory
            if memory is not None
            else AgentMemory()
        )

    # ========================================================
    # MODEL CALL
    # ========================================================

    def _model_call(self, messages):

        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOL_SCHEMA,
        )

    # ========================================================
    # RUN AGENT
    # ========================================================

    def run(
        self,
        goal,
        max_steps=6,
        verbose=True,
    ):

        trace = []

        # ----------------------------------------------------
        # Extract memory facts from current request
        # ----------------------------------------------------

        (
            budget,
            preferences,
            route,
            departure_date,
        ) = _extract_memory_facts(goal)

        # ----------------------------------------------------
        # Store current facts in memory
        # ----------------------------------------------------

        self.memory.remember(
            budget=budget,
            preferences=preferences,
            route=route,
            departure_date=departure_date,
        )

        # ----------------------------------------------------
        # Existing memory context
        # ----------------------------------------------------

        memory_line = (
            self.memory.context_summary()
        )

        if departure_date:

            memory_line += (
                f" | departure_date={departure_date}"
            )

        trace.append(
            f"[state] {memory_line}"
        )

        # ----------------------------------------------------
        # Build conversation
        # ----------------------------------------------------

        messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },

            {
                "role": "system",
                "content": (
                    "Current memory/state:\n"
                    + memory_line
                ),
            },

            {
                "role": "user",
                "content": goal,
            },
        ]

        if (
            "saved search" in goal.lower()
            and self.memory.last_answer
        ):
            trace.append("[memory] returned the saved search result")
            return {
                "answer": self.memory.last_answer,
                "trace": trace,
                "memory": self.memory.data,
                "steps": 0,
                "stopped_because": "saved result",
            }

        # ----------------------------------------------------
        # ReAct loop
        # ----------------------------------------------------

        for step in range(
            1,
            max_steps + 1,
        ):

            try:

                response = self._model_call(
                    messages
                )

            except Exception as e:

                trace.append(
                    f"[step {step}] "
                    f"model error: {e}"
                )

                return {
                    "answer": (
                        "I couldn't complete the "
                        "flight search because the "
                        f"model request failed: {e}"
                    ),
                    "trace": trace,
                    "memory": self.memory.data,
                    "steps": step,
                    "stopped_because": "model error",
                }

            message = (
                response.choices[0].message
            )

            # ------------------------------------------------
            # Record assistant message
            # ------------------------------------------------

            assistant_payload = {
                "role": "assistant",
                "content": (
                    message.content
                    or ""
                ),
            }

            tool_calls = getattr(
                message,
                "tool_calls",
                None,
            )

            if tool_calls:

                assistant_payload[
                    "tool_calls"
                ] = [

                    {
                        "id": call.id,

                        "type": "function",

                        "function": {
                            "name": (
                                call.function.name
                            ),
                            "arguments": (
                                call.function.arguments
                            ),
                        },
                    }

                    for call in tool_calls
                ]

            messages.append(
                assistant_payload
            )

            # ------------------------------------------------
            # No tool calls = final answer
            # ------------------------------------------------

            if not tool_calls:

                answer = (
                    message.content
                    or "No final answer was produced."
                )

                self.memory.add_message(
                    {
                        "role": "user",
                        "content": goal,
                    }
                )

                self.memory.add_message(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )
                self.memory.remember(last_answer=answer)

                trace.append(
                    f"[step {step}] done"
                )

                return {
                    "answer": answer,
                    "trace": trace,
                    "memory": self.memory.data,
                    "steps": step,
                    "stopped_because": "final answer",
                }

            # ------------------------------------------------
            # Execute requested tools
            # ------------------------------------------------

            for call in tool_calls:

                name = call.function.name

                raw_arguments = (
                    call.function.arguments
                    or "{}"
                )

                # --------------------------------------------
                # Parse arguments
                # --------------------------------------------

                try:

                    args = json.loads(
                        raw_arguments
                    )

                except json.JSONDecodeError:

                    result_text = (
                        "ERROR: Invalid tool "
                        "arguments returned by model."
                    )

                    trace.append(
                        f"[step {step}] "
                        f"{name} invalid arguments"
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": result_text,
                        }
                    )

                    continue

                # --------------------------------------------
                # Trace tool call
                # --------------------------------------------

                trace.append(
                    f"[step {step}] "
                    f"{name}({args})"
                )

                # --------------------------------------------
                # Execute through guarded executor
                # --------------------------------------------

                try:

                    result = call_tool(
                        name,
                        args,
                        REGISTRY,
                        retries=2,
                        backoff=0.0,
                    )

                    observation = (
                        result.observation
                    )

                except Exception as e:

                    observation = (
                        "ERROR: Tool execution "
                        f"failed: {e}"
                    )

                # --------------------------------------------
                # Determine success/failure
                # --------------------------------------------

                if observation.startswith(
                    "ERROR:"
                ):

                    trace.append(
                        f"[tool error] "
                        f"{observation}"
                    )

                else:

                    trace.append(
                        f"[OK] -> "
                        f"{observation[:1000]}"
                    )

                # --------------------------------------------
                # Return observation to model
                # --------------------------------------------

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": observation,
                    }
                )

        # ----------------------------------------------------
        # Maximum step budget reached
        # ----------------------------------------------------

        answer = (
            "I couldn't complete the flight "
            "selection within the allowed reasoning "
            "steps."
        )

        trace.append(
            "[stop] maximum step budget reached"
        )

        return {
            "answer": answer,
            "trace": trace,
            "memory": self.memory.data,
            "steps": max_steps,
            "stopped_because": "step budget",
        }


# ============================================================
# SIMPLE MANUAL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "T10 Flight Option Finder Agent"
    )

    print("=" * 70)

    agent = FlightAgent()

    result = agent.run(
        """
        Find me a flight from Delhi to Mumbai
        on September 15, 2026.

        My budget is ₹7000.

        I am traveling alone in economy class.

        Prefer a morning flight.
        """
    )

    print("\nFINAL ANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\nAGENT TRACE")
    print("=" * 70)

    for item in result["trace"]:

        print(item)

    print("\nMEMORY")
    print("=" * 70)

    print(result["memory"])

    print("\nSTEPS:", result["steps"])

    print(
        "STOPPED BECAUSE:",
        result["stopped_because"],
    )
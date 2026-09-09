# CSE476 CA1 — T10 Flight Option Finder Agent
## Unit 1 + Unit 2 aligned implementation

Project Overview

The Flight Option Finder Agent is an Agentic AI application whose goal is:

Find and pick a flight within the user's budget.

The agent uses live flight data through SerpApi / Google Flights, compares available prices, remembers user requirements across turns, and selects a suitable option.

Agent Architecture

The project demonstrates the four core parts of an agent:

Goal: Find a suitable flight within the user's budget.

Tools: search_flights() and compare_price().

Memory/State: Stores useful constraints such as budget, route, and preferences.

Loop/Stop: Uses a bounded multi-step ReAct loop and stops when enough information is available.

Agent Flow

User Request
     ↓
    LLM
     ↓
search_flights()
     ↓
Observe Results
     ↓
compare_price()
     ↓
Observe Ranked Results
     ↓
Apply Budget + Preferences
     ↓
Final Answer

Agent Type

The Flight Option Finder is primarily a Goal-Based Agent.

Its planning style is ReAct (Reason + Act):

Decide what action is required.

Call a tool.

Observe the result.

Decide the next action.

Produce the final answer.

Tools

1. search_flights()

Searches live flight options using SerpApi's Google Flights engine.

search_flights(
    from_city,
    to_city,
    departure_date,
    return_date=None,
    passengers=1,
    cabin_class="economy"
)

Example:

search_flights(
    from_city="Delhi",
    to_city="Mumbai",
    departure_date="2026-09-15",
    passengers=1,
    cabin_class="economy"
)

Common city names are converted to IATA codes:

Delhi      → DEL
Mumbai     → BOM
Bengaluru  → BLR
Chennai    → MAA
Hyderabad  → HYD

2. compare_price()

Receives flight search results and ranks them from cheapest to most expensive.

compare_price(search_results)

Memory

AgentMemory allows the agent to remember information across turns, such as:

Budget

Route

Travel preferences

Previous conversation

For example, the user can first ask:

Find me a flight from Delhi to Mumbai on September 15,
2026 under ₹7,000. Prefer morning flights.

Then ask:

What is the best option from my saved search?

The same agent instance can use the earlier conversation and memory.

Live Flight Data

The project uses:

SerpApi
   ↓
Google Flights

Flight prices and availability are live and can change between runs.

LLM

The agent uses a Groq-hosted model through an OpenAI-compatible client.

Default model:

openai/gpt-oss-120b

The LLM decides which tool to call, provides tool arguments, interprets observations, and decides when to stop.

Project Structure

flight_option_finder/
│
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── tools.py
│   ├── memory.py
│   ├── guards.py
│   └── design_review.py
│
├── data/
│   ├── __init__.py
│   └── flights.py
│
├── tests/
│   └── test_project.py
│
├── T10_Flight_Option_Finder_Clean_Live_Demo.ipynb
├── demo.py
├── README.md
├── requirements.txt
└── .env

The current search_flights() implementation uses live SerpApi data. The older data/flights.py mock dataset is not used by the live flight-search tool.

Installation

Create a virtual environment:

python -m venv .venv

Activate it in Git Bash:

source .venv/Scripts/activate

Install dependencies:

pip install -r requirements.txt

If necessary:

pip install serpapi

Environment Setup

Create a .env file in the project root:

SERPAPI_KEY=YOUR_SERPAPI_KEY
GROQ_API_KEY=YOUR_GROQ_API_KEY

Never share or commit API keys.

Test Live Flight Search

Run:

python -c "from app.tools import search_flights; s=search_flights(from_city='Delhi', to_city='Mumbai', departure_date='2026-09-15', passengers=1, cabin_class='economy'); print(s)"

A successful result starts with:

Flight search results: DEL → BOM
Departure date: 2026-09-15

Test Price Comparison

Run:

python -c "from app.tools import search_flights, compare_price; s=search_flights(from_city='Delhi', to_city='Mumbai', departure_date='2026-09-15', passengers=1, cabin_class='economy'); print(compare_price(s))"

The output should start with:

Flights ranked by price:

Run the Agent

After configuring the API keys:

python -m tests.test_live_agent

A successful multi-step trace should contain calls similar to:

[state] ...
[step 1] search_flights(...)
[OK] -> ...
[step 2] compare_price(...)
[OK] -> ...
[step 3] done

The exact flight results and prices may change because the data is live.

Notebook Demonstrations

The clean notebook contains only the important live demonstrations.

Demo 1 — Budget + Preference

Example request:

Find me a flight from Delhi to Mumbai
on September 15, 2026.

My budget is ₹7000.

I am traveling alone in economy class.

Prefer a morning flight.

The agent searches live flights, compares prices, applies the budget and preference, and returns a suitable option.

Demo 2 — Memory

Follow-up:

What is the best option from my saved search?

The same agent instance uses previous conversation and memory.

Demo 3 — No Fit

Example:

Find me a flight from Delhi to Bengaluru
on September 15, 2026.

My budget is ₹4000.

I am traveling alone in economy class.

If no returned flight fits the budget, the agent reports that instead of inventing a result.

Failure Handling

The project handles:

Missing SERPAPI_KEY

Flight API errors

No returned flight options

No flight within the user's budget

Invalid tool arguments

Maximum agent step limit

When no flight fits the budget, the agent should clearly report that fact and identify the cheapest available option when possible.

Requirements Demonstrated

Requirement

Implementation

Goal

Find a flight within budget

Tool 1

search_flights()

Tool 2

compare_price()

Multi-step behavior

Search → Compare → Decide

Memory

AgentMemory + conversation

Agent style

ReAct

Agent type

Goal-based

Live data

SerpApi / Google Flights

Failure handling

API errors, no results, no-fit budget

Stop condition

Final answer / step limit

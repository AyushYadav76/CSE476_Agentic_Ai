# CSE476 CA1 — T10 Flight Option Finder Agent
## Unit 1 + Unit 2 aligned implementation

### 1. Project
T10 is a Flight Option Finder agent. Its goal is to find and pick a flight within the user's budget. The required tools are `search_flights(from, to)` and `compare_price(options)`. Session memory stores the user's budget and preferences. The agent uses a multi-step Plan/Act/Observe/Decide loop instead of simply replying to the user.

### 2.concepts used
The project follows the teaching pattern of a goal, allowed tools, a state-carrying loop and a stop condition. It uses a goal-based/ReAct-style agent: the model decides which tool is needed, receives the tool result, then decides what to do next. Conversation messages are retained and important facts (budget, route and preferences) are pinned as structured memory so they can be reused on a later turn.

### 3.concepts used
Tool calling is implemented with a tool schema plus a Python `REGISTRY` whitelist. The model can request only tools that are declared and registered. Tool execution is hardened with a defended executor: unknown tools are refused, bad arguments are not pointlessly retried, transient failures may be retried, and unusable output is converted into an honest observation. The agent also has a maximum step budget.

### 4. Honest failure
A realistic failure is a tool returning unusable output such as an empty string or an HTML gateway error. The defended executor detects this instead of passing garbage to the model. Another bounded failure is an agent that cannot reach a final answer within the step budget; it stops and says so rather than looping forever.

### 5. Why local flight data?
The flight dataset is local/mock data. This keeps the assessment reproducible and free of paid flight APIs. The important assessment behavior is the agent loop, actual tool calls, memory and decision-making. The `search_flights` tool can later be replaced by a real API without changing the agent architecture.

### 6. Files
- `app/agent.py` — main agent loop, prompt, memory integration, model tool calls.
- `app/tools.py` — the two required T10 tools, registry and tool schemas.
- `app/memory.py` — conversation state and pinned session facts.
- `app/guards.py` — Unit 2 defended tool executor.
- `app/design_review.py` — small offline static audit.
- `data/flights.py` — local flight data.
- `T10_Flight_Option_Finder.ipynb` — assessment notebook.
- `demo.py` — offline architecture demo.
- `requirements.txt` — packages.
- `.env.example` — environment template.

### 7. Live model setup
1. Create a Python 3.10+ environment.
2. Run `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Put your class Groq API key in `GROQ_API_KEY`.
5. Run the notebook in VS Code/Jupyter.
6. Set `USE_LIVE_MODEL = True` for the live tool-calling agent demonstration.




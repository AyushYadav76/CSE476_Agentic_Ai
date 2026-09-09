# ✈️ T10 – Flight Option Finder Agent

An Agentic AI system that searches for available flights and selects the best flight option based on the user's **budget and preferences**.

The project uses **live Google Flights data through SerpApi** and an **LLM through Groq** to demonstrate a real agent loop with tools, memory, decision-making, and failure handling.

---

## 🎯 Project Goal

The goal of this project is to build an AI agent that can:

* Understand the user's flight requirements
* Search for available flights
* Compare flight prices
* Filter flights according to the user's budget
* Consider user preferences such as morning flights
* Remember information from previous turns
* Select the most suitable flight
* Explain when no flight fits the user's budget

---

## 🤖 Agent Architecture

The project follows a simple **Goal → Tools → State → Loop → Stop** architecture.

```text
                    User
                     │
                     ▼
              Flight Agent
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
        search_flights   Memory
              │
              ▼
        Flight Results
              │
              ▼
        compare_price
              │
              ▼
        Budget Filtering
              │
              ▼
          Final Answer
```

The agent uses a **ReAct-style loop**:

```text
Reason → Call Tool → Observe Result
       → Reason → Call Tool → Observe Result
       → Final Answer
```

---

## 🛠️ Tools

The agent has two main tools.

### 1. `search_flights()`

Searches live flight information using SerpApi / Google Flights.

```python
search_flights(
    from_city,
    to_city,
    departure_date,
    return_date=None,
    passengers=1,
    cabin_class="economy"
)
```

It returns information such as:

* Airline
* Departure time
* Arrival time
* Flight duration
* Number of stops
* Price

### 2. `compare_price()`

Takes the flight options returned by the search tool and sorts them from the cheapest to the most expensive.

```python
compare_price(options)
```

---

## 🧠 Memory

The agent contains a simple memory system that remembers useful information from previous conversations.

It can remember:

* User budget
* Previous route
* Travel preferences
* Previous flight search information

For example:

```text
User:
Find me a morning flight from Delhi to Mumbai under ₹7000.

Agent:
Searches flights and selects an option.

User:
What was the best option from my saved search?

Agent:
Uses the previous search information from memory.
```

---

## 🔄 Agent Workflow

The agent follows these steps:

1. Receive the user's goal.
2. Extract important information such as budget, route, date and preferences.
3. Check previously stored memory.
4. Decide which tool should be called.
5. Call `search_flights()`.
6. Observe the returned flight options.
7. Call `compare_price()`.
8. Filter the results according to the user's budget.
9. Consider the user's preferences.
10. Select the best available option.
11. Return the final answer.

---

## 🌐 Live Flight Data

This project uses **SerpApi** to retrieve live Google Flights information.

The system converts common city names into airport IATA codes.

For example:

```text
Delhi      → DEL
Mumbai     → BOM
Bengaluru  → BLR
Chennai    → MAA
Hyderabad  → HYD
Kolkata    → CCU
```

The project therefore works with real flight-search data instead of a fixed mock dataset.

---

## 🧠 LLM

The agent uses an LLM through **Groq's OpenAI-compatible API**.

The LLM is responsible for:

* Understanding the user's request
* Deciding which tool to use
* Providing tool arguments
* Interpreting tool results
* Deciding whether another tool call is required
* Producing the final response

The Python program controls the actual tool execution.

---

## 🔐 Environment Variables

API keys are stored in a `.env` file and should **never be committed to GitHub**.

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
SERPAPI_KEY=your_serpapi_api_key
```

Also create `.env.example` containing only placeholders:

```env
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_KEY=your_serpapi_api_key_here
```

Make sure `.env` is included in `.gitignore`.

---

## 📁 Project Structure

```text
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
├── .env.example
└── .gitignore
```

---

## ⚙️ Installation

Clone the repository and enter the project folder:

```bash
git clone <repository-url>
cd flight_option_finder
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the `.env` file and add the required API keys.

---

## ▶️ Running the Project

Run the main demo:

```bash
python demo.py
```

You can also test the flight-search tool directly:

```bash
python -c "from app.tools import search_flights; print(search_flights(from_city='Delhi', to_city='Mumbai', departure_date='2026-09-15', passengers=1, cabin_class='economy'))"
```

---

## 📓 Notebook Demonstration

The notebook:

```text
T10_Flight_Option_Finder_Clean_Live_Demo.ipynb
```

contains three demonstrations.

### Demo 1 – Flight Within Budget

Example:

```text
From: Delhi
To: Mumbai
Date: 15 September 2026
Budget: ₹7000
Preference: Morning
Passengers: 1
Cabin: Economy
```

The agent searches live flights, compares prices and selects a suitable option.

### Demo 2 – Memory

The same agent is used for a follow-up question.

```text
What is the best option from my saved search?
```

The agent uses information stored in memory from the previous interaction.

### Demo 3 – No Suitable Budget

Example:

```text
From: Delhi
To: Bengaluru
Date: 15 September 2026
Budget: ₹4000
```

If no available flight satisfies the budget, the agent reports that no suitable option was found instead of inventing a flight.

---

## 🛡️ Failure Handling

The project includes basic safeguards for unreliable or invalid results.

The agent:

* Validates required flight-search inputs
* Checks API configuration
* Uses a whitelist of allowed tools
* Handles tool execution errors
* Retries failed tool calls
* Prevents unknown tools from being executed
* Uses a maximum number of agent steps
* Does not invent flight prices or availability
* Reports when no flight fits the user's budget

---

## 🔒 Tool Whitelisting

Only registered tools can be executed by the agent.

```python
REGISTRY = {
    "search_flights": search_flights,
    "compare_price": compare_price
}
```

This prevents the LLM from directly executing arbitrary Python functions.

---

## 🧪 Testing

The project contains tests in:

```text
tests/test_project.py
```

Run them using:

```bash
pytest
```

---

## 📌 Requirements

| Component         | Purpose                         |
| ----------------- | ------------------------------- |
| Python            | Application development         |
| Groq              | LLM inference                   |
| SerpApi           | Live Google Flights data        |
| OpenAI Python SDK | LLM API interface               |
| python-dotenv     | Environment variable management |
| pytest            | Testing                         |
| Jupyter Notebook  | Agent demonstration             |

---

## 🎓 Agent Concepts Demonstrated

This project demonstrates the following Agentic AI concepts:

* Goal-based agent
* ReAct-style reasoning loop
* Tool calling
* Tool registry
* Function execution
* State and memory
* Multi-step decision making
* Budget-based decision making
* Error handling
* Retry mechanism
* Step limits
* Live API integration

---

## ✅ Expected Outcome

The final system demonstrates a functional Agentic AI workflow where the agent:

```text
Understand Goal
      ↓
Remember Context
      ↓
Search Live Flights
      ↓
Compare Prices
      ↓
Apply Budget & Preferences
      ↓
Select Best Option
      ↓
Return Answer
```

This satisfies the main requirements of the **T10 – Flight Option Finder Agent** assignment.

from app.tools import REGISTRY, TOOL_SCHEMA
from app.guards import call_tool
from app.design_review import audit_tools, audit_guards


def show_trace(result):
    for line in result["trace"]:
        print(line)
    print("FINAL:", result["answer"])
    print("STOP:", result["stopped_because"])


def offline_architecture_demo():
    """Offline demonstration of the exact Plan -> Act -> Observe -> Decide shape.

    This is intentionally deterministic so the notebook can be run without an API key.
    It is not pretending that a scripted response is an LLM; it is a teaching fallback.
    """
    print("\n=== OFFLINE PLAN-ACT DEMO ===")
    print("[plan] Goal: Delhi -> Mumbai, budget ₹6000, prefer morning")
    print("[act] search_flights('Delhi', 'Mumbai')")
    search = REGISTRY["search_flights"]("Delhi", "Mumbai")
    print("[observe]", search.replace("\n", " | "))
    print("[act] compare_price(options)")
    ranked = REGISTRY["compare_price"](search)
    print("[observe]", ranked.replace("\n", " | "))
    print("[decide] Keep options <= ₹6000 and prefer morning.")
    print("[decide] Selected 6E204, IndiGo, ₹4850, 08:10.")


if __name__ == "__main__":
    offline_architecture_demo()
    print("\n=== GUARDED TOOL DEMO ===")
    print(call_tool("search_flights", {"from_city":"Delhi","to_city":"Mumbai"}, REGISTRY))
    print(call_tool("delete_everything", {}, REGISTRY))

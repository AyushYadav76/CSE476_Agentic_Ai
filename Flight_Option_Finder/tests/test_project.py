from app.tools import REGISTRY, TOOL_SCHEMA, search_flights, compare_price
from app.guards import call_tool
from app.memory import AgentMemory
from app.design_review import audit_tools, audit_guards

def test_tools():
    s = search_flights("Delhi", "Mumbai")
    assert "6E204" in s
    ranked = compare_price(s)
    assert ranked.splitlines()[1].startswith("1. AI865") or ranked.splitlines()[1].startswith("1.  AI865")

def test_registry_schema():
    assert set(REGISTRY) == {x["function"]["name"] for x in TOOL_SCHEMA}
    assert not audit_tools(TOOL_SCHEMA, REGISTRY)

def test_guards():
    ok = call_tool("search_flights", {"from_city":"Delhi","to_city":"Mumbai"}, REGISTRY)
    assert ok.ok
    bad = call_tool("delete_everything", {}, REGISTRY)
    assert not bad.ok

def test_memory():
    m = AgentMemory()
    m.remember(budget=6000, preferences=["morning"], route=("Delhi","Mumbai"))
    assert m.pinned_facts["budget"] == 6000
    assert "morning" in m.pinned_facts["preferences"]
    assert m.pinned_facts["route"] == ("Delhi","Mumbai")

def test_guards_audit():
    assert not audit_guards(6, True, 2, True, True)

"""Conversation and structured memory for the T10 agent."""

class AgentMemory:
    def __init__(self):
        self.messages = []
        self.pinned_facts = {
            "budget": None,
            "preferences": [],
            "route": None,
            "departure_date": None,
        }
        self.last_answer = None

    @property
    def data(self):
        return {
            "messages": self.messages,
            "pinned_facts": self.pinned_facts,
        }

    def add_message(self, message):
        self.messages.append(message)

    def remember(
        self,
        budget=None,
        preferences=None,
        route=None,
        departure_date=None,
        last_answer=None,
    ):
        if budget is not None:
            self.pinned_facts["budget"] = budget
        if preferences:
            for item in preferences:
                if item not in self.pinned_facts["preferences"]:
                    self.pinned_facts["preferences"].append(item)
        if route is not None:
            self.pinned_facts["route"] = route
        if departure_date is not None:
            self.pinned_facts["departure_date"] = departure_date
        if last_answer is not None:
            self.last_answer = last_answer

    def context_summary(self):
        return (
            f"Budget={self.pinned_facts['budget']}; "
            f"Preferences={self.pinned_facts['preferences']}; "
            f"Route={self.pinned_facts['route']}; "
            f"Departure date={self.pinned_facts['departure_date']}"
        )

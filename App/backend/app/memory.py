class ConversationMemory:
    def __init__(self, max_turns=5):
        self.max_turns = max_turns
        self.history = []

    def add_exchange(self, question: str, answer: str):
        self.history.append((question, answer))
        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def get_history_text(self) -> str:
        if not self.history:
            return "None"
        return "\n".join(
            [f"User: {q}\nBot: {a}" for q, a in self.history]
        )

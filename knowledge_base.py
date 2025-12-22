class Rule:
    def __init__(self, conditions: list[str], conclusion: str):
        self._conditions = conditions
        self._conclusion = conclusion


class KnowledgeBase:
    def __init__(self):
        self._rules = []  # all rules
        self._facts = set()  # current known facts

    def add_rule(self, rule) -> None:
        """Appends a rule to the knowledge base"""        
        self._rules.append(rule)

    def add_fact(self, fact) -> None:
        """Adds a fact to the knowledge base"""        
        self._facts.add(fact)

class Rule:
    def __init__(self, conditions: list[str], conclusion: str):
        self._conditions = conditions
        self._conclusion = conclusion


class KnowledgeBase:
    def __init__(self):
        self._rules = []                # all rules
        self._true_facts = set()        # set of strings of all sets that are true after questioning or inference
        self._false_facts = set()       # set of strings of all sets that are false after questioning, helping with question selection
        self._facts = self._true_facts  # points to the true facts such that inference engine still works

    def add_rule(self, rule) -> None:
        """Appends a rule to the knowledge base"""        
        self._rules.append(rule)

    def add_fact(self, fact: str) -> None:
        self.set_fact_true(fact)

    def set_fact_true(self, fact) -> None:
        """Adds a fact to the knowledge base"""        
        self._true_facts.add(fact)
        self._false_facts.discard(fact)

    def set_fact_false(self, fact) -> None:
        """Adds a fact to the knowledge base"""        
        self._true_facts.discard(fact)
        self._false_facts.add(fact)

    def set_fact_unknown(self, fact) -> None:
        """Adds a fact to the knowledge base"""        
        self._true_facts.discard(fact)
        self._false_facts.discard(fact)

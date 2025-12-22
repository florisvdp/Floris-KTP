import json
import os
from knowledge_base import KnowledgeBase, Rule

class ForwardEngine:
    def __init__(self, kb: KnowledgeBase):
        self._kb = kb

    def run(self) -> set:
        changed = True
        while changed:
            changed = False
            for rule in self._kb._rules:
                if rule._conclusion not in self._kb._facts:
                    if all(cond in self._kb._facts for cond in rule._conditions):
                        self._kb.add_fact(rule._conclusion)
                        changed = True
        return self._kb._facts


class BackwardEngine:
    def __init__(self, kb: KnowledgeBase):
        self._kb = kb

    def solve(self, goal: str, visited=None) -> bool:
        if visited is None:
            visited = set()

        if goal in self._kb._facts:
            return True

        if goal in visited:
            return False

        visited.add(goal)

        for rule in self._kb._rules:
            if rule._conclusion == goal:
                if all(self.solve(cond, visited) for cond in rule._conditions):
                    self._kb.add_fact(goal)
                    return True
        return False


def load_rules_from_json(kb: KnowledgeBase, filename: str) -> None:
    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, filename)

    with open(full_path, "r") as f:
        data = json.load(f)

    for entry in data:
        kb.add_rule(Rule(entry["conditions"], entry["conclusion"]))

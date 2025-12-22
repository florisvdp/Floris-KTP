from __future__ import annotations

from knowledge_base import KnowledgeBase
from inference_engine import ForwardEngine, BackwardEngine, load_rules_from_json

kb = KnowledgeBase()

load_rules_from_json(kb, "orthopedic_rules.json")

kb.add_fact("xray_grade_4")
kb.add_fact("pain_vas_high")
kb.add_fact("BMI_over_35")
kb.add_fact("lifestyle_failed")
kb.add_fact("pain_medication_failed")
kb.add_fact("injections_failed")

fwd = ForwardEngine(kb)
derived = fwd.run()

print("Facts after forward chaining:")
for fact in sorted(derived):
    print("-", fact)

bwd = BackwardEngine(kb)

print("\nBackward chaining queries:")
print("Surgery indicated?        ", bwd.solve("surgery_indicated"))
print("Proceed with surgery?     ", bwd.solve("proceed_with_surgery"))
print("Delay or avoid surgery?   ", bwd.solve("delay_or_avoid_surgery"))

print("Number of rules loaded:", len(kb._rules))

import tkinter as tk
from tkinter import ttk, messagebox

from knowledge_base import KnowledgeBase
from inference_engine import ForwardEngine, BackwardEngine, load_rules_from_json

import os
print("Loaded gui.py from:", __file__)
print("CWD:", os.getcwd())


""" 
We may want to change to backward engine as this 
"""

# These strings MUST match your orthopedic_rules.json facts exactly
# All yes and no questions are tuples for easier use

RULES_PATH = "orthopedic_rules_2.json"

KL = ["kl_grade_1", "kl_grade_2", "kl_grade_3", "kl_grade_4"]

PAIN_SIGNIFICANT = (
    "has_significant_pain",
    "no_significant_pain",
)


BMI = ["BMI_below_18", "BMI_18_24", "BMI_25_30", "BMI_30_35", "BMI_over_35"]

AGE_75 = (
    "age_over_75",
    "age_under_75",
)

LIFESTYLE_STATUS = [
    "has_done_lifestyle_improvement",
    "not_done_lifestyle_improvement",
    "unknown_done_lifestyle_improvement",
]


ROOM_IMPROVE_MUSCLE = (
    "room_for_improvement_muscle_strength",
    "no_room_for_improvement_muscle_strength",
)

ROOM_IMPROVE_CONDITIONAL = (
    "room_for_improvement_conditional",
    "no_room_for_improvement_conditional",
)

ROOM_IMPROVE_WEIGHT = (
    "room_for_improvement_lose_weight",
    "no_room_for_improvement_lose_weight",
)


PAINKILLERS_STATUS = [
    "has_used_all_painkillers",
    "not_used_all_painkillers",
    "unknown_used_all_painkillers",
]

PAINKILLER_PARACETAMOL = (
    "used_paracetamol",
    "not_used_paracetamol",
)

PAINKILLER_NSAID = (
    "used_NSAID",
    "not_used_NSAID",
)

PAINKILLER_TRAMADOL = (
    "used_tramadol",
    "not_used_tramadol",
)


INJECTIONS_STATUS = [
    "has_used_all_injections",
    "not_used_all_injections",
    "unknown_used_all_injections",
]

INJECTION_CORTICOSTEROID = (
    "used_corticosteroid",
    "not_used_corticosteroid",
)

INJECTION_HYALURONIC = (
    "used_hyaluronic_acid",
    "not_used_hyaluronic_acid",
)


RISK_STATUS = ["no_high_risk", "high_risk_unknown", "high_risk"]

RISK_HEART = ("heart_disease_risk", "no_heart_disease_risk")
RISK_LUNG = ("lung_disease_risk", "no_lung_disease_risk")
RISK_BLOOD_THINNERS = ("blood_thinners_risk", "no_blood_thinners_risk")
RISK_DIABETES = ("uncontrolled_diabetes_risk", "no_uncontrolled_diabetes_risk")
RISK_KIDNEY = ("kidney_desease_risk", "no_kidney_disease_risk")
RISK_CLOTS = ("blood_clots_history_risk", "no_blood_clots_history_risk")
RISK_INFECTION = (
    "active_infection_or_immune_supression_risk",
    "no_active_infection_or_immune_suppression_risk",
)

WILLING_RISK = (
    "willing_to_take_risk",
    "not_willing_to_take_risk",
)

SMOKING = (
    "willing_to_stop_smoking",
    "not_willing_to_stop_smoking",
)


COMPLICATIONS_EXPLAINED = (
    "complications_explained",
    "complications_not_explained",
)


HEART_LUNG_LIFESTYLE = (
    "no_heart_lungs_problems",
    "heart_lungs_problems",
)

YESNO_QUESTIONS = [
    ("Significant pain", "Does the pain make you irritable, and does the limitation caused by your worn-out knee significantly reduce your quality of life?", PAIN_SIGNIFICANT),
    ("Age", "Are you older than 75?", AGE_75),

    ("Heart or Lung problems", "Do you have heart or lungs problems that prevent you from exercising", HEART_LUNG_LIFESTYLE),

    ("Muscle strength", "Is there room for improvement in muscle strength?", ROOM_IMPROVE_MUSCLE),
    ("Conditioning", "Is there room for improvement in conditioning?", ROOM_IMPROVE_CONDITIONAL),
    ("Weight loss", "Is there room for improvement in weight loss?", ROOM_IMPROVE_WEIGHT),

    ("Paracetamol", "Has paracetamol been used? (3 times a day)", PAINKILLER_PARACETAMOL),
    ("NSAID", "Has NSAID been tried? (e.g. ibuprofen, diclofenac or naproxen)", PAINKILLER_NSAID),
    ("Tramadol", "Has tramadol been tried?", PAINKILLER_TRAMADOL),

    ("Corticosteroid", "Was a corticosteroid injection tried?", INJECTION_CORTICOSTEROID),
    ("Hyaluronic acid", "Was a hyaluronic acid injection tried?", INJECTION_HYALURONIC),

    # Risk factors
    ("Heart disease risk", "Do you have heart failure, angina, a previous heart attack, or a heart valve problem?", RISK_HEART),
    ("Lung disease risk", "Do you have COPD, severe asthma, or sleep apnea that is untreated?", RISK_LUNG),
    ("Blood thinners risk", "Do you take blood thinners or have a bleeding/clotting disorder?", RISK_BLOOD_THINNERS),
    ("Uncontrolled diabetes risk", "Do you have diabetes that is poorly controlled?", RISK_DIABETES),
    ("Kidney disease risk", "Do you have moderate/severe kidney disease or are you on dialysis?", RISK_KIDNEY),
    ("Blood clots history", "Have you ever had a blood clot in your leg or lungs?", RISK_CLOTS),
    ("Infection / immune suppression", "Active infection or immune suppression?", RISK_INFECTION),

    ("Risk willingness", "You have a high risk of complication during surgery: are you willing to accept the risk?", WILLING_RISK),
    ("Smoking", "Are you willing to stop smoking 4 before and 2 weeks after surgery?", SMOKING),
    ("Complications", "Were the possible complications explained that come with every surgery?", COMPLICATIONS_EXPLAINED),
]


class WizardGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Orthopedic Expert System")
        self.geometry("860x520")

        self.kb = KnowledgeBase()
        load_rules_from_json(self.kb, RULES_PATH)

        # history snapshots: (true_facts, false_facts)
        self.history: list[tuple[set[str], set[str]]] = []

        # Keeps track of which past was previously by using a stack
        self.nav_stack: list[int] = []

        # UI layout
        self.container = ttk.Frame(self, padding=14)
        self.container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(self.container)
        header.pack(fill=tk.X)

        self.step_label = ttk.Label(header, text="", font=("TkDefaultFont", 12, "bold"))
        self.step_label.pack(side=tk.LEFT)

        self.progress_label = ttk.Label(header, text="")
        self.progress_label.pack(side=tk.RIGHT)

        ttk.Separator(self.container).pack(fill=tk.X, pady=10)

        self.body = ttk.Frame(self.container)
        self.body.pack(fill=tk.BOTH, expand=True)

        ttk.Separator(self.container).pack(fill=tk.X, pady=10)

        nav = ttk.Frame(self.container)
        nav.pack(fill=tk.X)

        self.back_btn = ttk.Button(nav, text="◀ Back", command=self.on_back)
        self.back_btn.pack(side=tk.LEFT)

        self.next_btn = ttk.Button(nav, text="Next ▶", command=self.on_next)
        self.next_btn.pack(side=tk.RIGHT)

        # Define wizard pages (one question per page)
        self.pages = [
            self.page_choice("KL Grade", "Select KL grade:", KL, default="kl_grade_3"),
            self.page_choice("BMI", "Select your BMI range:", BMI, default="BMI_25_30"),
            self.page_choice("Lifestyle status", "Have you done all lifestyle improvements?",
                            LIFESTYLE_STATUS, default="unknown_done_lifestyle_improvement"),
            self.page_choice("Painkillers status", "Did you use/try all painkillers?",
                            PAINKILLERS_STATUS, default="unknown_used_all_painkillers"),
            self.page_choice("Injections status", "Did you use/try injections?",
                            INJECTIONS_STATUS, default="unknown_used_all_injections"),
            self.page_choice("High risk status", "Do you know if you have increased risk for surgeries? (Select unknown for questionnaire)",
                            RISK_STATUS, default="high_risk_unknown"),
        ]

        # append all yes/no questions
        for title, prompt, fact_pair in YESNO_QUESTIONS:
            self.pages.append(self.page_yesno(title, prompt, fact_pair))

        # final page
        self.pages.append(self.page_review_and_run())

        self.page_index = 0
        self.goal = "advice_given"   # used by goto_best_next_page/_goal_is_provable
        
        self.render_page()

    # --------- Selecting new page ----------

    def _goal_is_provable(self) -> bool:
        # BackwardEngine only sees TRUE facts via kb._facts (alias), which is correct.
        return BackwardEngine(self.kb).solve(self.goal)

    def _next_needed_fact(self, goal: str) -> str | None:
        true_facts = self.kb._true_facts
        false_facts = self.kb._false_facts
        rules = self.kb._rules

        derivable = {r._conclusion for r in rules}
        visiting: set[str] = set()

        def dfs(goal: str) -> str | None:
            if goal in true_facts:
                return None

            if goal in visiting: # ensures no cyclic behaviour, please note that the goal changes recursively
                return None
            visiting.add(goal)

            # primitive fact: no rule can derive it 
            if goal not in derivable:
                return goal

            # rules that can derive the gpa;, skipping any rule blocked by false conditions
            candidates = []
            for rule in rules:
                if rule._conclusion != goal:
                    continue
                if any(condition in false_facts for condition in rule._conditions):
                    continue
                missing = sum(1 for condition in rule._conditions if condition not in true_facts)
                candidates.append((missing, rule))
            candidates.sort(key=lambda x: x[0])  # prefer easiest rule first

            for _, r in candidates:
                # ask for missing conditions in that rule
                for c in r._conditions:
                    if c in true_facts:
                        continue
                    if c in false_facts:
                        break
                    nxt = dfs(c)
                    if nxt:
                        return nxt

            return None # found no conditions that can be asked or only false conditions

        return dfs(goal)

    def _find_page_for_fact(self, fact: str) -> int | None:
        for i, page in enumerate(self.pages):
            if fact in page.get("facts", set()):
                return i
        return None

    def goto_best_next_page(self):
        print("\n=== goto_best_next_page ===")
        print("Current page_index:", self.page_index)
        print("Current true facts:", sorted(self.kb._true_facts))
        print("Current false facts:", sorted(self.kb._false_facts))

        # If goal already provable, jump to review/run page
        provable = self._goal_is_provable()
        print("Goal provable?", provable)

        if provable:
            print("→ Jumping to REVIEW because goal is provable")
            self.page_index = len(self.pages) - 1
            self.render_page()
            return

        needed = self._next_needed_fact(self.goal)
        print("Next needed fact:", needed)

        if needed is None:
            print("→ Jumping to REVIEW because _next_needed_fact returned None")
            self.page_index = len(self.pages) - 1
            self.render_page()
            return

        idx = self._find_page_for_fact(needed)
        print(f"Page index for fact '{needed}':", idx)

        if idx is None:
            print("→ Jumping to REVIEW because no page provides this fact")
            self.page_index = len(self.pages) - 1
            self.render_page()
            return

        print(f"→ Navigating to page {idx} for fact '{needed}'")
        self.nav_stack.append(self.page_index)
        self.page_index = idx
        self.render_page()


    # ---------- Page builders ----------

    def clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def page_choice(self, title, prompt, options, default=None, post_process=None):
        """Single-choice (radio) question page."""
        def render():
            self.clear_body()
            ttk.Label(self.body, text=prompt, font=("TkDefaultFont", 11)).pack(anchor="w", pady=(0, 10))

            var = tk.StringVar(value=default or options[0])

            card = ttk.Frame(self.body)
            card.pack(anchor="w", fill=tk.X)

            for opt in options:
                ttk.Radiobutton(card, text=opt, value=opt, variable=var).pack(anchor="w", pady=2)

            def apply():
                chosen = var.get()

                # unknown does not set the others to true or false since that may change in the future
                if chosen.startswith("unknown_"):
                    self.kb.set_fact_true(chosen)
                    return True


                for opt in options:
                    if opt == chosen:
                        self.kb.set_fact_true(opt)
                    else:
                        self.kb.set_fact_false(opt)

                if post_process:
                    for implied in post_process(chosen):
                        self.kb.set_fact_true(implied)

                return True
                

            return apply

        return {"title": title, "render": render, "facts": set(options)}


    def page_yesno(self, title, prompt, fact_pair):
        yes_fact, no_fact = fact_pair

        def render():
            self.clear_body()
            ttk.Label(self.body, text=prompt, font=("TkDefaultFont", 11)).pack(anchor="w", pady=(0, 10))

            var = tk.StringVar(value="no")

            card = ttk.Frame(self.body)
            card.pack(anchor="w", fill=tk.X)

            ttk.Radiobutton(card, text="Yes", value="yes", variable=var).pack(anchor="w", pady=2)
            ttk.Radiobutton(card, text="No", value="no", variable=var).pack(anchor="w", pady=2)

            def apply():
                if var.get() == "yes":
                    self.kb.set_fact_true(yes_fact)
                    self.kb.set_fact_false(no_fact)
                else:
                    self.kb.set_fact_true(no_fact)
                    self.kb.set_fact_false(yes_fact)
                return True

            return apply

        return {"title": title, "render": render, "facts": set(fact_pair)}


    def page_review_and_run(self):
        """Final page: show selected facts and run forward chaining."""
        def render():
            self.clear_body()

            ttk.Label(self.body, text="Review & Run", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
            ttk.Label(self.body, text="Selected facts:", foreground="#555").pack(anchor="w", pady=(6, 4))

            facts_box = tk.Text(self.body, height=10, wrap="none")
            facts_box.pack(fill=tk.X)
            facts_box.insert(tk.END, "\n".join(sorted(self.kb._true_facts)))
            facts_box.configure(state="disabled")

            ttk.Label(self.body, text="Results (forward chaining):", foreground="#555").pack(anchor="w", pady=(10, 4))
            results_box = tk.Text(self.body, height=10, wrap="word")
            results_box.pack(fill=tk.BOTH, expand=True)

            def apply():
                # Run forward chaining and display results
                kb = KnowledgeBase()
                load_rules_from_json(kb, RULES_PATH)
                print("Rules loaded:", len(kb._rules))
                for f in self.kb._true_facts:
                    kb.add_fact(f)

                # we still run forward chaining so you can show derived facts, as well as further advice that may be given
                derived = ForwardEngine(kb).run()

                #  backward chaining goal check
                bwd = BackwardEngine(kb)
                goal = "advice_given"
                goal_reached = bwd.solve(goal)

                results_box.configure(state="normal")
                results_box.delete("1.0", tk.END)

                results_box.insert(tk.END, f"Backward chaining goal: {goal}\n")
                results_box.insert(tk.END, f"Goal provable? {'YES' if goal_reached else 'NO'}\n\n")

                # Keep your existing headline + derived facts display
                results_box.insert(tk.END, "Headline conclusions (forward chaining):\n")

                #conclusions you probably care about
                headline = [
                    "advice_surgery",
                    "advice_too_risky",
                    "advice_weight_loss",
                    "advice_lifestyle",
                    "advice_pain_killers",
                    "advice_injection",
                    "reason_no_surgery_low_radiographic_severity",
                    "reason_pain_treatment_explanation",
                    "risk_worth_surgery",
                ]
                found_headlines = [h for h in headline if h in derived]

                results_box.configure(state="normal")

                results_box.insert(tk.END, "Headline conclusions:\n")
                if found_headlines:
                    for h in found_headlines:
                        results_box.insert(tk.END, f"• {h}\n")
                else:
                    results_box.insert(tk.END, "• (none of the headline conclusions were derived)\n")

                results_box.insert(tk.END, "\nAll derived facts:\n")
                for f in sorted(derived):
                    results_box.insert(tk.END, f"• {f}\n")
                results_box.configure(state="disabled")

                # Change Next button into Finish
                self.next_btn.configure(text="Finish", command=self.destroy)
                return True

            return apply

        return {"title": "Run", "render": render}

    # ---------- Navigation ----------

    def render_page(self):
        page = self.pages[self.page_index]
        self.step_label.configure(text=page["title"])
        self.progress_label.configure(text=f"Step {self.page_index + 1} / {len(self.pages)}")

        self.apply_fn = page["render"]()

        self.back_btn.configure(state=("disabled" if self.page_index == 0 else "normal"))

        # Reset Next button if we came back from results
        self.next_btn.configure(text="Next ▶", command=self.on_next)

        # On final page, label Next as "Run"
        if self.page_index == len(self.pages) - 1:
            self.next_btn.configure(text="Run ▶")

    def on_next(self):
        if not self.apply_fn():
            return

        # Save snapshot
        snap = (set(self.kb._true_facts), set(self.kb._false_facts))
        if len(self.history) <= self.page_index:
            self.history.append(snap)
        else:
            self.history[self.page_index] = snap

        if self.page_index < len(self.pages) - 1:
            self.goto_best_next_page()
        else:
            # last page should handle its own "Finish"
            pass

    def on_back(self):
        if not self.nav_stack:
            return

        self.page_index = self.nav_stack.pop()

        # Restore facts from snapshot of previous page (if present)
        if self.page_index < len(self.history):
            true_snap, false_snap = self.history[self.page_index]
            self.kb._true_facts = set(true_snap)
            self.kb._false_facts = set(false_snap)
            self.kb._facts = self.kb._true_facts 

        self.render_page()


if __name__ == "__main__":
    app = WizardGUI()
    app.mainloop()

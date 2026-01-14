import tkinter as tk
from tkinter import ttk, messagebox

from knowledge_base import KnowledgeBase
from inference_engine import ForwardEngine, load_rules_from_json

import os
print("Loaded gui.py from:", __file__)
print("CWD:", os.getcwd())


""" 
We may want to change to backward engine as this 
"""

RULES_PATH = "orthopedic_rules_2.json"

# These strings MUST match your orthopedic_rules.json facts exactly
RULES_PATH = "orthopedic_rules_2.json"

KL = ["kl_grade_1", "kl_grade_2", "kl_grade_3", "kl_grade_4"]

PAIN_SIG = ["has_significant_pain", "no_significant_pain"]

BMI = ["BMI_below_18", "BMI_18_24", "BMI_25_30", "BMI_30_35", "BMI_over_35"]

AGE75 = ["age_under_75", "age_over_75"]

LIFESTYLE_STATUS = [
    "has_done_lifestyle_improvement",
    "not_done_lifestyle_improvement",
    "unknown_done_lifestyle_improvement",
]

ROOM_IMPROVE = [
    "room_for_improvement_muscle_strength",
    "room_for_improvement_conditional",
    "room_for_improvement_lose_weight",
    "no_room_for_improvement_muscle_strength",
    "no_room_for_improvement_conditional",
    "no_room_for_improvement_lose_weight",
]

PAINKILLERS_STATUS = [
    "has_used_all_painkillers",
    "not_used_all_painkillers",
    "unknown_used_all_painkillers",
]

PAINKILLERS_DETAILS = [
    "used_paracetamol", "not_used_paracetamol",
    "used_NSAID", "not_used_NSAID",
    "used_tramadol", "not_used_tramadol",
]

INJECTIONS_STATUS = [
    "has_used_all_injections",
    "not_used_all_injections",
    "unknown_used_all_injections",
]

INJECTIONS_DETAILS = [
    "used_corticosteroid", "not_used_corticosteroid",
    "used_hyaluronic_acid", "not_used_hyaluronic_acid",
]

RISK_STATUS = ["no_high_risk", "high_risk_unknown"]
RISK_FACTORS = [
    "heart_disease_risk",
    "lung_disease_risk",
    "blood_thinners_risk",
    "uncontrolled_diabetes_risk",
    "kidney_desease_risk",  # (or kidney_disease_risk if you fix JSON)
    "blood_clots_history_risk",
    "active_infection_or_immune_supression_risk",  # (or suppression)
]

WILLING_RISK = ["willing_to_take_risk", "not_willing_to_take_risk"]
SMOKING = ["willing_to_stop_smoking", "not_willing_to_stop_smoking"]

OTHER = ["complications_explained", "no_heart_lungs_problems"]



def pain_implied_facts(pain_fact: str) -> set[str]:
    """Your rules include pain_vas_7_10 in one place; we infer it when pain is 7-8 or 9-10."""
    implied = set()
    if pain_fact in ("pain_vas_7_8", "pain_vas_9_10"):
        implied.add("pain_vas_7_10")
    return implied


class WizardGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Orthopedic Expert System(Forward Chaining)")
        self.geometry("860x520")

        self.facts: set[str] = set()
        self.page_index = 0
        self.history: list[set[str]] = []  # snapshot of facts after each page

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
            self.page_choice("KL Grade", "Select KL (Kellgren–Lawrence) grade:", KL, default="kl_grade_3"),
            self.page_choice("Significant pain", "Is there significant pain?", PAIN_SIG, default="has_significant_pain"),
            self.page_choice("BMI", "Select BMI range:", BMI, default="BMI_25_30"),

            # Lifestyle status
            self.page_choice("Lifestyle status", "Lifestyle improvements done?", LIFESTYLE_STATUS, default="unknown_done_lifestyle_improvement"),
            # If unknown, your rules depend on the *no_room_for_improvement_* facts:
            self.page_multi("Lifestyle room for improvement", "If unknown: mark room/no-room for improvement:", ROOM_IMPROVE),

            # Painkillers status + detail evidence
            self.page_choice("Painkillers status", "Used all painkillers?", PAINKILLERS_STATUS, default="unknown_used_all_painkillers"),
            self.page_choice("Age", "Age group relevant for tramadol:", AGE75, default="age_under_75"),
            self.page_multi("Painkillers detail", "Select applicable painkiller details:", PAINKILLERS_DETAILS),

            # Injections status + detail evidence
            self.page_choice("Injections status", "Used all injections?", INJECTIONS_STATUS, default="unknown_used_all_injections"),
            self.page_multi("Injections detail", "Select applicable injection details:", INJECTIONS_DETAILS),

            # Risk pathway
            self.page_choice("High risk status", "Is high risk known?", RISK_STATUS, default="high_risk_unknown"),
            self.page_multi("Risk factors", "If unknown: select present risk factors:", RISK_FACTORS),
            self.page_choice("Risk willingness", "If high risk: willing to take risk?", WILLING_RISK, default="not_willing_to_take_risk"),

            # Smoking + complications
            self.page_choice("Smoking", "Willing to stop smoking?", SMOKING, default="willing_to_stop_smoking"),
            self.page_yesno("Complications explained", "Were complications explained?", yes_fact="complications_explained", no_fact="complications_not_explained"),

            self.page_review_and_run(),
        ]


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
                # Remove any previous choice from this option-set before adding new
                self.facts.difference_update(options)
                self.facts.add(var.get())
                if post_process:
                    self.facts.update(post_process(var.get()))
                return True

            return apply

        return {"title": title, "render": render}

    def page_yesno(self, title, prompt, yes_fact, no_fact):
        """Yes/No question page with one one fact"""
        def render():
            self.clear_body()
            ttk.Label(self.body, text=prompt, font=("TkDefaultFont", 11)).pack(anchor="w", pady=(0, 10))

            var = tk.StringVar(value="no")

            card = ttk.Frame(self.body)
            card.pack(anchor="w", fill=tk.X)

            ttk.Radiobutton(card, text="Yes", value="yes", variable=var).pack(anchor="w", pady=2)
            ttk.Radiobutton(card, text="No", value="no", variable=var).pack(anchor="w", pady=2)

            def apply():
                self.facts.discard(yes_fact)
                self.facts.discard(no_fact)
                self.facts.add(yes_fact if var.get() == "yes" else no_fact)
                return True

            return apply

        return {"title": title, "render": render}

    def page_multi(self, title, prompt, options):
        """Multi-select page (checkboxes), many facts (optional) """
        def render():
            self.clear_body()
            ttk.Label(self.body, text=prompt, font=("TkDefaultFont", 11)).pack(anchor="w", pady=(0, 10))

            vars_map = {opt: tk.BooleanVar(value=(opt in self.facts)) for opt in options}

            card = ttk.Frame(self.body)
            card.pack(anchor="w", fill=tk.X)

            for opt in options:
                ttk.Checkbutton(card, text=opt, variable=vars_map[opt]).pack(anchor="w", pady=2)

            def apply():
                # Replace comorbidity set with current selections
                self.facts.difference_update(options)
                for opt, v in vars_map.items():
                    if v.get():
                        self.facts.add(opt)
                return True

            return apply

        return {"title": title, "render": render}

    def page_review_and_run(self):
        """Final page: show selected facts and run forward chaining."""
        def render():
            self.clear_body()

            ttk.Label(self.body, text="Review & Run", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
            ttk.Label(self.body, text="Selected facts:", foreground="#555").pack(anchor="w", pady=(6, 4))

            facts_box = tk.Text(self.body, height=10, wrap="none")
            facts_box.pack(fill=tk.X)
            facts_box.insert(tk.END, "\n".join(sorted(self.facts)))
            facts_box.configure(state="disabled")

            ttk.Label(self.body, text="Results (forward chaining):", foreground="#555").pack(anchor="w", pady=(10, 4))
            results_box = tk.Text(self.body, height=10, wrap="word")
            results_box.pack(fill=tk.BOTH, expand=True)

            def apply():
                # Run forward chaining and display results
                kb = KnowledgeBase()
                load_rules_from_json(kb, RULES_PATH)
                load_rules_from_json(kb, RULES_PATH)
                print("Rules loaded:", len(kb._rules))
                for f in self.facts:
                    kb.add_fact(f)

                derived = ForwardEngine(kb).run()

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
                results_box.delete("1.0", tk.END)
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
        if len(self.history) <= self.page_index:
            self.history.append(set(self.facts))
        else:
            self.history[self.page_index] = set(self.facts)

        if self.page_index < len(self.pages) - 1:
            self.page_index += 1
            self.render_page()
        else:
            # last page should handle its own "Finish"
            pass

    def on_back(self):
        if self.page_index == 0:
            return
        self.page_index -= 1

        # Restore facts from snapshot of previous page (if present)
        if self.page_index < len(self.history):
            self.facts = set(self.history[self.page_index])

        self.render_page()


if __name__ == "__main__":
    app = WizardGUI()
    app.mainloop()

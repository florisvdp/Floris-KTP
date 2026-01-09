import tkinter as tk
from tkinter import ttk, messagebox

from knowledge_base import KnowledgeBase
from inference_engine import ForwardEngine, load_rules_from_json

""" 
We may want to change to backward engine as this 
"""

RULES_PATH = "orthopedic_rules.json"

# These strings MUST match your orthopedic_rules.json facts exactly
XRAY = ["xray_grade_1", "xray_grade_2", "xray_grade_3", "xray_grade_4"]
PAIN = ["pain_vas_0_2", "pain_vas_3_4", "pain_vas_5_6", "pain_vas_7_8", "pain_vas_9_10"]
BMI = ["BMI_18_24", "BMI_25_30", "BMI_30_35", "BMI_over_35"]
AGE = ["age_young_adult", "age_adult", "age_middle_age", "age_elderly", "age_very_elderly"]
PROM = [
    "PROM_very_low_function",
    "PROM_low_function",
    "PROM_medium_function",
    "PROM_high_function",
    "PROM_very_high_function",
]
PREF = [
    "patient_prefers_surgery",
    "patient_prefers_non_surgical",
    "patient_unsure",
    "patient_prefers_minimal_intervention",
]
COMORB = ["hypertension", "diabetes", "osteoporosis", "heart_disease"]


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
            self.page_choice("X-ray grade", "Select X-ray grade:", XRAY, default=XRAY[-1]),
            self.page_choice("Pain VAS", "Select pain VAS range:", PAIN, default=PAIN[-1], post_process=pain_implied_facts),
            self.page_choice("BMI", "Select BMI range:", BMI, default=BMI[-1]),
            self.page_choice("Age", "Select age category:", AGE, default=AGE[2]),
            self.page_choice("PROM", "Select PROM functional level:", PROM, default=PROM[1]),
            self.page_choice("Preference", "What is the patient preference?", PREF, default=PREF[2]),
            self.page_yesno("Exercise", "Does the patient exercise regularly?", yes_fact="exercise_regularly", no_fact="exercise_not_regularly"),
            self.page_yesno("Pain medication", "Was pain medication successful?", yes_fact="pain_medication_success", no_fact="pain_medication_not_effective"),
            self.page_yesno("Physiotherapy", "Was physiotherapy successful?", yes_fact="physiotherapy_success", no_fact="physiotherapy_not_effective"),
            self.page_yesno("Injections", "Were injections successful?", yes_fact="injections_success", no_fact="injections_not_effective"),
            self.page_multi("Comorbidities", "Select any comorbidities present (optional):", COMORB),
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
                for f in self.facts:
                    kb.add_fact(f)

                derived = ForwardEngine(kb).run()

                #conclusions you probably care about
                headline = [
                    "surgery_indicated",
                    "proceed_with_surgery",
                    "proceed_with_caution",
                    "delay_or_avoid_surgery",
                    "shared_decision_needed",
                    "urgent_surgery_consideration",
                    "consider_surgery",
                    "consider_risk_vs_benefit",
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

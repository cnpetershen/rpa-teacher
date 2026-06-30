import json
import tkinter as tk


class ReviewUI:

    def __init__(self, steps_file="skill.json"):
        self.steps_file = steps_file
        self.load_steps()

        self.root = tk.Tk()
        self.root.title("Hermes RPA - Step Review Editor")
        self.root.geometry("1050x600")

        self.selected_index = None

        self.build_ui()
        self.refresh_list()
        self.refresh_intent_bar()
        self.refresh_corrections()

        self.root.mainloop()

    # -------------------------
    # load skill
    # -------------------------
    def load_steps(self):
        try:
            with open(
                self.steps_file, "r", encoding="utf-8"
            ) as f:
                data = json.load(f)
                self.steps = data.get("steps", [])
                self.intent = data.get("intent", {})
                self.corrections = data.get(
                    "corrections", []
                )
        except Exception:
            self.steps = []
            self.intent = {}
            self.corrections = []

    # -------------------------
    # build UI
    # -------------------------
    def build_ui(self):

        # top frame: intent info
        intent_frame = tk.Frame(
            self.root, relief=tk.RIDGE, bd=2
        )
        intent_frame.pack(
            side=tk.TOP, fill=tk.X, padx=5, pady=5
        )

        tk.Label(
            intent_frame,
            text="Recognized Intent:",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=5)
        self.intent_var = tk.StringVar()
        self.intent_entry = tk.Entry(
            intent_frame,
            textvariable=self.intent_var,
            width=20
        )
        self.intent_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(
            intent_frame,
            text="Update Intent",
            command=self.update_intent
        ).pack(side=tk.LEFT, padx=5)

        self.phases_var = tk.StringVar()
        tk.Label(
            intent_frame, text="Phases:"
        ).pack(side=tk.LEFT, padx=(15, 2))
        tk.Label(
            intent_frame,
            textvariable=self.phases_var
        ).pack(side=tk.LEFT)

        # main content area
        main_area = tk.Frame(self.root)
        main_area.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True
        )

        # left side list
        self.listbox = tk.Listbox(main_area, width=55)
        self.listbox.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False
        )
        self.listbox.bind(
            "<<ListboxSelect>>", self.on_select
        )

        # right side editor
        right = tk.Frame(main_area)
        right.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True
        )

        # action
        tk.Label(right, text="Action").pack()
        self.action_var = tk.StringVar()
        self.action_entry = tk.Entry(
            right, textvariable=self.action_var
        )
        self.action_entry.pack(fill=tk.X)

        # value
        tk.Label(right, text="Value / Params").pack()
        self.value_var = tk.StringVar()
        self.value_entry = tk.Entry(
            right, textvariable=self.value_var
        )
        self.value_entry.pack(fill=tk.X)

        # intent (per-step)
        tk.Label(
            right, text="Intent (auto-recognized)"
        ).pack()
        self.step_intent_var = tk.StringVar()
        self.step_intent_entry = tk.Entry(
            right, textvariable=self.step_intent_var
        )
        self.step_intent_entry.pack(fill=tk.X)

        # label (semantic)
        tk.Label(
            right, text="Label (optional)"
        ).pack()
        self.label_var = tk.StringVar()
        self.label_entry = tk.Entry(
            right, textvariable=self.label_var
        )
        self.label_entry.pack(fill=tk.X)

        # correction list
        tk.Label(
            right,
            text="Corrections (纠偏建议)",
            font=("Arial", 9, "bold")
        ).pack(fill=tk.X, pady=(10, 2))
        self.correction_listbox = tk.Listbox(
            right, height=5, fg="red"
        )
        self.correction_listbox.pack(
            fill=tk.X, padx=2
        )
        self.correction_listbox.bind(
            "<<ListboxSelect>>",
            self.on_correction_select
        )

        # ---------------- buttons ----------------
        btn_frame = tk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(
            btn_frame, text="Update",
            command=self.update_step
        ).pack(side=tk.LEFT)
        tk.Button(
            btn_frame, text="Delete",
            command=self.delete_step
        ).pack(side=tk.LEFT)
        tk.Button(
            btn_frame, text="Up",
            command=self.move_up
        ).pack(side=tk.LEFT)
        tk.Button(
            btn_frame, text="Down",
            command=self.move_down
        ).pack(side=tk.LEFT)
        tk.Button(
            btn_frame, text="Save",
            command=self.save
        ).pack(side=tk.LEFT)

    # -------------------------
    # refresh intent bar
    # -------------------------
    def refresh_intent_bar(self):
        intent = self.intent.get(
            "overall_intent", "unknown"
        )
        self.intent_var.set(intent)

        phases = self.intent.get("phases", [])
        if phases:
            self.phases_var.set(", ".join(phases))
        else:
            self.phases_var.set("(none)")

    # -------------------------
    # refresh list
    # -------------------------
    def refresh_list(self):
        self.listbox.delete(0, tk.END)

        for i, s in enumerate(self.steps):
            label = s.get("label", "")
            action = s.get("action", "")
            value = s.get("value", "")
            intent = s.get("intent", "")

            display = (
                f"{i}. {action} | {value}"
                f" | intent:{intent} | {label}"
            )
            self.listbox.insert(tk.END, display)

    # -------------------------
    # select step
    # -------------------------
    def on_select(self, event):
        if not self.listbox.curselection():
            return

        index = self.listbox.curselection()[0]
        self.selected_index = index
        self._load_step_into_editor(index)

    # -------------------------
    # refresh corrections display
    # -------------------------
    def refresh_corrections(self):
        self.correction_listbox.delete(0, tk.END)
        if not self.corrections:
            self.correction_listbox.insert(
                tk.END, "(No issues found)"
            )
            return

        severity_icons = {
            "error": "!!",
            "warning": "!",
            "info": "i"
        }
        for i, c in enumerate(self.corrections):
            icon = severity_icons.get(
                c.get("severity", "info"), "?"
            )
            display = (
                f"{icon} [{c['type']}] "
                f"{c['message']}"
            )
            self.correction_listbox.insert(
                tk.END, display
            )

    # -------------------------
    # correction selected
    # -------------------------
    def on_correction_select(self, event):
        if not self.correction_listbox.curselection():
            return
        index = (
            self.correction_listbox.curselection()[0]
        )
        if index >= len(self.corrections):
            return
        c = self.corrections[index]
        step_idx = c.get("step_index")
        if step_idx is not None:
            if 0 <= step_idx < len(self.steps):
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(step_idx)
                self.listbox.see(step_idx)
                self.selected_index = step_idx
                self._load_step_into_editor(step_idx)

    # -------------------------
    # load step into editor
    # -------------------------
    def _load_step_into_editor(self, index):
        step = self.steps[index]
        self.action_var.set(step.get("action", ""))
        self.value_var.set(step.get("value", ""))
        self.step_intent_var.set(
            step.get("intent", "")
        )
        self.label_var.set(step.get("label", ""))

    # -------------------------
    # update overall intent
    # -------------------------
    def update_intent(self):
        self.intent["overall_intent"] = (
            self.intent_var.get()
        )
        print(
            "[Hermes] Intent updated to: "
            f"{self.intent_var.get()}"
        )

    # -------------------------
    # update step
    # -------------------------
    def update_step(self):
        if self.selected_index is None:
            return

        self.steps[self.selected_index] = {
            "action": self.action_var.get(),
            "value": self.value_var.get(),
            "intent": self.step_intent_var.get(),
            "label": self.label_var.get()
        }

        self.refresh_list()

    # -------------------------
    # delete step
    # -------------------------
    def delete_step(self):
        if self.selected_index is None:
            return

        del self.steps[self.selected_index]
        self.selected_index = None

        self.refresh_list()

    # -------------------------
    # move up
    # -------------------------
    def move_up(self):
        i = self.selected_index
        if i is None or i == 0:
            return

        self.steps[i], self.steps[i-1] = (
            self.steps[i-1], self.steps[i]
        )
        self.selected_index -= 1

        self.refresh_list()

    # -------------------------
    # move down
    # -------------------------
    def move_down(self):
        i = self.selected_index
        if i is None or i >= len(self.steps) - 1:
            return

        self.steps[i], self.steps[i+1] = (
            self.steps[i+1], self.steps[i]
        )
        self.selected_index += 1

        self.refresh_list()

    # -------------------------
    # save skill
    # -------------------------
    def save(self):
        with open(
            "skill.json", "w", encoding="utf-8"
        ) as f:
            json.dump({
                "steps": self.steps,
                "intent": self.intent,
                "corrections": self.corrections,
            }, f, indent=2, ensure_ascii=False)
        print("[Hermes] HUMAN REVIEW SAVED")


# -------------------------
# launch
# -------------------------
if __name__ == "__main__":
    ReviewUI()

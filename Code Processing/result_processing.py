import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import re


class WekaDiagnosisSystem:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Hệ thống Chẩn đoán Bệnh")
        self.window.geometry("1000x800")

        self.rules = []  # List of (conditions, result, confidence)
        self.all_symptoms = set()  # All possible symptoms
        self.symptom_vars = {}  # Checkbox variables for each symptom

        self.create_gui()

    def create_gui(self):
        # Create main split pane
        main_paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Symptoms selection
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Right side: Results display
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        # Control buttons
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Load Rules File", command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Diagnose", command=self.diagnose).pack(side=tk.LEFT, padx=5)

        # Symptoms selection area
        symptom_frame = ttk.LabelFrame(left_frame, text="Select Symptoms", padding="5")
        symptom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create scrollable frame for symptoms
        self.canvas = tk.Canvas(symptom_frame)
        scrollbar = ttk.Scrollbar(symptom_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Results area
        result_frame = ttk.LabelFrame(right_frame, text="Diagnosis Results", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def parse_weka_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Clear existing rules
            self.rules.clear()
            self.all_symptoms.clear()

            # Extract attributes (symptoms)
            attributes_section = re.search(r"Attributes:(.*?)===", content, re.DOTALL)
            if attributes_section:
                attributes_text = attributes_section.group(1)
                for line in attributes_text.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('Disease='):
                        self.all_symptoms.add(line)

            # Extract rules
            rules_section = content.split("===")[-1]
            rule_matches = re.findall(
                r"\d+\.\s+\[(.*?)\](?::\s*\d+)?\s*==>\s*\[(.*?)\](?::\s*\d+)?\s*<conf:\(([\d.]+)\)>",
                rules_section
            )

            for condition_str, result_str, confidence in rule_matches:
                conditions = []
                # Process conditions
                for cond in condition_str.split(','):
                    cond = cond.strip()
                    if '=t' in cond:
                        symptom = cond.replace('=t', '').strip()
                        conditions.append(symptom)

                # Process result (disease)
                disease = None
                if 'Disease=' in result_str:
                    disease_match = re.search(r'Disease=(\w+)=t', result_str)
                    if disease_match:
                        disease = disease_match.group(1)

                # Add Critical status if present
                if 'Critical=' in condition_str:
                    critical_match = re.search(r'Critical=(\w+)', condition_str)
                    if critical_match:
                        critical_status = critical_match.group(1)
                        conditions.append(f"Critical={critical_status}")

                # Only add rule if both conditions and disease are present
                if conditions and disease:
                    self.rules.append((conditions, disease, float(confidence)))

            messagebox.showinfo("Success",
                                f"Loaded {len(self.rules)} rules and {len(self.all_symptoms)} symptoms.")

        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")

    def create_symptom_checkboxes(self):
        # Clear existing checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.symptom_vars.clear()

        # Group symptoms by category
        symptom_categories = {}
        for symptom in self.all_symptoms:
            category, symptom_name = symptom.split('=')
            if category not in symptom_categories:
                symptom_categories[category] = []
            symptom_categories[category].append(symptom_name)

        # Add Critical status
        if 'Critical' not in symptom_categories:
            symptom_categories['Critical'] = ['Critical', 'Not Critical']

        # Create checkboxes grouped by category
        for category, symptoms in symptom_categories.items():
            ttk.Label(
                self.scrollable_frame,
                text=category,
                font=('Arial', 10, 'bold')
            ).pack(anchor='w', padx=5, pady=(10, 5))

            for symptom_name in symptoms:
                full_symptom = f"{category}={symptom_name}"
                var = tk.BooleanVar()
                self.symptom_vars[full_symptom] = var
                ttk.Checkbutton(
                    self.scrollable_frame,
                    text=symptom_name,
                    variable=var
                ).pack(anchor='w', padx=20, pady=2)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.parse_weka_file(file_path)
            self.create_symptom_checkboxes()

    def diagnose(self):
        # Get selected symptoms
        selected_symptoms = [
            symptom for symptom, var in self.symptom_vars.items()
            if var.get()
        ]

        if not selected_symptoms:
            messagebox.showwarning("Warning", "Please select at least one symptom.")
            return

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Display selected symptoms
        self.result_text.insert(tk.END, "SELECTED SYMPTOMS:\n")
        for symptom in selected_symptoms:
            self.result_text.insert(tk.END, f"- {symptom}\n")

        self.result_text.insert(tk.END, "\nDIAGNOSIS RESULTS:\n")

        # Find matching rules
        matching_results = []
        for conditions, disease, confidence in self.rules:
            condition_set = set(conditions)
            selected_set = set(selected_symptoms)

            # Check for Critical status
            critical_condition = next((c for c in condition_set if c.startswith('Critical=')), None)
            critical_selected = next((s for s in selected_set if s.startswith('Critical=')), None)

            # Check if conditions match
            symptoms_match = condition_set.issubset(selected_set)
            critical_match = (critical_condition == critical_selected) if critical_condition else True

            if symptoms_match and critical_match:
                matching_results.append((disease, confidence))

        # Display results
        if matching_results:
            matching_results.sort(key=lambda x: x[1], reverse=True)
            for disease, confidence in matching_results:
                self.result_text.insert(
                    tk.END,
                    f"Disease: {disease} (Confidence: {confidence * 100:.1f}%)\n"
                )
        else:
            self.result_text.insert(
                tk.END,
                "No matching diseases found for the selected symptoms."
            )

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = WekaDiagnosisSystem()
    app.run()
#!/usr/bin/env python3
"""
SysVulScorer – Modern GUI with Sensitivity Analysis
"""

import os, json, math
try:
    import pandas as pd
except:
    pd = None

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

base = ""

CONFIG_FILE = "settings.json"
DEFAULT_THEME = "darkly"
ALL_THEMES = ["flatly", "cosmo", "minty", "journal", "litera",
              "superhero", "cyborg", "darkly", "solar"]


# ------------------ UTILITIES ------------------

def load_settings():
    defaults = {
        "theme": DEFAULT_THEME,
        "exp_exposed": 1.0,
        "exp_non_exposed": 0.75,
        "maturity_boundary": 0.5,
        "maturity_high": 1.0,
        "maturity_low": 0.75
    }
    if os.path.exists(CONFIG_FILE):
        try:
            s = json.load(open(CONFIG_FILE))
            defaults.update(s)
        except:
            pass
    return defaults


def save_settings(settings):
    with open(CONFIG_FILE, "w") as fh:
        json.dump(settings, fh)


def safe_float(v, default=0.0):
    try:
        if v is None or v == "" or (isinstance(v, float) and math.isnan(v)):
            return default
        return float(v)
    except:
        return default


# ------------------ COMPUTATION ------------------

def compute_adjusted(cvss, internet, exposed, non_exposed, epss, m_high, m_low, m_boundary):
    e = exposed if internet.upper() == "Y" else non_exposed
    m = m_high if epss >= m_boundary else m_low
    v = cvss * e * m
    return round(v, 4), round(e, 3), round(m, 3)


def aggregate_scores(vlist):
    prod = 1.0
    for v in vlist:
        prod *= (1 - v / 10)
    X = 1 - prod
    avg = sum(vlist) / len(vlist) if vlist else 0
    mx = max(vlist) if vlist else 0
    X = X * 10
    return round(X, 6), round(avg, 4), round(mx, 4)


# ------------------ MAIN GUI CLASS ------------------

class SysVulScorer_GUI:
    def __init__(self):
        self.settings = load_settings()
        self.app = tb.Window(title="SysVulScorer – Adjusted/Aggregated Scores",
                             themename=self.settings["theme"])
        self.app.geometry("1200x720")

        self.notebook = tb.Notebook(self.app)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.main_tab = tb.Frame(self.notebook)
        self.adjusted_tab = tb.Frame(self.notebook)
        self.aggregated_tab = tb.Frame(self.notebook)
        self.settings_tab = tb.Frame(self.notebook)
        self.sensitivity_tab = tb.Frame(self.notebook)

        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.adjusted_tab, text="Adjusted Scores")
        self.notebook.add(self.aggregated_tab, text="Aggregated Scores")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.sensitivity_tab, text="Sensitivity Analysis")

        self.build_main_tab()
        self.build_settings_tab()
        self.build_sensitivity_tab()

    # ------------------ MAIN TAB ------------------

    def build_main_tab(self):
        frm = tb.Frame(self.main_tab, padding=10)
        frm.pack(fill="both", expand=True)

        tb.Label(frm, text="SysVulScorer Formulas",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

        eq_text = (
            "Adjusted Score: V = CVSS × Exposure × Maturity\n"
            "Exposure = exposed if EPS ≥ Maturity_Boundary else non-exposed\n"
            "Maturity = High if EPS ≥ Maturity_Boundary else Low\n"
            "Aggregate per CS:\n"
            "  X = 1 - ∏(1 - V_i/10)\n"
            "  Max = max(V_i)\n"
            "  Average = mean(V_i)"
        )
        tb.Label(frm, text=eq_text, font=("Consolas", 12)).pack(anchor="w", pady=5)

        # File selection
        filefrm = tb.Frame(frm)
        filefrm.pack(fill="x", pady=10)
        tb.Label(filefrm, text="Input CSV:").grid(row=0, column=0, sticky="w")
        self.in_var = tk.StringVar()
        tb.Entry(filefrm, textvariable=self.in_var, width=80).grid(row=0, column=1)
        tb.Button(filefrm, text="Browse", bootstyle=PRIMARY,
                  command=self.pick_input).grid(row=0, column=2)

        # Parameters
        paramfrm = tb.Labelframe(frm, text="Exposure & Maturity Parameters")
        paramfrm.pack(fill="x", pady=10)

        self.exp_exposed = tk.StringVar(value=str(self.settings.get("exp_exposed", 1.0)))
        self.exp_non = tk.StringVar(value=str(self.settings.get("exp_non_exposed", 0.75)))
        self.m_boundary = tk.StringVar(value=str(self.settings.get("maturity_boundary", 0.5)))
        self.m_high = tk.StringVar(value=str(self.settings.get("maturity_high", 1.0)))
        self.m_low = tk.StringVar(value=str(self.settings.get("maturity_low", 0.75)))

        labels = [
            ("Exposure (Exposed)", self.exp_exposed),
            ("Exposure (Non Exposed)", self.exp_non),
            ("Maturity Boundary", self.m_boundary),
            ("Maturity High", self.m_high),
            ("Maturity Low", self.m_low),
        ]

        for i, (txt, var) in enumerate(labels):
            tb.Label(paramfrm, text=txt).grid(row=i // 2, column=(i % 2) * 2, padx=5, pady=2, sticky="w")
            tb.Entry(paramfrm, textvariable=var, width=10).grid(row=i // 2, column=(i % 2) * 2 + 1)

        tb.Button(frm, text="Process Input", bootstyle=SUCCESS,
                  command=self.process_input).pack(pady=10)

        # Log output
        tb.Label(frm, text="Log Output:").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(frm, height=12, font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)

    # ------------------ SETTINGS TAB ------------------

    def build_settings_tab(self):
        frm = tb.Frame(self.settings_tab, padding=10)
        frm.pack(fill="both", expand=True)

        tb.Label(frm, text="Theme Settings",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=10)

        self.theme_var = tk.StringVar(value=self.settings.get("theme", DEFAULT_THEME))

        tb.Label(frm, text="Select Theme:").pack(anchor="w")
        self.theme_menu = tb.Combobox(frm, textvariable=self.theme_var,
                                      values=ALL_THEMES, state="readonly", width=20)
        self.theme_menu.pack(anchor="w", pady=5)

        tb.Button(frm, text="Apply Theme", bootstyle=INFO,
                  command=self.apply_theme).pack(anchor="w", pady=5)

    # ------------------ SENSITIVITY TAB ------------------

    def build_sensitivity_tab(self):
        frm = tb.Frame(self.sensitivity_tab, padding=10)
        frm.pack(fill="both", expand=True)

        tb.Label(frm, text="Sensitivity Analysis",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

        slider_frame = tb.Frame(frm)
        slider_frame.pack(fill="x", pady=5)

        # Slider variables
        self.sens_vars = {
            "exp_exposed": tk.DoubleVar(value=self.settings.get("exp_exposed", 1.0)),
            "exp_non_exposed": tk.DoubleVar(value=self.settings.get("exp_non_exposed", 0.75)),
            "maturity_high": tk.DoubleVar(value=self.settings.get("maturity_high", 1.0)),
            "maturity_low": tk.DoubleVar(value=self.settings.get("maturity_low", 0.75)),
            "maturity_boundary": tk.DoubleVar(value=self.settings.get("maturity_boundary", 0.5)),
        }

        labels = {
            "exp_exposed": "Exposure (Exposed)",
            "exp_non_exposed": "Exposure (Non Exposed)",
            "maturity_high": "Maturity High",
            "maturity_low": "Maturity Low",
            "maturity_boundary": "Maturity Boundary",
        }

        self.sens_value_labels = {}

        for i, (k, text) in enumerate(labels.items()):
            tb.Label(slider_frame, text=text).grid(row=i, column=0, sticky="w")

            var = self.sens_vars[k]
            scale = tk.Scale(
                slider_frame, from_=0.00, to=1.00, orient="horizontal",
                resolution=0.05, variable=var, showvalue=False, length=300,
                command=lambda e, k=k: self.update_sensitivity_table()
            )
            scale.grid(row=i, column=1, sticky="we")

            val_label = tb.Label(slider_frame, text=f"{var.get():.2f}")
            val_label.grid(row=i, column=2, padx=5)
            self.sens_value_labels[k] = val_label

            var.trace_add("write", lambda *a, k=k:
                          self.sens_value_labels[k].config(
                              text=f"{self.sens_vars[k].get():.2f}"
                          ))

        # Frames for table and plot
        self.sens_tree_frame = tb.Frame(frm)
        self.sens_tree_frame.pack(fill="both", expand=True, pady=10)

        self.sens_plot_frame = tb.Frame(frm)
        self.sens_plot_frame.pack(fill="both", expand=True, pady=10)

        # Export button
        tb.Button(
            frm, text="Export Sensitivity Results",
            bootstyle=INFO, command=self.export_sensitivity_csv
        ).pack(pady=5)

        self.sens_log = scrolledtext.ScrolledText(frm, height=5, font=("Consolas", 10))
        self.sens_log.pack(fill="both", expand=True)

        self.sens_tree = None

    # ------------------ HELPER FUNCTIONS ------------------

    def pick_input(self):
        file = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if file:
            self.in_var.set(file)

    def log_print(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def apply_theme(self):
        new_theme = self.theme_var.get()
        self.app.style.theme_use(new_theme)
        self.settings["theme"] = new_theme
        save_settings(self.settings)
        messagebox.showinfo("Theme Updated", f"Theme changed to: {new_theme}")

    # ------------------ PROCESS CSV INPUT ------------------

    def process_input(self):
        infile = self.in_var.get().strip()
        self.base = infile
        if not infile or not os.path.exists(infile):
            messagebox.showerror("Input Error", "Please select a valid CSV file.")
            return

        # Load parameters
        exp_ex = safe_float(self.exp_exposed.get(), 1.0)
        exp_nx = safe_float(self.exp_non.get(), 0.75)
        mb = safe_float(self.m_boundary.get(), 0.5)
        mh = safe_float(self.m_high.get(), 1.0)
        ml = safe_float(self.m_low.get(), 0.75)

        # Save new settings
        self.settings.update({
            "exp_exposed": exp_ex,
            "exp_non_exposed": exp_nx,
            "maturity_boundary": mb,
            "maturity_high": mh,
            "maturity_low": ml
        })
        save_settings(self.settings)

        # Load CSV
        if pd:
            df = pd.read_csv(infile)
            rows = df.to_dict(orient="records")
        else:
            import csv
            with open(infile, newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))

        # Compute adjusted rows
        adjusted = []
        for r in rows:
            cvss = safe_float(r.get("CVSS") or r.get("cvss"))
            epss = safe_float(r.get("epss") or r.get("EPSS"))
            exp = r.get("Internet") or r.get("internet") or "N"
            v, e, m = compute_adjusted(cvss, exp, exp_ex, exp_nx, epss, mh, ml, mb)
            newrow = dict(r)
            newrow.update({"Adjusted_V": v, "Exposure": e, "Maturity": m})
            adjusted.append(newrow)

        base, _ = os.path.splitext(infile)
        adjusted_file = base + "_adjusted.csv"

        if pd:
            pd.DataFrame(adjusted).to_csv(adjusted_file, index=False)
        else:
            import csv
            with open(adjusted_file, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=adjusted[0].keys())
                writer.writeheader()
                writer.writerows(adjusted)

        self.log_print(f"Adjusted CSV saved: {adjusted_file}")
        self.show_tab_data(self.adjusted_tab, adjusted, "Adjusted Scores")

        # Aggregate per CS
        cs_map = {}
        for r in adjusted:
            cs = r.get("CS") or r.get("cs")
            cs_map.setdefault(cs, []).append(r["Adjusted_V"])

        aggregated = []
        for cs, vlist in cs_map.items():
            X, avg, mx = aggregate_scores(vlist)
            aggregated.append({
                "CS": cs,
                "X_formula": X,
                "Max_V": mx,
                "Average_V": avg
            })

        aggregated_file = base + "_aggregated.csv"
        if pd:
            pd.DataFrame(aggregated).to_csv(aggregated_file, index=False)
        else:
            import csv
            with open(aggregated_file, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=aggregated[0].keys())
                writer.writeheader()
                writer.writerows(aggregated)

        self.log_print(f"Aggregated CSV saved: {aggregated_file}")
        self.show_tab_data(self.aggregated_tab, aggregated, "Aggregated Scores")

        # Load into sensitivity tab
        self.sens_rows = adjusted
        self.update_sensitivity_table()

    # ------------------ SENSITIVITY ANALYSIS LOGIC ------------------

    def update_sensitivity_table(self):
        if not hasattr(self, "sens_rows") or not self.sens_rows:
            return

        exp_ex = self.sens_vars["exp_exposed"].get()
        exp_nx = self.sens_vars["exp_non_exposed"].get()
        mh = self.sens_vars["maturity_high"].get()
        ml = self.sens_vars["maturity_low"].get()
        mb = self.sens_vars["maturity_boundary"].get()

        # Compute adjusted values
        adjusted = []
        for r in self.sens_rows:
            cvss = safe_float(r.get("CVSS") or r.get("cvss"))
            epss = safe_float(r.get("epss") or r.get("EPSS"))
            exp = r.get("Internet") or r.get("internet") or "N"
            v, e, m = compute_adjusted(cvss, exp, exp_ex, exp_nx, epss, mh, ml, mb)
            nr = dict(r)
            nr.update({"Adjusted_V": v, "Exposure": e, "Maturity": m})
            adjusted.append(nr)

        # Aggregate per CS
        cs_map = {}
        for r in adjusted:
            cs = r.get("CS") or r.get("cs")
            cs_map.setdefault(cs, []).append(r["Adjusted_V"])

        aggregated = []
        for cs, vlist in cs_map.items():
            X, avg, mx = aggregate_scores(vlist)
            aggregated.append({
                "CS": cs,
                "X_formula": X,
                "Max_V": mx,
                "Average_V": avg
            })

        # Update treeview
        for w in self.sens_tree_frame.winfo_children():
            w.destroy()

        cols = ["CS", "X_formula", "Max_V", "Average_V"]
        self.sens_tree = ttk.Treeview(self.sens_tree_frame,
                                      columns=cols, show="headings")
        self.sens_tree.pack(fill="both", expand=True)

        for c in cols:
            self.sens_tree.heading(c, text=c)
            self.sens_tree.column(c, width=120, anchor="center")

        for row in aggregated:
            self.sens_tree.insert("", "end", values=[row[c] for c in cols])

        # Update plot
        for w in self.sens_plot_frame.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot([r["Adjusted_V"] for r in adjusted], marker="o")
        ax.set_title("Adjusted Score per Vulnerability")
        ax.set_xlabel("Index")
        ax.set_ylabel("Adjusted V")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.sens_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.sens_log.delete("1.0", "end")
        self.sens_log.insert(
            "end",
            f"Sensitivity updated: {len(adjusted)} vulnerabilities, {len(aggregated)} CS scores.\n"
        )

    # ------------------ EXPORT SENSITIVITY DATA ------------------

    def export_sensitivity_csv(self):
        if not self.sens_tree:
            messagebox.showwarning("No Data", "Run sensitivity analysis first.")
            return

        # outfile = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        # base, _ = os.path.splitext(infile)
        outfile =  self.base + "_sensitivity.csv"
        if not outfile:
            return

        cols = self.sens_tree["columns"]
        data = []
        for item in self.sens_tree.get_children():
            vals = self.sens_tree.item(item)["values"]
            data.append(dict(zip(cols, vals)))

        if pd:
            pd.DataFrame(data).to_csv(outfile, index=False)
        else:
            import csv
            with open(outfile, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=cols)
                writer.writeheader()
                writer.writerows(data)

        # messagebox.showinfo("Exported", f"Sensitivity results exported to:\n{outfile}")
        self.sens_log.insert(
            "end",
            f"Sensitivity results exported to:{outfile}.\n"
        )

    # ------------------ TAB DATA VIEW ------------------

    def show_tab_data(self, tab, data, title=""):
        for w in tab.winfo_children():
            w.destroy()

        frm = tb.Frame(tab, padding=10)
        frm.pack(fill="both", expand=True)

        tb.Label(frm, text=title, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

        if not data:
            return

        cols = list(data[0].keys())
        tree = ttk.Treeview(frm, columns=cols, show="headings")
        tree.pack(fill="both", expand=True)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor="center")

        for r in data:
            tree.insert("", "end", values=[r.get(c, "") for c in cols])

    # ------------------ RUN ------------------

    def run_loop(self):
        self.app.mainloop()


# ------------------ MAIN ------------------

if __name__ == "__main__":
    gui = SysVulScorer_GUI()
    gui.run_loop()

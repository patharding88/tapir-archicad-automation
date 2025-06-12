# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
CDC Bench Tools - Archicad Automation Script
===========================================

A tool for calculating bench and FFL RLs, slab thickness, and site checks for Archicad.

Requirements:
- Python 3.x
- tkinter (for UI)
- math (for calculations)
- re (for string parsing)

"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import re

__version__ = '1.0.0'  # CDC Bench Tools version

SLAB_THICKNESS_OPTIONS = [
    ("S8/WM8", 0.310),
    ("S9/WM9", 0.325),
    ("WH18", 0.385),
    ("WH19", 0.400),
    ("WH2-8/9", 0.400),
    ("E", 0.475),
    ("460mm", 0.460),
]

class CDCBenchToolsApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CDC Bench Tools - Archicad Automation")
        self.master.geometry("700x650")
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # RL Input
        rl_frame = ttk.LabelFrame(main_frame, text="Input RLs (separate by + or comma)")
        rl_frame.pack(fill='x', pady=5)
        self.rl_var = tk.StringVar()
        ttk.Entry(rl_frame, textvariable=self.rl_var, width=50).pack(side='left', padx=5)

        # Slab Thickness Dropdown (show thickness in name)
        slab_frame = ttk.Frame(main_frame)
        slab_frame.pack(fill='x', pady=5)
        ttk.Label(slab_frame, text="Slab Thickness:").pack(side='left', padx=5)
        self.slab_options = [f"{name} ({int(thick*1000)}mm)" for name, thick in SLAB_THICKNESS_OPTIONS]
        self.slab_var = tk.StringVar(value=self.slab_options[0])
        slab_menu = ttk.Combobox(slab_frame, textvariable=self.slab_var, values=self.slab_options, state="readonly", width=20)
        slab_menu.pack(side='left', padx=5)

        # Minimum FFL RL
        min_ffl_frame = ttk.Frame(main_frame)
        min_ffl_frame.pack(fill='x', pady=5)
        ttk.Label(min_ffl_frame, text="Minimum FFL RL (Flood Height):").pack(side='left', padx=5)
        self.min_ffl_var = tk.DoubleVar(value=0.0)
        ttk.Entry(min_ffl_frame, textvariable=self.min_ffl_var, width=10).pack(side='left', padx=5)

        # Calculate Button (main results)
        calc_btn = ttk.Button(main_frame, text="Calculate Main Results", command=self.calculate_results)
        calc_btn.pack(pady=8)

        # Results Box
        results_frame = ttk.LabelFrame(main_frame, text="Results")
        results_frame.pack(fill='both', expand=True, pady=5)
        self.results_text = scrolledtext.ScrolledText(results_frame, height=12, font=("Consolas", 10))
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Checks Section
        checks_frame = ttk.LabelFrame(main_frame, text="Site Checks")
        checks_frame.pack(fill='x', pady=5)
        ttk.Label(checks_frame, text="Road High RL:").grid(row=0, column=0, padx=2, pady=2)
        self.road_high_var = tk.DoubleVar(value=0.0)
        ttk.Entry(checks_frame, textvariable=self.road_high_var, width=8).grid(row=0, column=1, padx=2)
        ttk.Label(checks_frame, text="Road Low RL:").grid(row=0, column=2, padx=2)
        self.road_low_var = tk.DoubleVar(value=0.0)
        ttk.Entry(checks_frame, textvariable=self.road_low_var, width=8).grid(row=0, column=3, padx=2)
        ttk.Label(checks_frame, text="Neighbour RL 1:").grid(row=1, column=0, padx=2, pady=2)
        self.neigh1_var = tk.DoubleVar(value=0.0)
        ttk.Entry(checks_frame, textvariable=self.neigh1_var, width=8).grid(row=1, column=1, padx=2)
        self.zero1_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(checks_frame, text="Zero Boundary", variable=self.zero1_var).grid(row=1, column=2, padx=2)
        ttk.Label(checks_frame, text="Neighbour RL 2:").grid(row=2, column=0, padx=2)
        self.neigh2_var = tk.DoubleVar(value=0.0)
        ttk.Entry(checks_frame, textvariable=self.neigh2_var, width=8).grid(row=2, column=1, padx=2)
        self.zero2_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(checks_frame, text="Zero Boundary", variable=self.zero2_var).grid(row=2, column=2, padx=2)

        # Site Checks Button
        site_checks_btn = ttk.Button(main_frame, text="Calculate Site Checks", command=self.calculate_site_checks)
        site_checks_btn.pack(pady=8)

        # Second Results/Warnings Box
        self.checks_results_text = scrolledtext.ScrolledText(main_frame, height=9, font=("Consolas", 10))
        self.checks_results_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Version label
        version_label = ttk.Label(self.master, text=f"CDC Bench Tools v{__version__}", anchor='e')
        version_label.pack(side='bottom', fill='x', padx=5, pady=2)

    def calculate_results(self):
        self.results_text.delete(1.0, tk.END)
        # --- Parse RLs ---
        rl_input = self.rl_var.get().replace(' ', '')
        rl_values = re.split(r'[+,]', rl_input)
        try:
            rls = [round(float(v), 3) for v in rl_values if v]
        except Exception as e:
            self.results_text.insert(tk.END, f"Error parsing RLs: {e}\n")
            self._main_results = None
            return
        if not rls:
            self.results_text.insert(tk.END, "No RLs provided.\n")
            self._main_results = None
            return
        rls.sort()
        bench_rl = round(sum(rls) / len(rls), 3)
        highest_rl = max(rls)
        lowest_rl = min(rls)
        cut_max = round(highest_rl - bench_rl, 3)
        fill_max = round(lowest_rl - bench_rl, 3)

        # --- Slab thickness ---
        slab_label_full = self.slab_var.get()
        # Extract slab name and thickness from dropdown
        for name, thick in SLAB_THICKNESS_OPTIONS:
            if name in slab_label_full:
                slab_label = name
                slab_thickness = thick
                break
        else:
            slab_label = slab_label_full
            slab_thickness = 0.0
        ffl_rl = round(bench_rl + slab_thickness, 3)

        # --- Minimum FFL RL (Flood Height) ---
        min_ffl_rl = round(self.min_ffl_var.get(), 3)
        fill_to_min_ffl = round(max(0, min_ffl_rl - ffl_rl), 3)

        # --- External area RLs ---
        ext_tile_rl = round(bench_rl - 0.07, 3)
        ext_deck_rl = round(bench_rl - 0.09, 3)
        service_pad_rl = round(ffl_rl - 0.12, 3)

        # --- Results Output (formatted) ---
        self.results_text.insert(tk.END, "==== INPUT RLs ====" + "\n")
        self.results_text.insert(tk.END, f"  {', '.join(f'{v:.3f}' for v in rls)}\n\n")
        self.results_text.insert(tk.END, "==== CALCULATED LEVELS ====" + "\n")
        self.results_text.insert(tk.END, f"  Average RL (Bench RL):      {bench_rl:.3f} m\n")
        self.results_text.insert(tk.END, f"  FFL RL (Top of Slab):       {ffl_rl:.3f} m\n")
        self.results_text.insert(tk.END, f"  Slab Thickness:             {slab_label} ({slab_thickness*1000:.0f} mm)\n")
        if min_ffl_rl > 0:
            self.results_text.insert(tk.END, f"  Minimum FFL RL (Flood):     {min_ffl_rl:.3f} m\n")
        self.results_text.insert(tk.END, f"  Fill needed to min FFL RL:  {fill_to_min_ffl:.3f} m\n\n")
        self.results_text.insert(tk.END, "==== SITE CUT/FILL ====" + "\n")
        self.results_text.insert(tk.END, f"  CUT MAX (Highest RL - Bench): {cut_max:+.3f} m\n")
        self.results_text.insert(tk.END, f"  FILL MAX (Lowest RL - Bench): {fill_max:+.3f} m\n\n")
        self.results_text.insert(tk.END, "==== EXTERNAL LEVELS ====" + "\n")
        self.results_text.insert(tk.END, f"  External Area RL (Tile):    {ext_tile_rl:.3f} m\n")
        self.results_text.insert(tk.END, f"  External Area RL (Deck):    {ext_deck_rl:.3f} m\n")
        self.results_text.insert(tk.END, f"  Service Pad RL:             {service_pad_rl:.3f} m\n")

        # Store for site checks
        self._main_results = {
            'bench_rl': bench_rl,
            'ffl_rl': ffl_rl,
            'cut_max': cut_max,
            'fill_max': fill_max
        }

    def calculate_site_checks(self):
        self.checks_results_text.delete(1.0, tk.END)
        # Must have main results
        if not hasattr(self, '_main_results') or self._main_results is None:
            self.checks_results_text.insert(tk.END, "Please calculate main results first.\n")
            return
        bench_rl = self._main_results['bench_rl']
        ffl_rl = self._main_results['ffl_rl']
        # --- Site Checks ---
        road_high = round(self.road_high_var.get(), 3)
        road_low = round(self.road_low_var.get(), 3)
        neigh1 = round(self.neigh1_var.get(), 3)
        neigh2 = round(self.neigh2_var.get(), 3)
        zero1 = self.zero1_var.get()
        zero2 = self.zero2_var.get()
        # Determine which neighbour is higher/lower
        if neigh1 >= neigh2:
            neigh_high, neigh_low = neigh1, neigh2
            zero_high, zero_low = zero1, zero2
        else:
            neigh_high, neigh_low = neigh2, neigh1
            zero_high, zero_low = zero2, zero1
        neigh_diff_high = abs(neigh_high - bench_rl)
        neigh_diff_low = abs(neigh_low - bench_rl)
        warnings = []
        # Stormwater requirements
        if road_high > ffl_rl and road_low > ffl_rl:
            warnings.append("- Both road high and low RLs are higher than FFL RL. Special stormwater requirements may be required (e.g., Strip Wastes, Charged Lines, Rubble Pits, Sump Pits).\n")
        # Driveway profile check
        if abs(road_high - ffl_rl) <= 0.6 or abs(road_low - ffl_rl) <= 0.6:
            warnings.append("- Driveway is within ±600mm of FFL RL. A driveway profile needs to be provided.\n")
        # Neighbour bench height checks (high side)
        if 0 < neigh_diff_high <= 0.4:
            msg = "- Higher neighbour bench height is 0-400mm different. Recommend retaining under fence by owner after handover."
            if zero_high:
                msg += " Dwelling is on zero boundary: additional garage treatments required (piering, drop edge beams, concrete retaining, drainage)."
            warnings.append(msg + "\n")
        if neigh_diff_high > 0.4:
            msg = "- Higher neighbour bench height is >400mm different. Recommend concrete retaining by CMA during build."
            if neigh_diff_high > 0.6:
                msg += " On a tight site, CMA is required to do concrete retaining."
                if zero_high:
                    msg += " Where garage is on zero high side, block-up will be required."
            warnings.append(msg + "\n")
        # Neighbour bench height checks (low side)
        if 0 < neigh_diff_low <= 0.4:
            msg = "- Lower neighbour bench height is 0-400mm different. Recommend retaining under fence by owner after handover."
            if zero_low:
                msg += " Dwelling is on zero boundary: additional garage treatments required (piering, drop edge beams, concrete retaining, drainage)."
            warnings.append(msg + "\n")
        if neigh_diff_low > 0.4:
            msg = "- Lower neighbour bench height is >400mm different. Recommend concrete retaining by CMA during build."
            if neigh_diff_low > 0.6:
                msg += " On a tight site, CMA is required to do concrete retaining."
                if zero_low:
                    msg += " Where garage is on zero low side, block-up will be required."
            warnings.append(msg + "\n")
        if warnings:
            self.checks_results_text.insert(tk.END, "==== SITE CHECKS & RECOMMENDATIONS ====" + "\n")
            for w in warnings:
                self.checks_results_text.insert(tk.END, w)
        else:
            self.checks_results_text.insert(tk.END, "No special site requirements detected.\n")


def main():
    root = tk.Tk()
    app = CDCBenchToolsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
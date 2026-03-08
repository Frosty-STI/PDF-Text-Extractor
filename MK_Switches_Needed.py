import tkinter as tk
from tkinter import ttk, messagebox
import math
import matplotlib.pyplot as plt


def calculate(show_math=False):
    try:
        runtime = float(entries["runtime"].get())
        time_per_match = float(entries["time_per_match"].get())
        players = float(entries["players"].get())
        losses_to_elimination = float(entries["losses_to_elimination"].get())
        losses_per_match = float(entries["losses_per_match"].get())
        players_per_switch = float(entries["players_per_switch"].get())
        players_per_match = float(entries["players_per_match"].get())

        if time_per_match <= 0 or losses_per_match <= 0 or players_per_switch <= 0:
            raise ValueError("Time per match, losses per match, and players per switch must be greater than 0.")

        min_matches = ((players - 1) * losses_to_elimination) / losses_per_match
        rounds_max = runtime / time_per_match
        rounds_max_floored = math.floor(rounds_max)

        if rounds_max_floored <= 0:
            raise ValueError("Runtime divided by time per match must be at least 1 round.")

        games_per_round = min_matches / rounds_max_floored
        switches_per_match = players_per_match / players_per_switch
        total_switches_needed = games_per_round * switches_per_match

        result_label.config(
            text=f"The total number of Switches given this tournament setup is {total_switches_needed:.2f}."
        )

        if show_math:
            show_math_window(
                runtime,
                time_per_match,
                players,
                losses_to_elimination,
                losses_per_match,
                players_per_switch,
                players_per_match,
                min_matches,
                rounds_max,
                rounds_max_floored,
                games_per_round,
                switches_per_match,
                total_switches_needed
            )

    except ValueError as e:
        messagebox.showerror("Input Error", f"Please enter valid numbers.\n\nDetails: {e}")


def show_math_window(runtime, time_per_match, players, losses_to_elimination,
                     losses_per_match, players_per_switch, players_per_match,
                     min_matches, rounds_max, rounds_max_floored,
                     games_per_round, switches_per_match, total_switches_needed):

    fig = plt.figure(figsize=(8, 6))
    fig.patch.set_facecolor("white")

    explanation = rf"""
Minimum Matches Required

$\frac{{(Players - 1) \times Losses\ to\ Elimination}}{{Losses\ per\ Match}}$

$= \frac{{({players:.2f} - 1) \times {losses_to_elimination:.2f}}}{{{losses_per_match:.2f}}} = {min_matches:.2f}$


Maximum Possible Rounds

$\frac{{Runtime}}{{Time\ per\ Match}}$

$= \frac{{{runtime:.2f}}}{{{time_per_match:.2f}}} = {rounds_max:.2f}$

$Floor({rounds_max:.2f}) = {rounds_max_floored}$


Games Per Round

$\frac{{Minimum\ Matches}}{{Maximum\ Rounds}}$

$= \frac{{{min_matches:.2f}}}{{{rounds_max_floored}}} = {games_per_round:.2f}$


Switches Per Match

$\frac{{Players\ per\ Match}}{{Players\ per\ Switch}}$

$= \frac{{{players_per_match:.2f}}}{{{players_per_switch:.2f}}} = {switches_per_match:.2f}$


Total Nintendo Switch Consoles Required

$Games\ per\ Round \times Switches\ per\ Match$

$= {games_per_round:.2f} \times {switches_per_match:.2f} = {total_switches_needed:.2f}$
"""

    plt.text(0.01, 0.99, explanation, fontsize=13, va="top")
    plt.axis("off")
    plt.title("Tournament Mathematics Explanation", fontsize=16)

    plt.show()


root = tk.Tk()
root.title("MK8 Tourney Switch Count Calculator")
root.geometry("520x420")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

title_label = ttk.Label(main_frame, text="Tournament Switch Calculator", font=("Arial", 16, "bold"))
title_label.pack(pady=(0, 15))

fields = [
    ("runtime", "Runtime (in minutes)"),
    ("time_per_match", "Time per match (in minutes)"),
    ("players", "Players (in people)"),
    ("losses_to_elimination", "Losses to elimination"),
    ("losses_per_match", "Losses per match (how many players 'lose' one match)"),
    ("players_per_switch", "Players per switch (how many players on one switch)"),
    ("players_per_match", "Players per match (how many players can play in one match)")
]

entries = {}

for key, label_text in fields:
    row = ttk.Frame(main_frame)
    row.pack(fill="x", pady=5)

    label = ttk.Label(row, text=label_text, width=55, anchor="w")
    label.pack(side="left")

    entry = ttk.Entry(row, width=15)
    entry.pack(side="right")
    entries[key] = entry

calculate_button = ttk.Button(main_frame, text="Calculate", command=lambda: calculate(False))
calculate_button.pack(pady=10)

math_button = ttk.Button(main_frame, text="Show Math Explanation", command=lambda: calculate(True))
math_button.pack(pady=5)

result_label = ttk.Label(main_frame, text="", wraplength=460, font=("Arial", 11))
result_label.pack(pady=10)

root.mainloop()

import sqlite3
from tkinter import *
from tkinter import messagebox, simpledialog
from scoring_engine import calculate_score

conn = sqlite3.connect("fantasy_cricket.db")
c = conn.cursor()
root = Tk()
root.title("Fantasy Cricket")

selected_team = []
team_name = ""
points_available = 100
points_used = 0

# UI Layout
cat_var = StringVar()

# --- Functions ---
def load_players(category):
    list_players.delete(0, END)
    c.execute("SELECT player FROM stats WHERE ctg=?", (category,))
    for p in c.fetchall():
        list_players.insert(END, p[0])

def get_player_value(player_name):
    """Return integer value for a player (safe conversion)."""
    c.execute("SELECT value FROM stats WHERE player=?", (player_name,))
    row = c.fetchone()
    if row and row[0] is not None:
        try:
            return int(row[0])
        except (ValueError, TypeError):
            try:
                return int(float(row[0]))
            except:
                return 0
    return 0

def add_player(event=None):
    global points_used, points_available
    sel = list_players.get(ACTIVE)
    if not sel:
        return
    if sel in selected_team:
        return
    val = get_player_value(sel)
    if val > points_available:
        messagebox.showerror("Not enough points", f"Player '{sel}' costs {val} points but only {points_available} available.")
        return
    selected_team.append(sel)
    list_selected.insert(END, sel)
    update_points()

def remove_player(event=None):
    global points_used, points_available
    sel = list_selected.get(ACTIVE)
    if sel in selected_team:
        selected_team.remove(sel)
        list_selected.delete(ACTIVE)
        update_points()

def update_points():
    global points_used, points_available
    points_used = 0
    for p in selected_team:
        points_used += get_player_value(p)
    points_available = max(0, 100 - points_used)
    lbl_points.config(text=f"Points Used: {points_used} | Available: {points_available}")

def new_team():
    global team_name, selected_team, points_available, points_used
    name = simpledialog.askstring("Team Name", "Enter team name:")
    if not name:
        return
    team_name = name
    selected_team = []
    list_selected.delete(0, END)
    points_available = 100
    points_used = 0
    update_points()

def save_team():
    if not team_name:
        messagebox.showerror("Error", "Create a team first!")
        return

    players = ",".join(selected_team)
    c.execute("INSERT OR REPLACE INTO teams VALUES (?,?,?)", (team_name, players, points_used))
    conn.commit()
    messagebox.showinfo("Saved", "Team saved successfully!")

def evaluate_team():
    if not selected_team:
        messagebox.showerror("Error", "No players in team!")
        return

    total_score = 0
    for p in selected_team:
        total_score += calculate_score(p)

    messagebox.showinfo("Team Score", f"Final score of {team_name}: {total_score}")

# --- UI WIDGETS ---
Frame(root).pack()

Label(root, text="Fantasy Cricket Team Builder", font=("Arial", 16, "bold")).pack(pady=10)

frame_main = Frame(root)
frame_main.pack()

# Category Buttons
for text, cat in [("Batsmen", "BAT"), ("Bowlers", "BWL"), ("WK", "WK"), ("All Rounder", "AR")]:
    Radiobutton(root, text=text, variable=cat_var, value=cat, command=lambda: load_players(cat_var.get())).pack(side=LEFT)

# Listboxes
frame_lists = Frame(root)
frame_lists.pack()

list_players = Listbox(frame_lists, width=30, height=15)
list_players.grid(row=0, column=0, padx=10)
list_players.bind("<Double-1>", add_player)

list_selected = Listbox(frame_lists, width=30, height=15)
list_selected.grid(row=0, column=1, padx=10)
list_selected.bind("<Double-1>", remove_player)

# Points Label
lbl_points = Label(root, text="Points Used: 0 | Available: 100", font=("Arial", 12))
lbl_points.pack(pady=10)

# Buttons
Frame(root).pack()
Button(root, text="New Team", width=20, command=new_team).pack(pady=5)
Button(root, text="Save Team", width=20, command=save_team).pack(pady=5)
Button(root, text="Evaluate Score", width=20, command=evaluate_team).pack(pady=5)

# ensure a default category loads on start
cat_var.set("BAT")
load_players(cat_var.get())

root.mainloop()

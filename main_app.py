import sqlite3
from tkinter import *
from tkinter import messagebox, simpledialog
from scoring_engine import calculate_score

# Database setup
conn = sqlite3.connect("fantasy_cricket.db")
c = conn.cursor()

# Create root window
root = Tk()
root.title("Fantasy Cricket Team Builder")
root.geometry("900x700")

# Global variables
selected_team = []
team_name = ""
points_available = 100
points_used = 0

# UI Layout
cat_var = StringVar()
list_players = None
list_selected = None
lbl_points = None

# --- DATABASE FUNCTIONS ---
def ensure_player_data():
    """Ensure player data exists in database"""
    try:
        c.execute("SELECT COUNT(*) FROM stats")
        count = c.fetchone()[0]
        if count == 0:
            # Insert sample data if empty
            sample_players = [
                ("Virat Kohli", "BAT", 10),
                ("Rohit Sharma", "BAT", 10),
                ("KL Rahul", "BAT", 9),
                ("Suryakumar Yadav", "BAT", 9),
                ("MS Dhoni", "WK", 10),
                ("Rishabh Pant", "WK", 9),
                ("Ravichandran Ashwin", "AR", 9),
                ("Hardik Pandya", "AR", 9),
                ("Jasprit Bumrah", "BWL", 10),
                ("Bhuvneshwar Kumar", "BWL", 9),
                ("Yuzvendra Chahal", "BWL", 8),
            ]
            c.executemany("INSERT INTO stats (player, ctg, value) VALUES (?, ?, ?)", sample_players)
            conn.commit()
            print("✓ Sample player data inserted")
    except Exception as e:
        print(f"Error ensuring player data: {e}")

# --- FUNCTIONS ---
def load_players(category):
    """Load players for selected category"""
    try:
        list_players.delete(0, END)
        c.execute("SELECT player FROM stats WHERE ctg=?", (category,))
        players = c.fetchall()
        
        if not players:
            list_players.insert(END, f"No players in {category} category")
            return
        
        for p in players:
            list_players.insert(END, p[0])
        print(f"✓ Loaded {len(players)} players from {category}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load players: {e}")
        print(f"Error loading players: {e}")

def get_player_value(player_name):
    """Return integer value for a player (safe conversion)."""
    try:
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
    except Exception as e:
        print(f"Error getting player value: {e}")
        return 0

def add_player(event=None):
    """Add player to selected team"""
    global points_used, points_available
    try:
        sel = list_players.get(ACTIVE)
        if not sel or "No players" in sel:
            return
        if sel in selected_team:
            messagebox.showwarning("Warning", "Player already in team!")
            return
        
        val = get_player_value(sel)
        if val > points_available:
            messagebox.showerror("Not enough points", 
                f"Player '{sel}' costs {val} points but only {points_available} available.")
            return
        
        selected_team.append(sel)
        list_selected.insert(END, sel)
        update_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add player: {e}")
        print(f"Error adding player: {e}")

def remove_player(event=None):
    """Remove player from selected team"""
    global points_used, points_available
    try:
        sel = list_selected.get(ACTIVE)
        if sel in selected_team:
            selected_team.remove(sel)
            list_selected.delete(ACTIVE)
            update_points()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove player: {e}")
        print(f"Error removing player: {e}")

def update_points():
    """Update points display"""
    global points_used, points_available
    try:
        points_used = 0
        for p in selected_team:
            points_used += get_player_value(p)
        points_available = max(0, 100 - points_used)
        lbl_points.config(text=f"Points Used: {points_used} | Available: {points_available}")
    except Exception as e:
        print(f"Error updating points: {e}")

def new_team():
    """Create new team"""
    global team_name, selected_team, points_available, points_used
    try:
        name = simpledialog.askstring("Team Name", "Enter team name:")
        if not name:
            return
        team_name = name
        selected_team = []
        list_selected.delete(0, END)
        points_available = 100
        points_used = 0
        update_points()
        messagebox.showinfo("Success", f"Team '{name}' created! Add players now.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create team: {e}")
        print(f"Error creating new team: {e}")

def save_team():
    """Save team to database"""
    global team_name
    try:
        if not team_name:
            messagebox.showerror("Error", "Create a team first!")
            return
        
        if not selected_team:
            messagebox.showerror("Error", "Add at least one player to the team!")
            return

        players = ",".join(selected_team)
        c.execute("INSERT OR REPLACE INTO teams VALUES (?,?,?)", 
                 (team_name, players, points_used))
        conn.commit()
        messagebox.showinfo("Saved", f"Team '{team_name}' saved successfully!")
        print(f"✓ Team '{team_name}' saved with {len(selected_team)} players")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save team: {e}")
        print(f"Error saving team: {e}")

def evaluate_team():
    """Calculate and display team score"""
    try:
        if not selected_team:
            messagebox.showerror("Error", "No players in team!")
            return

        total_score = 0
        score_details = []
        for p in selected_team:
            score = calculate_score(p)
            total_score += score
            score_details.append(f"{p}: {score}")

        details_text = "\n".join(score_details)
        messagebox.showinfo("Team Score", 
            f"Team: {team_name}\n\n{details_text}\n\n{'='*30}\nTotal Score: {total_score}")
        print(f"✓ Team score calculated: {total_score}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to evaluate team: {e}")
        print(f"Error evaluating team: {e}")

# --- UI WIDGETS ---

# Main frame
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

# Title
title_label = Label(main_frame, text="🏏 Fantasy Cricket Team Builder", 
                    font=("Arial", 18, "bold"), fg="blue")
title_label.pack(pady=10)

# Team Name Entry
team_frame = Frame(main_frame)
team_frame.pack(pady=10)
Label(team_frame, text="Team Name:", font=("Arial", 10)).pack(side=LEFT, padx=5)
team_entry = Entry(team_frame, width=30, font=("Arial", 10))
team_entry.pack(side=LEFT, padx=5)

# Category Selection Frame
cat_frame = LabelFrame(main_frame, text="Select Player Category", font=("Arial", 10, "bold"))
cat_frame.pack(pady=10, fill=X, padx=5)

categories = [("Batsmen", "BAT"), ("Bowlers", "BWL"), ("Wicket Keeper", "WK"), ("All Rounder", "AR")]
for text, cat in categories:
    Radiobutton(cat_frame, text=text, variable=cat_var, value=cat, 
                command=lambda c=cat: load_players(c), font=("Arial", 10)).pack(side=LEFT, padx=10)

# Lists Frame
lists_frame = Frame(main_frame)
lists_frame.pack(pady=10, fill=BOTH, expand=True)

# Available Players
left_frame = LabelFrame(lists_frame, text="Available Players", font=("Arial", 10, "bold"))
left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

list_players = Listbox(left_frame, width=30, height=15, font=("Arial", 9))
list_players.pack(side=LEFT, fill=BOTH, expand=True)
list_players.bind("<Double-1>", add_player)

scrollbar_left = Scrollbar(left_frame, command=list_players.yview)
scrollbar_left.pack(side=RIGHT, fill=Y)
list_players.config(yscrollcommand=scrollbar_left.set)

# Selected Team
right_frame = LabelFrame(lists_frame, text="Your Team", font=("Arial", 10, "bold"))
right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5)

list_selected = Listbox(right_frame, width=30, height=15, font=("Arial", 9))
list_selected.pack(side=LEFT, fill=BOTH, expand=True)
list_selected.bind("<Double-1>", remove_player)

scrollbar_right = Scrollbar(right_frame, command=list_selected.yview)
scrollbar_right.pack(side=RIGHT, fill=Y)
list_selected.config(yscrollcommand=scrollbar_right.set)

# Points Section
points_frame = LabelFrame(main_frame, text="Points Status", font=("Arial", 10, "bold"))
points_frame.pack(pady=10, fill=X, padx=5)

lbl_points = Label(points_frame, text="Points Used: 0 | Available: 100", 
                   font=("Arial", 11, "bold"), fg="green")
lbl_points.pack(pady=10)

# Buttons Frame
button_frame = Frame(main_frame)
button_frame.pack(pady=10)

Button(button_frame, text="New Team", width=15, command=new_team, 
       font=("Arial", 10), bg="lightblue").pack(side=LEFT, padx=5)
Button(button_frame, text="Save Team", width=15, command=save_team, 
       font=("Arial", 10), bg="lightgreen").pack(side=LEFT, padx=5)
Button(button_frame, text="Evaluate Score", width=15, command=evaluate_team, 
       font=("Arial", 10), bg="lightyellow").pack(side=LEFT, padx=5)

# Initialize
try:
    ensure_player_data()
    cat_var.set("BAT")
    load_players("BAT")
    print("✓ Application initialized successfully")
except Exception as e:
    messagebox.showerror("Initialization Error", f"Failed to initialize: {e}")
    print(f"Initialization error: {e}")

# Start GUI
root.mainloop()

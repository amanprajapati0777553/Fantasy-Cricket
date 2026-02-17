# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Database file path
db_file = "fantasy_cricket.db"

print("Starting player database setup...\n")

# Try to close any existing connections
try:
    conn_test = sqlite3.connect(db_file)
    conn_test.close()
    print("[INFO] Existing database connection closed")
except:
    pass

# Delete old database
try:
    if os.path.exists(db_file):
        os.remove(db_file)
        print("[SUCCESS] Old database deleted\n")
except Exception as e:
    print(f"[WARNING] Could not delete database: {e}")
    print("[INFO] Continuing anyway...\n")

# Create new database
try:
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Drop existing tables if they exist
    c.execute("DROP TABLE IF EXISTS stats")
    c.execute("DROP TABLE IF EXISTS teams")
    
    # Create fresh tables
    c.execute('''CREATE TABLE stats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  player TEXT UNIQUE,
                  ctg TEXT,
                  value INTEGER,
                  runs INTEGER DEFAULT 0,
                  wickets INTEGER DEFAULT 0)''')
    
    c.execute('''CREATE TABLE teams
                 (name TEXT PRIMARY KEY,
                  players TEXT,
                  points_used INTEGER)''')
    
    conn.commit()
    print("[SUCCESS] Fresh tables created\n")
    
except Exception as e:
    print(f"[ERROR] Creating tables: {e}\n")
    sys.exit(1)

# Player data (NO DUPLICATES)
batsmen = [
    ("Virat Kohli", "BAT", 10),
    ("Rohit Sharma", "BAT", 10),
    ("KL Rahul", "BAT", 9),
    ("Suryakumar Yadav", "BAT", 9),
    ("Ishan Kishan", "BAT", 8),
    ("Shreyas Iyer", "BAT", 8),
    ("Manish Pandey", "BAT", 7),
    ("Shubman Gill", "BAT", 8),
    ("Prithvi Shaw", "BAT", 7),
    ("Ajinkya Rahane", "BAT", 6),
]

bowlers = [
    ("Jasprit Bumrah", "BWL", 10),
    ("Bhuvneshwar Kumar", "BWL", 9),
    ("Yuzvendra Chahal", "BWL", 8),
    ("Ravichandran Ashwin", "BWL", 9),
    ("Axar Patel", "BWL", 8),
    ("Siraj Mohammed", "BWL", 8),
    ("Umran Malik", "BWL", 7),
    ("Deepak Chahar", "BWL", 8),
    ("Navdeep Saini", "BWL", 7),
    ("Prasidh Krishna", "BWL", 7),
]

wicketkeepers = [
    ("MS Dhoni", "WK", 10),
    ("Rishabh Pant", "WK", 9),
    ("Dinesh Karthik", "WK", 8),
    ("Wriddhiman Saha", "WK", 7),
    ("Samson Sanju", "WK", 8),
    ("KS Bharat", "WK", 7),
]

allrounders = [
    ("Hardik Pandya", "AR", 9),
    ("Ravindra Jadeja", "AR", 9),
    ("Mitchell Marsh", "AR", 8),
    ("Washington Sundar", "AR", 7),
    ("Venkatesh Iyer", "AR", 7),
    ("Krunal Pandya", "AR", 7),
    ("Shardul Thakur", "AR", 7),
    ("Sikandar Raza", "AR", 8),
    ("Chris Woakes", "AR", 8),
]

all_players = batsmen + bowlers + wicketkeepers + allrounders

# Insert players
try:
    c.executemany("INSERT INTO stats (player, ctg, value) VALUES (?, ?, ?)", all_players)
    conn.commit()
    print(f"[SUCCESS] Added {len(all_players)} players")
    print(f"  - Batsmen: {len(batsmen)}")
    print(f"  - Bowlers: {len(bowlers)}")
    print(f"  - Wicket Keepers: {len(wicketkeepers)}")
    print(f"  - All Rounders: {len(allrounders)}\n")
    
except Exception as e:
    print(f"[ERROR] Inserting players: {e}\n")
    conn.close()
    sys.exit(1)

# Verify data
try:
    c.execute("SELECT COUNT(*) FROM stats")
    total = c.fetchone()[0]
    print(f"[INFO] Total players in database: {total}\n")
    
    print("=" * 60)
    print("PLAYERS BY CATEGORY")
    print("=" * 60)
    
    categories = [("BATSMEN", "BAT"), ("BOWLERS", "BWL"), 
                  ("WICKET KEEPERS", "WK"), ("ALL ROUNDERS", "AR")]
    
    for cat_name, cat_code in categories:
        c.execute("SELECT player, value FROM stats WHERE ctg=? ORDER BY value DESC", (cat_code,))
        players = c.fetchall()
        print(f"\n[{cat_name}] - {len(players)} players")
        print("-" * 60)
        for idx, (player, value) in enumerate(players, 1):
            print(f"  {idx:2d}. {player:<30} {value} pts")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] DATABASE SETUP COMPLETE!")
    print("=" * 60 + "\n")
    
    conn.close()
    
except Exception as e:
    print(f"[ERROR] Verifying data: {e}\n")
    conn.close()
    sys.exit(1)

print("Now run: python main_app.py\n")
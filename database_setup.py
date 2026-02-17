# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

db_file = "fantasy_cricket.db"

print("Starting database setup...\n")

try:
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Drop old tables
    c.execute("DROP TABLE IF EXISTS stats")
    c.execute("DROP TABLE IF EXISTS teams")
    print("[INFO] Dropped old tables\n")
    
    # Create stats table (6 columns)
    c.execute('''CREATE TABLE stats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  player TEXT UNIQUE,
                  ctg TEXT,
                  value INTEGER,
                  runs INTEGER DEFAULT 0,
                  wickets INTEGER DEFAULT 0)''')
    
    # Create teams table
    c.execute('''CREATE TABLE teams
                 (name TEXT PRIMARY KEY,
                  players TEXT,
                  points_used INTEGER)''')
    
    conn.commit()
    print("[SUCCESS] Tables created\n")
    
    # Player data - 4 values per tuple (player, category, value, runs/wickets)
    stats_data = [
        # Batsmen
        ("Virat Kohli", "BAT", 10, 0),
        ("Rohit Sharma", "BAT", 10, 0),
        ("KL Rahul", "BAT", 9, 0),
        ("Suryakumar Yadav", "BAT", 9, 0),
        ("Ishan Kishan", "BAT", 8, 0),
        ("Shreyas Iyer", "BAT", 8, 0),
        ("Manish Pandey", "BAT", 7, 0),
        ("Shubman Gill", "BAT", 8, 0),
        ("Prithvi Shaw", "BAT", 7, 0),
        ("Ajinkya Rahane", "BAT", 6, 0),
        
        # Bowlers
        ("Jasprit Bumrah", "BWL", 10, 0),
        ("Bhuvneshwar Kumar", "BWL", 9, 0),
        ("Yuzvendra Chahal", "BWL", 8, 0),
        ("Ravichandran Ashwin", "BWL", 9, 0),
        ("Axar Patel", "BWL", 8, 0),
        ("Siraj Mohammed", "BWL", 8, 0),
        ("Umran Malik", "BWL", 7, 0),
        ("Deepak Chahar", "BWL", 8, 0),
        ("Navdeep Saini", "BWL", 7, 0),
        ("Prasidh Krishna", "BWL", 7, 0),
        
        # Wicket Keepers
        ("MS Dhoni", "WK", 10, 0),
        ("Rishabh Pant", "WK", 9, 0),
        ("Dinesh Karthik", "WK", 8, 0),
        ("Wriddhiman Saha", "WK", 7, 0),
        ("Samson Sanju", "WK", 8, 0),
        ("KS Bharat", "WK", 7, 0),
        
        # All Rounders
        ("Hardik Pandya", "AR", 9, 0),
        ("Ravindra Jadeja", "AR", 9, 0),
        ("Mitchell Marsh", "AR", 8, 0),
        ("Washington Sundar", "AR", 7, 0),
        ("Venkatesh Iyer", "AR", 7, 0),
        ("Krunal Pandya", "AR", 7, 0),
        ("Shardul Thakur", "AR", 7, 0),
        ("Sikandar Raza", "AR", 8, 0),
        ("Chris Woakes", "AR", 8, 0),
    ]
    
    # Insert with 4 values (player, ctg, value, runs)
    # id and wickets will use defaults
    c.executemany('''INSERT OR IGNORE INTO stats 
                     (player, ctg, value, runs) 
                     VALUES (?, ?, ?, ?)''', stats_data)
    conn.commit()
    
    # Count inserted
    c.execute("SELECT COUNT(*) FROM stats")
    total = c.fetchone()[0]
    print(f"[SUCCESS] Inserted {total} players\n")
    
    # Show by category
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
    print("=" * 60)
    print("\nNow run: python main_app.py\n")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"[ERROR] Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

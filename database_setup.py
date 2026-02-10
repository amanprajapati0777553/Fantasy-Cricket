import sqlite3

def create_database():
    conn = sqlite3.connect("fantasy_cricket.db")
    c = conn.cursor()

    # --- TABLE: stats ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            player TEXT PRIMARY KEY,
            matches INT,
            runs INT,
            hundreds INT,
            fifties INT,
            value INT,
            ctg TEXT
        )
    """)

    # --- TABLE: match ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS match (
            player TEXT,
            scored INT,
            faced INT,
            fours INT,
            sixes INT,
            bowled INT,
            maiden INT,
            given INT,
            wkts INT,
            catches INT,
            stumping INT,
            runout INT
        )
    """)

    # --- TABLE: teams ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            name TEXT PRIMARY KEY,
            players TEXT,
            value INT
        )
    """)

    # Sample Stats Data
    stats_data = [
        ("Rohit Sharma", 250, 10000, 30, 50, 9, "BAT"),
        ("Virat Kohli", 270, 12000, 45, 60, 10, "BAT"),
        ("Suryakumar Yadav", 80, 1800, 0, 12, 8, "BAT"),
        ("KL Rahul", 120, 4000, 5, 20, 8, "WK"),
        ("Hardik Pandya", 110, 1500, 0, 3, 9, "AR"),
        ("Ravindra Jadeja", 160, 2500, 0, 2, 9, "AR"),
        ("Jasprit Bumrah", 100, 100, 0, 0, 10, "BWL"),
        ("Mohammad Shami", 110, 150, 0, 0, 9, "BWL")
    ]

    c.executemany("INSERT OR IGNORE INTO stats VALUES (?,?,?,?,?,?,?)", stats_data)

    # Sample Match Data for scoring
    match_data = [
        ("Rohit Sharma", 50, 35, 6, 2, 0, 0, 0, 0, 1, 0, 0),
        ("Virat Kohli", 80, 55, 8, 1, 0, 0, 0, 0, 0, 0, 1),
        ("Suryakumar Yadav", 30, 18, 4, 1, 0, 0, 0, 0, 1, 0, 0),
        ("KL Rahul", 45, 40, 5, 0, 0, 0, 0, 0, 2, 1, 0),
        ("Hardik Pandya", 25, 15, 3, 1, 3, 0, 20, 1, 0, 0, 0),
        ("Ravindra Jadeja", 10, 10, 1, 0, 6, 1, 25, 2, 0, 0, 1),
        ("Jasprit Bumrah", 0, 2, 0, 0, 8, 2, 15, 3, 0, 0, 0),
        ("Mohammad Shami", 5, 5, 0, 0, 10, 0, 30, 2, 0, 0, 0)
    ]

    c.executemany("INSERT INTO match VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", match_data)

    conn.commit()
    conn.close()

create_database()
print("Database created successfully!")

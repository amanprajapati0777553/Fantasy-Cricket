import sqlite3

def calculate_score(player):
    conn = sqlite3.connect("fantasy_cricket.db")
    c = conn.cursor()

    c.execute("SELECT * FROM match WHERE player=?", (player,))
    data = c.fetchone()
    conn.close()

    if not data:
        return 0

    (_, scored, faced, fours, sixes, bowled, maiden, given, wkts, catches, stumping, runout) = data

    score = 0

    # Batting
    score += scored // 2
    if scored >= 100:
        score += 10
    elif scored >= 50:
        score += 5

    strike_rate = (scored / faced) * 100 if faced else 0
    if 80 <= strike_rate <= 100:
        score += 2
    elif strike_rate > 100:
        score += 6

    score += (fours * 1)
    score += (sixes * 2)

    # Bowling
    score += (wkts * 10)
    if wkts >= 5:
        score += 10
    elif wkts >= 3:
        score += 5

    if bowled > 0:
        economy = given / (bowled / 6)
        if 3.5 <= economy <= 4.5:
            score += 4
        elif 2 <= economy < 3.5:
            score += 7
        elif economy < 2:
            score += 10

    # Fielding
    score += catches * 10
    score += stumping * 10
    score += runout * 10

    return score

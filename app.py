from flask import Flask, render_template, request, jsonify, session
import sqlite3
import json
from datetime import datetime
from scoring_engine import calculate_score

app = Flask(__name__)
app.secret_key = 'fantasy_cricket_secret_2026'

# Database connection
def get_db():
    conn = sqlite3.connect("fantasy_cricket.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_player_value(player_name):
    """Return integer value for a player (safe conversion)."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT value FROM stats WHERE player=?", (player_name,))
    row = c.fetchone()
    conn.close()
    
    if row:
        try:
            return int(row[0])
        except (ValueError, TypeError):
            try:
                return int(float(row[0]))
            except:
                return 0 
    return 0

@app.route('/')
def index():
    """Home page - Team Builder"""
    return render_template('index.html')

@app.route('/api/players/<category>')
def get_players(category):
    """Get players by category"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT player FROM stats WHERE ctg=? ORDER BY player", (category,))
    players = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(players)

@app.route('/api/player-value/<player_name>')
def get_player_info(player_name):
    """Get player value and stats"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT player, ctg, value, runs, wickets FROM stats WHERE player=?", (player_name,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'name': row[0],
            'category': row[1],
            'value': int(row[2]),
            'runs': int(row[3]) if row[3] else 0,
            'wickets': int(row[4]) if row[4] else 0
        })
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get all saved teams"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name, players, points_used FROM teams ORDER BY rowid DESC")
    teams = []
    for row in c.fetchall():
        players = row[1].split(',') if row[1] else []
        teams.append({
            'id': row[0],
            'name': row[0],
            'players': players,
            'points_used': row[2],
            'created_at': datetime.now().isoformat()
        })
    conn.close()
    return jsonify(teams)

@app.route('/api/team/save', methods=['POST'])
def save_team():
    """Save a new team"""
    data = request.get_json()
    team_name = data.get('team_name')
    players = data.get('players', [])
    
    if not team_name:
        return jsonify({'error': 'Team name required'}), 400
    
    if not players:
        return jsonify({'error': 'Add at least one player'}), 400
    
    # Calculate points used
    points_used = sum(get_player_value(p) for p in players)
    
    if points_used > 100:
        return jsonify({'error': 'Team exceeds 100 points'}), 400
    
    try:
        conn = get_db()
        c = conn.cursor()
        players_str = ",".join(players)
        c.execute("INSERT OR REPLACE INTO teams VALUES (?,?,?)", 
                 (team_name, players_str, points_used))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Team saved successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team/delete/<team_name>', methods=['DELETE'])
def delete_team(team_name):
    """Delete a team"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM teams WHERE name=?", (team_name,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Team deleted successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team/score/<team_name>')
def evaluate_team_score(team_name):
    """Calculate team score"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT players FROM teams WHERE name=?", (team_name,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Team not found'}), 404
        
        players = row[0].split(',') if row[0] else []
        
        if not players:
            return jsonify({'error': 'Team has no players'}), 400
        
        total_score = 0
        player_scores = {}
        
        for player in players:
            score = calculate_score(player)
            player_scores[player] = score
            total_score += score
        
        return jsonify({
            'team_name': team_name,
            'total_score': total_score,
            'player_scores': player_scores,
            'player_count': len(players)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def get_categories():
    """Get all player categories"""
    categories = [
        {'id': 'BAT', 'name': 'Batsmen', 'icon': '🏏'},
        {'id': 'BWL', 'name': 'Bowlers', 'icon': '⚡'},
        {'id': 'WK', 'name': 'Wicket Keeper', 'icon': '🧤'},
        {'id': 'AR', 'name': 'All Rounder', 'icon': '⚙️'}
    ]
    return jsonify(categories)

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print("[INFO] Starting Fantasy Cricket Flask App")
    print("[INFO] Database: fantasy_cricket.db")
    print("[INFO] Running on http://localhost:5000")
    print("[INFO] Press Ctrl+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
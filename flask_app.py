import os
import requests
from flask import Flask, render_template, jsonify, request
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

# Initialiser la base de données SQLite au démarrage
if not os.path.exists(storage.DB_FILE):
    storage.init_db()

# Au démarrage, on récupère la liste des magasins (Steam, Epic, GOG...) pour traduire les ID
STORES_MAP = {}
try:
    r = requests.get("https://www.cheapshark.com/api/1.0/stores")
    if r.status_code == 200:
        for store in r.json():
            STORES_MAP[store['storeID']] = store['storeName']
except:
    pass

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    runs = storage.get_runs()
    return render_template('dashboard.html', runs=runs)

@app.route('/search', methods=['GET', 'POST'])
def search_games():
    games = []
    if request.method == 'POST':
        title = request.form.get('title')
        try:
            # On cherche des JEUX uniques, pas des deals en vrac
            r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"title": title, "limit": 20})
            if r.status_code == 200:
                games = r.json()
        except:
            pass

    return render_template('search.html', games=games)

@app.route('/game/<game_id>')
def game_details(game_id):
    # Nouvelle route : Récupère toutes les offres pour un jeu précis
    game_data = None
    try:
        r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"id": game_id})
        if r.status_code == 200:
            game_data = r.json()
    except:
        pass
    
    return render_template('game_details.html', game=game_data, stores=STORES_MAP)

@app.route('/run')
def trigger_run():
    summary = run_all_tests()
    return jsonify(summary)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "api": "CheapShark Testing App"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

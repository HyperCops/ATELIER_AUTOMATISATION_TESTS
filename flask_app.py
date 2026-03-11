import os
import requests
from flask import Flask, render_template, jsonify, request
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

if not os.path.exists(storage.DB_FILE):
    storage.init_db()

STORES_MAP = {}

try:
    r = requests.get("https://www.cheapshark.com/api/1.0/stores", timeout=5)
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
    trending_deals = []
    
    if request.method == 'POST':
        title = request.form.get('title')
        try:
            r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"title": title, "limit": 20}, timeout=5)
            if r.status_code == 200:
                games = r.json()
        except:
            pass
    else:
        # NOUVEAU : Si aucune recherche, on récupère les meilleures promos du moment !
        try:
            r = requests.get("https://www.cheapshark.com/api/1.0/deals", params={"sortBy": "Deal Rating", "limit": 8}, timeout=5)
            if r.status_code == 200:
                trending_deals = r.json()
        except:
            pass

    return render_template('search.html', games=games, trending=trending_deals)

@app.route('/game/<game_id>')
def game_details(game_id):
    game_data = None
    steam_data = None
    
    try:
        r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"id": game_id}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data: 
                game_data = data
                steam_id = game_data.get('info', {}).get('steamAppID')
                if steam_id:
                    steam_id_str = str(steam_id) 
                    r_steam = requests.get(f"https://store.steampowered.com/api/appdetails?appids={steam_id_str}", timeout=3)
                    
                    if r_steam.status_code == 200:
                        steam_json = r_steam.json()
                        if steam_json and steam_json.get(steam_id_str, {}).get('success'):
                            steam_data = steam_json.get(steam_id_str, {}).get('data')
    except Exception as e:
        print(f"Erreur : {e}")
    
    return render_template('game_details.html', game=game_data, stores=STORES_MAP, steam_data=steam_data)

@app.route('/run')
def trigger_run():
    summary = run_all_tests()
    return jsonify(summary)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "api": "CheapShark App"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

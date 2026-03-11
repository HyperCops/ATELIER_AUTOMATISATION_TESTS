import os
import requests
from flask import Flask, render_template, jsonify, request
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

if not os.path.exists(storage.DB_FILE):
    storage.init_db()

STORES_MAP = {}
EXCHANGE_RATE = 0.92 

try:
    r = requests.get("https://www.cheapshark.com/api/1.0/stores", timeout=5)
    if r.status_code == 200:
        for store in r.json():
            STORES_MAP[store['storeID']] = store['storeName']
except:
    pass

try:
    r_rate = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
    if r_rate.status_code == 200:
        EXCHANGE_RATE = r_rate.json()['rates']['EUR']
except:
    pass

@app.template_filter('to_eur')
def to_eur_filter(usd_price):
    try:
        eur_price = float(usd_price) * EXCHANGE_RATE
        return f"{eur_price:.2f}"
    except:
        return usd_price

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
            r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"title": title, "limit": 20}, timeout=5)
            if r.status_code == 200:
                games = r.json()
        except:
            pass
    return render_template('search.html', games=games)

@app.route('/game/<game_id>')
def game_details(game_id):
    game_data = None
    steam_data = None
    
    try:
        r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"id": game_id}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data: # On s'assure que Cheapshark a bien trouvé le jeu
                game_data = data
                
                # Récupération sécurisée de l'ID Steam
                steam_id = game_data.get('info', {}).get('steamAppID')
                if steam_id:
                    steam_id_str = str(steam_id) # On force en format texte pour éviter les bugs JSON
                    r_steam = requests.get(f"https://store.steampowered.com/api/appdetails?appids={steam_id_str}", timeout=3)
                    
                    if r_steam.status_code == 200:
                        steam_json = r_steam.json()
                        # On vérifie que la requête Steam a réussi avant d'extraire les datas
                        if steam_json and steam_json.get(steam_id_str, {}).get('success'):
                            steam_data = steam_json.get(steam_id_str, {}).get('data')
    except Exception as e:
        print(f"Erreur de chargement du jeu : {e}")
    
    return render_template('game_details.html', game=game_data, stores=STORES_MAP, steam_data=steam_data)

@app.route('/run')
def trigger_run():
    summary = run_all_tests()
    return jsonify(summary)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "api": "CheapShark Testing App"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import os
import requests
from flask import Flask, render_template, jsonify, request
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

# Initialiser la base de données SQLite au démarrage
if not os.path.exists(storage.DB_FILE):
    storage.init_db()

# --- 1. INITIALISATION DES DONNÉES GLOBALES ---
STORES_MAP = {}
EXCHANGE_RATE = 0.92 # Taux par défaut (au cas où l'API de change plante)

# Récupération des magasins
try:
    r = requests.get("https://www.cheapshark.com/api/1.0/stores", timeout=5)
    if r.status_code == 200:
        for store in r.json():
            STORES_MAP[store['storeID']] = store['storeName']
except:
    pass

# Récupération du taux de change direct USD -> EUR
try:
    r_rate = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
    if r_rate.status_code == 200:
        EXCHANGE_RATE = r_rate.json()['rates']['EUR']
except:
    pass

# --- 2. FILTRE JINJA POUR LA CONVERSION EN EUROS ---
@app.template_filter('to_eur')
def to_eur_filter(usd_price):
    try:
        eur_price = float(usd_price) * EXCHANGE_RATE
        return f"{eur_price:.2f}"
    except:
        return usd_price

# --- 3. ROUTES DE L'APPLICATION ---
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
            r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"title": title, "limit": 20})
            if r.status_code == 200:
                games = r.json()
        except:
            pass

    return render_template('search.html', games=games)

@app.route('/game/<game_id>')
def game_details(game_id):
    game_data = None
    steam_data = None # Pour stocker les images et le trailer
    try:
        # Récupération des infos CheapShark
        r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"id": game_id})
        if r.status_code == 200:
            game_data = r.json()
            
            # Si le jeu a un ID Steam, on va chercher le trailer et les images chez Steam !
            steam_id = game_data.get('info', {}).get('steamAppID')
            if steam_id:
                r_steam = requests.get(f"https://store.steampowered.com/api/appdetails?appids={steam_id}", timeout=3)
                if r_steam.status_code == 200:
                    steam_json = r_steam.json()
                    # L'API Steam est un peu spéciale, il faut vérifier que le "success" est à True
                    if steam_json.get(steam_id, {}).get('success'):
                        steam_data = steam_json[steam_id]['data']
    except:
        pass
    
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

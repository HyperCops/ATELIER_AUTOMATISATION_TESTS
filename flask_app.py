import os
import requests
import traceback
from flask import Flask, render_template, jsonify, request
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

if not os.path.exists(storage.DB_FILE):
    storage.init_db()

STORES_MAP = {}
# On se fait passer pour un vrai navigateur web (Chrome/Mac) pour éviter d'être bloqué par l'API
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

try:
    r = requests.get("https://www.cheapshark.com/api/1.0/stores", headers=HEADERS, timeout=5)
    if r.status_code == 200:
        for store in r.json():
            STORES_MAP[store['storeID']] = store['storeName']
except:
    pass

@app.route("/")
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h3 style='color:red;'>Erreur Accueil : {e}</h3>"

@app.route('/dashboard')
def dashboard():
    runs = storage.get_runs()
    return render_template('dashboard.html', runs=runs)

@app.route('/search', methods=['GET', 'POST'])
def search_games():
    try:
        deals = []
        trending_deals = []
        api_error = ""
        is_post = (request.method == 'POST')
        
        if is_post:
            # Nettoyage des paramètres vides pour ne pas faire planter l'API
            title = request.form.get('title', '').strip()
            max_price = request.form.get('max_price', '').strip()
            store_id = request.form.get('store_id', '').strip()
            sort_by = request.form.get('sort_by', '').strip()
            min_metacritic = request.form.get('min_metacritic', '').strip()
            
            params = {"limit": 24}
            if title: params['title'] = title
            if max_price: params['upperPrice'] = max_price
            if store_id: params['storeID'] = store_id
            if sort_by: params['sortBy'] = sort_by
            if min_metacritic: params['metacritic'] = min_metacritic
            
            r = requests.get("https://www.cheapshark.com/api/1.0/deals", params=params, headers=HEADERS, timeout=5)
            if r.status_code == 200:
                deals = r.json()
            else:
                api_error = f"Erreur Recherche API ({r.status_code})"

        # Si c'est un accès normal (GET) OU si la recherche n'a rien donné, on charge les tendances
        if not is_post or not deals:
            r_trend = requests.get("https://www.cheapshark.com/api/1.0/deals", params={"sortBy": "Deal Rating", "limit": 8}, headers=HEADERS, timeout=5)
            if r_trend.status_code == 200:
                trending_deals = r_trend.json()
            else:
                api_error += f" Erreur Tendances API ({r_trend.status_code})"

        return render_template('search.html', deals=deals, trending=trending_deals, stores=STORES_MAP, api_error=api_error, is_post=is_post)
    
    except Exception as e:
        error_trace = traceback.format_exc()
        return f"<h3>Erreur Python dans la recherche :</h3><pre>{error_trace}</pre>"

@app.route('/game/<game_id>')
def game_details(game_id):
    try:
        game_data = None
        steam_data = None
        
        r = requests.get("https://www.cheapshark.com/api/1.0/games", params={"id": game_id}, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data: 
                game_data = data
                steam_id = game_data.get('info', {}).get('steamAppID')
                if steam_id:
                    steam_id_str = str(steam_id) 
                    r_steam = requests.get(f"https://store.steampowered.com/api/appdetails?appids={steam_id_str}", headers=HEADERS, timeout=3)
                    if r_steam.status_code == 200:
                        steam_json = r_steam.json()
                        if

import os
import requests
from flask import Flask, render_template, jsonify, request
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

if not os.path.exists(storage.DB_FILE):
    storage.init_db()

STORES_MAP = {}

# Récupération des magasins au démarrage (utile pour les filtres)
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
    deals = []
    trending_deals = []
    
    if request.method == 'POST':
        # --- NOUVEAU : Récupération des Filtres Avancés ---
        title = request.form.get('title')
        max_price = request.form.get('max_price')
        store_id = request.form.get('store_id')
        sort_by = request.form.get('sort_by')
        min_metacritic = request.form.get('min_metacritic')
        
        # Construction des paramètres pour l'API
        params = {"limit": 24} # On affiche 24 résultats max
        if title: params['title'] = title
        if max_price: params['upperPrice'] = max_price
        if store_id: params['storeID'] = store_id
        if sort_by: params['sortBy'] = sort_by
        if min_metacritic: params['metacritic'] = min_metacritic
        
        try:
            # On utilise maintenant /deals pour profiter des filtres et des notes
            r = requests.get("https://www.cheapshark.com/api/1.0/deals", params=params, timeout=5)
            if r.status_code == 200:
                deals = r.json()
        except:
            pass
    else:
        # Offres populaires par défaut
        try:
            r = requests.get("https://www.cheapshark.com/api/1.0/deals", params={"sortBy": "Deal Rating", "limit": 8}, timeout=5)
            if r.status_code == 200:
                trending_deals = r.json()
        except:
            pass

import os
import requests
import traceback
from flask import Flask, render_template, jsonify, request
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

# Initialisation sécurisée de la BDD
try:
    if not os.path.exists(storage.DB_FILE):
        storage.init_db()
except Exception as e:
    print(f"Erreur initialisation DB: {e}")

STORES_MAP = {}

# Récupération sécurisée des magasins
try:
    r = requests.get("https://www.cheapshark.com/api/1.0/stores", timeout=5)
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
        # Au lieu de planter avec une Erreur 500, on affiche le problème !
        return f"""
        <h3 style='color:red;'>Erreur sur la page d'accueil !</h3>
        <p><b>Détail de l'erreur :</b> {e}</p>
        <p><b>Solution :</b> Vérifiez que vous avez bien créé un fichier nommé exactement <code>index.html</code> (tout en minuscules) et qu'il est bien placé à l'intérieur du dossier <code>templates/</code>.</p>
        """

@app.route('/dashboard')
def dashboard():
    try:
        runs = storage.get_runs()
        return render_template('dashboard.html', runs=runs)
    except Exception as e:
        return f"<h3>Erreur Dashboard :</h3><p>{e}</p>"

@app.route('/search', methods=['GET', 'POST'])
def search_games():
    try:
        deals = []
        trending_deals = []
        
        if request.method == 'POST':
            title = request.form.get('title')
            max_price = request.form.get('max_price')
            store_id = request.form.get('store_id')
            sort_by = request.form.get('sort_by')
            min_metacritic = request.form.get('min_metacritic')
            
            params = {"limit": 24}
            if title: params['title'] = title
            if max_price: params['upperPrice'] = max_price
            if store_id: params['storeID'] = store_id
            if sort_by: params['sortBy'] = sort_by
            if min_metacritic: params['metacritic'] = min_metacritic
            
            try:
                r = requests.get("https://www.cheapshark.com/api/1.0/deals", params=params, timeout=5)
                if r.status_code == 200:
                    deals = r.json()
            except:
                pass
        else:
            try:
                r = requests.get("https://www.cheapshark.com/api/1.0/deals", params={"sortBy": "Deal Rating", "limit": 8}, timeout=5)
                if r.status_code == 200:
                    trending_deals = r.json()
            except:
                pass

        return render_template('search.html', deals=deals, trending=trending_deals, stores=STORES_MAP)
    
    except Exception as e:
        error_trace = traceback.format_exc()
        return f"<h3>Erreur dans la recherche :</h3><pre>{error_trace}</pre>"

@app.route('/game/<game_id>')
def game_details(game_id):
    try:
        game_data = None
        steam_data = None
        
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
        
        return render_template('game_details.html', game=game_data, stores=STORES_MAP, steam_data=steam_data)
    except Exception as e:
        return f"<h3>Erreur sur les détails du jeu :</h3><p>{e}</p>"

@app.route('/run')
def trigger_run():
    summary = run_all_tests()
    return jsonify(summary)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "api": "CheapShark App"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

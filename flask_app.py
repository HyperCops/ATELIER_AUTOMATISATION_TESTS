import os
import requests
from flask import Flask, render_template, jsonify, request
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

# Initialiser la base de données SQLite au démarrage si elle n'existe pas
if not os.path.exists(storage.DB_FILE):
    storage.init_db()

@app.route("/")
def home():
    # Page d'accueil avec tous les liens
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Route pour afficher les résultats de tests
    runs = storage.get_runs()
    return render_template('dashboard.html', runs=runs)

@app.route('/search', methods=['GET', 'POST'])
def search_games():
    # Nouvelle route pour chercher des jeux manuellement !
    deals = []
    if request.method == 'POST':
        title = request.form.get('title')
        max_price = request.form.get('max_price')
        
        # On prépare les paramètres pour l'API CheapShark
        params = {}
        if title: params['title'] = title
        if max_price: params['upperPrice'] = max_price
        
        try:
            # On appelle l'API en direct pour l'utilisateur
            r = requests.get("https://www.cheapshark.com/api/1.0/deals", params=params)
            if r.status_code == 200:
                deals = r.json()
        except:
            pass # En cas d'erreur de connexion, on renvoie une liste vide

    return render_template('search.html', deals=deals)

@app.route('/run')
def trigger_run():
    # Déclenche un test manuel et renvoie du JSON
    summary = run_all_tests()
    return jsonify(summary)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "api": "CheapShark Testing App"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

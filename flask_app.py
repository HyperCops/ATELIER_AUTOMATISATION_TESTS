import os
from flask import Flask, render_template, jsonify
# On importe les modules de ton projet que tu as créés
import storage
from tester.runner import run_all_tests

app = Flask(__name__)

# Initialiser la base de données SQLite au démarrage si elle n'existe pas
if not os.path.exists(storage.DB_FILE):
    storage.init_db()

@app.get("/")
def consignes():
    # Route pour afficher tes consignes
    return render_template('consignes.html')

@app.route('/dashboard')
def dashboard():
    # Route pour afficher les résultats
    runs = storage.get_runs()
    return render_template('dashboard.html', runs=runs)

@app.route('/run')
def trigger_run():
    # Déclenche un test manuel et renvoie du JSON (Bonus export téléchargeable)
    summary = run_all_tests()
    return jsonify(summary)

@app.route('/health')
def health():
    # Bonus Endpoint /health
    return jsonify({"status": "ok", "api": "CheapShark Testing App"})

if __name__ == "__main__":
    # Utile en local uniquement pour tester sur ta machine
    app.run(host="0.0.0.0", port=5000, debug=True)

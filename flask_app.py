from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)

@app.get("/")
def consignes():
     return render_template('consignes.html')

@app.route('/dashboard')
def dashboard():
    runs = storage.get_runs()
    return render_template('dashboard.html', runs=runs)

@app.route('/run')
def trigger_run():
    # Déclenche un test, renvoie du JSON (Bonus export téléchargeable)
    summary = run_all_tests()
    return jsonify(summary)

@app.route('/health')
def health():
    # Bonus Endpoint /health
    return jsonify({"status": "ok", "api": "CheapShark Testing App"})

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)

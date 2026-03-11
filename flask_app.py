<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Recherche de Jeux Avancée</title>
    <link href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.0/dist/darkly/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: radial-gradient(circle at top, #2b2b45, #12121c);
            background-attachment: fixed;
            min-height: 100vh;
        }
        .navbar {
            background: rgba(26, 26, 46, 0.9) !important;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .game-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        .game-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.6);
            border-color: #0dcaf0;
        }
        .hero-banner {
            background: linear-gradient(135deg, rgba(13,202,240,0.1) 0%, rgba(26,26,46,0) 100%);
            border-radius: 15px;
            padding: 30px;
            border: 1px solid rgba(13,202,240,0.2);
        }
        .score-badge {
            font-size: 0.8rem;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        }
    </style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
  <div class="container">
    <a class="navbar-brand fw-bold" href="/">🦈 CheapShark App</a>
    <div class="navbar-nav">
        <a class="nav-link" href="/">Accueil</a>
        <a class="nav-link active" href="/search">Recherche</a>
        <a class="nav-link" href="/dashboard">Dashboard Tests</a>
    </div>
  </div>
</nav>

<div class="container pb-5">

    {% if api_error %}
        <div class="alert alert-danger shadow-sm mb-4">
            <strong>Attention :</strong> Problème de communication avec CheapShark ({{ api_error }}). Les données peuvent être incomplètes.
        </div>
    {% endif %}
    
    <div class="hero-banner mb-5">
        <h3 class="mb-4 text-info fw-bold text-center">Recherche Avancée</h3>
        <form method="POST" action="/search" class="row g-3">
            <div class="col-md-12">
                <input type="text" name="title" class="form-control form-control-lg bg-dark text-light border-secondary" placeholder="Titre du jeu (ex: Batman, Elden Ring)...">
            </div>
            <div class="col-md-3">
                <label class="form-label text-muted small">Prix Max ($)</label>
                <input type="number" step="1" name="max_price" class="form-control bg-dark text-light border-secondary" placeholder="ex: 15">
            </div>
            <div class="col-md-3">
                <label class="form-label text-muted small">Boutique</label>
                <select name="store_id" class="form-select bg-dark text-light border-secondary">
                    <option value="">Toutes les boutiques</option>
                    {% for sid, sname in stores.items() %}
                        <option value="{{ sid }}">{{ sname }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label text-muted small">Trier par</label>
                <select name="sort_by" class="form-select bg-dark text-light border-secondary">
                    <option value="Deal Rating">Meilleure offre (Défaut)</option>
                    <option value="Price">Prix le plus bas</option>
                    <option value="Savings">Plus grosse réduction</option>
                    <option value="Metacritic">Note Metacritic</option>
                    <option value="Release">Date de sortie</option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label text-muted small">Score Metacritic Min.</label>
                <input type="number" name="min_metacritic" class="form-control bg-dark text-light border-secondary" placeholder="ex: 80">
            </div>
            <div class="col-md-12 text-center mt-4">
                <button type="submit" class="btn btn-info btn-lg fw-bold px-5">Filtrer les offres</button>
            </div>
        </form>
    </div>

    {% set results = deals if deals else trending %}

    {% if results %}
        <h4 class="mb-4 border-bottom border-secondary pb-2">
            {% if is_post and deals %} Résultats de la recherche ({{ deals|length }}) {% else %} 🔥 Offres populaires du moment {% endif %}
        </h4>
        
        <div class="row">
            {% for deal in results %}
            <div class="col-md-3 mb-4">
                <div class="card h-100 game-card text-center position-relative">
                    
                    {% set savings = deal.get('savings') %}
                    {% if savings and savings != '0.000000' %}
                        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger fs-6 border border-dark">
                            -{{ (savings|string).split('.')[0] }}%
                        </span>
                    {% endif %}

                    <img src="{{ deal.get('thumb', '') }}" class="card-img-top mx-auto mt-3 rounded" alt="Cover" style="height: 120px; width: auto; max-width: 90%; object-fit: contain;">
                    
                    <div class="card-body d-flex flex-column">
                        <h6 class="card-title text-light mb-3">{{ deal.get('title', 'Titre inconnu') }}</h6>
                        
                        <div class="mb-3">
                            {% if deal.get('metacriticScore') and deal.get('metacriticScore') != '0' %}
                                {% set meta = deal.get('metacriticScore')|int %}
                                {% set m_color = 'success' if meta >= 80 else ('warning' if meta >= 60 else 'danger') %}
                                <span class="badge bg-{{ m_color }} score-badge me-1" title="Note Metacritic">Ⓜ️ {{ meta }}</span>
                            {% endif %}
                            
                            {% if deal.get('steamRatingPercent') and deal.get('steamRatingPercent') != '0' %}
                                {% set steam = deal.get('steamRatingPercent')|int %}
                                {% set s_color = 'success' if steam >= 80 else ('warning' if steam >= 60 else 'danger') %}
                                <span class="badge bg-{{ s_color }} score-badge" title="Avis positifs Steam">💨 {{ steam }}%</span>
                            {% endif %}
                        </div>

                        <div class="

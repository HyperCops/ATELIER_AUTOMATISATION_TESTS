def test_deals_status_200(client):
    """Test 1: HTTP 200 attendu sur /deals"""
    res, lat, err = client.get("/deals", params={"storeID": "1"})
    assert err is None, f"Erreur réseau: {err}"
    assert res.status_code == 200, f"Code inattendu: {res.status_code}"
    return lat, res

def test_deals_content_type(client):
    """Test 2: Content-Type JSON"""
    res, lat, err = client.get("/deals", params={"storeID": "1"})
    assert "application/json" in res.headers.get("Content-Type", ""), "Pas du JSON"
    return lat, res

def test_deals_schema(client):
    """Test 3: Champs obligatoires présents"""
    res, lat, err = client.get("/deals", params={"storeID": "1"})
    data = res.json()
    assert len(data) > 0, "La liste est vide"
    first_deal = data[0]
    for champ in ["dealID", "title", "salePrice"]:
        assert champ in first_deal, f"Champ manquant: {champ}"
    return lat, res

def test_deals_types(client):
    """Test 4: Vérification des types (string/float)"""
    res, lat, err = client.get("/deals", params={"storeID": "1"})
    first_deal = res.json()[0]
    assert isinstance(first_deal["title"], str), "title n'est pas un string"
    # L'API renvoie des strings pour les prix, on vérifie si c'est castable en float
    try:
        float(first_deal["salePrice"])
    except ValueError:
        raise AssertionError("salePrice ne peut pas être casté en float")
    return lat, res

def test_game_missing_id_400(client):
    """Test 5: Cas d'entrée invalide (400 Bad Request attendu)"""
    res, lat, err = client.get("/games") # Pas d'ID fourni
    assert res.status_code == 400, f"On attendait 400, on a eu {res.status_code}"
    return lat, res

def test_invalid_endpoint_404(client):
    """Test 6: Endpoint inexistant (404 Not Found)"""
    res, lat, err = client.get("/nexiste_pas_12345")
    assert res.status_code == 404, f"On attendait 404, on a eu {res.status_code}"
    return lat, res

def test_functional_upper_price(client):
    """Test 7: Fonctionnel - Le filtre 'upperPrice' fonctionne-t-il ?"""
    res, lat, err = client.get("/deals", params={"upperPrice": "5"})
    assert res.status_code == 200, "L'API n'a pas répondu 200"
    
    deals = res.json()
    assert len(deals) > 0, "Aucun deal retourné"
    
    for deal in deals:
        prix = float(deal["salePrice"])
        assert prix <= 5.0, f"Erreur métier: un jeu à {prix}$ a été retourné alors que la limite est de 5$"
    return lat, res

def test_functional_game_lookup(client):
    """Test 8: Fonctionnel - Les données d'un jeu spécifique sont-elles exactes ?"""
    # L'ID 612 correspond à 'Batman: Arkham Asylum'
    res, lat, err = client.get("/games", params={"id": "612"})
    assert res.status_code == 200, "L'API n'a pas répondu 200"
    
    data = res.json()
    titre = data.get("info", {}).get("title", "")
    assert "Batman" in titre, f"Erreur métier: Le jeu attendu était Batman, on a reçu {titre}"
    return lat, res

def test_functional_store_filter(client):
    """Test 9: Fonctionnel - Le filtre par magasin (storeID) est-il respecté ?"""
    res, lat, err = client.get("/deals", params={"storeID": "1"})
    assert res.status_code == 200, "L'API n'a pas répondu 200"
    
    deals = res.json()
    assert len(deals) > 0, "Aucun deal retourné"
    
    for deal in deals:
        assert deal["storeID"] == "1", f"Erreur métier: Un deal du store {deal['storeID']} a fuité"
    return lat, res

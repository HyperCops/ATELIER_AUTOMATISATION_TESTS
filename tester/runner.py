from tester.client import APIClient
import tester.tests as tests
import storage

def calculate_p95(latencies):
    if not latencies: return 0.0
    s_lats = sorted(latencies)
    idx = int(0.95 * len(s_lats))
    return round(s_lats[idx], 3)

def run_all_tests():
    client = APIClient()
    
    # Liste des tests à exécuter
    test_funcs = [
        tests.test_deals_status_200,
        tests.test_deals_content_type,
        tests.test_deals_schema,
        tests.test_deals_types,
        tests.test_game_missing_id_400,
        tests.test_invalid_endpoint_404
    ]
    
    results = []
    latencies = []
    failed = 0
    errors_5xx = 0 # Pour le calcul du taux d'erreur

    for func in test_funcs:
        try:
            lat, res = func(client)
            latencies.append(lat)
            results.append({"test": func.__name__, "status": "PASS", "latency": lat})
            if res and res.status_code >= 500:
                errors_5xx += 1
        except Exception as e:
            failed += 1
            results.append({"test": func.__name__, "status": "FAIL", "error": str(e)})

    total = len(test_funcs)
    passed = total - failed
    avg_latency = round(sum(latencies) / len(latencies), 3) if latencies else 0.0
    p95_latency = calculate_p95(latencies)
    
    # Taux d'erreur (requêtes ayant échouées ou renvoyé 5xx)
    error_rate = round(((failed + errors_5xx) / total) * 100, 2)
    # Disponibilité du dernier run (API joignable et répondant aux attentes minimales)
    is_available = (error_rate < 50) 

    stats = {
        "total": total, "passed": passed, "failed": failed,
        "avg_latency": avg_latency, "p95_latency": p95_latency,
        "error_rate": error_rate, "is_available": is_available
    }
    
    # Sauvegarder dans SQLite
    storage.save_run(stats)
    
    return {"stats": stats, "details": results}

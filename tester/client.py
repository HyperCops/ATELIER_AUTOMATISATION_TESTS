import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIClient:
    def __init__(self, base_url="https://www.cheapshark.com/api/1.0"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Robustesse : 1 retry max, gestion des 429 (rate limit) et 5xx (serveur) avec backoff
        retry = Retry(total=1, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def get(self, endpoint, params=None, timeout=3.0):
        start = time.time()
        try:
            # Robustesse : Timeout de 3 secondes
            response = self.session.get(f"{self.base_url}{endpoint}", params=params, timeout=timeout)
            latence = time.time() - start
            return response, latence, None
        except requests.exceptions.RequestException as e:
            latence = time.time() - start
            return None, latence, str(e)

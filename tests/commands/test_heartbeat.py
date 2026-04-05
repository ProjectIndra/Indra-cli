import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")

def test_heartbeat_api():
    """
    Test hitting the root of the real backend server to verify it is online.
    """
    url = f"{BASE_URL}/"
    try:
        response = requests.get(url, timeout=5)
        # Assuming the backend returns 200 OK on its root ping endpoint
        response.raise_for_status()
        assert response.status_code == 200
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Heartbeat to {BASE_URL} failed: {e}")

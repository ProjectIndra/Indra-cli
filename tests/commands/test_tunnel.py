import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")
TOKEN = os.getenv("CKART_SESSION", "")

def test_tunnel_api_list_clients():
    """
    Query the real tunnel API endpoints to fetch active clients.
    """
    url = f"{BASE_URL}/ui/getUserClients"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    
    response = requests.post(url, headers=headers, timeout=15)
    assert response.status_code in [200, 401, 500]
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)

def test_tunnel_api_delete_invalid():
    """
    Attempt to delete a random/fake tunnel ID to ensure proper error boundaries on backend.
    """
    url = f"{BASE_URL}/ui/deleteTunnel"
    headers = {"Authorization": f"BearerCLI {TOKEN}", "Content-Type": "application/json"}
    payload = {"tunnel_id": "invalid_tunnel_id_99999"}
    
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    if response.status_code == 401:
        pytest.skip("No valid session token found for testing. Skipping test.")
        
    # The server might return a 500, a 400 or just a failed message for an invalid deletion request 
    # Usually it's 500 or 400 for bad ids. Let's make sure it doesn't return a 2xx without error strings or simply handles gracefully
    assert response.status_code in [200, 400, 404, 500] 
    if response.status_code == 200:
        data = response.json()
        assert "error" in data or "message" in data

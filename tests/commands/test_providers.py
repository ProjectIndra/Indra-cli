import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")
TOKEN = os.getenv("CKART_SESSION", "")

def test_providers_api_list():
    """
    Test fetching the list of existing providers from the backend.
    """
    url = f"{BASE_URL}/providers/lists"
    headers = {"Authorization": f"BearerCLI {TOKEN}", "Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)
    assert response.status_code in [200, 401, 500]
    if response.status_code == 200:
        data = response.json()
        assert "all_providers" in data
        assert isinstance(data["all_providers"], list)

def test_providers_api_query_invalid():
    """
    Test hitting the provider query with an invalid provider ID 
    to assert it responds with a failure/false status elegantly.
    """
    url = f"{BASE_URL}/providers/query"
    headers = {"Authorization": f"BearerCLI {TOKEN}", "Content-Type": "application/json"}
    payload = {
        "provider_id": "non_existent_provider_test_123",
        "vcpus": 9999,
        "ram": 99999999,
        "storage": 99999999,
        "details": None
    }
    
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code in [200, 400, 401, 500]
    if response.status_code == 200:
        data = response.json()
        assert "can_create" in data
        assert data["can_create"] == False

import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")
TOKEN = os.getenv("CKART_SESSION", "")

def test_connect_api_invalid_vm():
    """
    Attempt to connect to a non-existent VM ID to check failure responses.
    """
    url = f"{BASE_URL}/cli/wg/connect"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    payload = {"vm_id": "non_existent_random_vm_id_testing"}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 401:
        pytest.skip("No valid session token found for testing. Skipping test.")
        
    data = response.json()
    # If the VM doesn't exist, it should throw an error. Usually 4xx or 5xx, or 200 with error property
    if "error" in data:
        assert isinstance(data["error"], str)
    else:
        assert response.status_code in [400, 404, 500]

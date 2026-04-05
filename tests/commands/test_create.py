import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")
TOKEN = os.getenv("CKART_SESSION", "")

def test_create_api_invalid_provider():
    """
    Test hitting the actual VM creation endpoint with a completely invalid provider ID.
    This safely verifies bad inputs return the appropriate 400 Bad Request or 500 without spawning a real VM.
    """
    url = f"{BASE_URL}/vms/launch"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    payload = {
        "vm_name": "test_invalid_creation_vm",
        "provider_id": "invalid_provider_id_testing_777",
        "vcpus": "1",
        "ram": "1024",
        "storage": "2048",
        "vm_image": "ubuntu",
        "remarks": "integration test",
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 401:
        pytest.skip("No valid session token found for testing. Skipping test.")
        
    # Expect error from the server instead of 200 creation success.
    assert response.status_code in [400, 500]
    data = response.json()
    assert "error" in data

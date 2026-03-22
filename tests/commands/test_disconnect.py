import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")
TOKEN = os.getenv("CKART_SESSION", "")

def test_disconnect_api_invalid_vm():
    """
    Test disconnecting from a fake VM ID.
    Expect a 404 or backend refusal instead of success.
    """
    url = f"{BASE_URL}/cli/vms/disconnect?vm_id=missing_vm_testing_123"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    
    response = requests.get(url, headers=headers)
    assert response.status_code in [404, 400, 500, 405]
    if response.content and "application/json" in response.headers.get("Content-Type", ""):
        data = response.json()
        assert "error" in data or "message" in data

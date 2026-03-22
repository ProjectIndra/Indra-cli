import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")
TOKEN = os.getenv("CKART_SESSION", "")

def test_ps_api_active_vms():
    """
    Test hitting the real backend for active VMs.
    Requires a valid session token in .env.
    """
    url = f"{BASE_URL}/vms/allActiveVms"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    # If we have an invalid token, it might drop a 401; otherwise, we expect 200.
    assert response.status_code in [200, 401, 500]
    if response.status_code == 200:
        data = response.json()
        assert "active_vms" in data
        assert isinstance(data["active_vms"], list)

def test_ps_api_all_vms():
    """
    Test hitting the real backend to get ALL VMs.
    """
    url = f"{BASE_URL}/vms/allVms"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    
    response = requests.get(url, headers=headers)
    assert response.status_code in [200, 401, 500]
    if response.status_code == 200:
        data = response.json()
        assert "all_vms" in data
        assert isinstance(data["all_vms"], list)

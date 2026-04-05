import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")
TOKEN = os.getenv("CKART_SESSION", "")

def test_rm_api_invalid_vm():
    """
    Test regular removal of an invalid VM.
    The real endpoint should reject with 404 if the VM is not found.
    """
    url = f"{BASE_URL}/vms/removeCLI?vm_name=non_existent_vm_9879879"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 401:
        pytest.skip("No valid session token found for testing. Skipping test.")
        
    assert response.status_code in [400, 404, 405, 500]
    data = response.json()
    assert "error" in data

def test_force_rm_api_invalid_vm():
    """
    Test force removal of an invalid VM directly on the backend.
    """
    url = f"{BASE_URL}/vms/forceRemoveCLI?vm_name=non_existent_vm_9879879"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 401:
        pytest.skip("No valid session token found for testing. Skipping test.")
        
    assert response.status_code in [400, 404, 405, 500]
    data = response.json()
    assert "error" in data

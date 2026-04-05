import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")
TOKEN = os.getenv("CKART_SESSION", "")

def test_start_api_invalid_vm():
    """
    Test hitting /vms/start on the real backend with a non-existent VM.
    """
    url = f"{BASE_URL}/vms/start"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    payload = {"vm_id": "non_existent_vm_for_testing", "provider_id": ""}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 401:
        pytest.skip("No valid session token found for testing. Skipping test.")
        
    assert response.status_code in [404, 500]
    data = response.json()
    assert "error" in data

def test_stop_api_invalid_vm():
    """
    Test hitting /vms/stop on the real backend with a non-existent VM.
    """
    url = f"{BASE_URL}/vms/stop"
    headers = {"Authorization": f"BearerCLI {TOKEN}"}
    payload = {"vm_id": "non_existent_vm_for_testing", "provider_id": ""}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 401:
        pytest.skip("No valid session token found for testing. Skipping test.")
        
    assert response.status_code in [404, 500]
    data = response.json()
    assert "error" in data

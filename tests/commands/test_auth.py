import os
import requests
from dotenv import load_dotenv

# Load the real environment variables from the actual .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
BASE_URL = os.getenv("MGMT_SERVER", "https://backend.computekart.com")

def test_auth_api_invalid_token():
    """
    Test hitting the actual backend server with an invalid CLI token.
    Validates that the server responds with a 401 status and correct error structure.
    """
    url = f"{BASE_URL}/cli/profile/verifyCliToken"
    payload = {
        "cli_verification_token": "some_invalid_random_token_12345",
        "wireguard_endpoint": os.getenv("WG_ENDPOINT", "10.24.37.4:3000"),
        "wireguard_public_key": os.getenv("WG_PUBLIC_KEY", "fainfiaa0f=4949"),
    }
    
    response = requests.post(url, headers={"ngrok-skip-browser-warning": "true"}, json=payload)
    data = response.json()
    
    assert response.status_code == 401
    assert "error" in data
    assert data["error"] == "Invalid token"

def test_auth_api_missing_token():
    """
    Test hitting the backend server without providing a token entirely.
    Validates that the backend handles empty/missing inputs gracefully.
    """
    url = f"{BASE_URL}/cli/profile/verifyCliToken"
    payload = {
        "cli_verification_token": "",
        "wireguard_endpoint": "10.24.37.4:3000",
        "wireguard_public_key": "fainfiaa0f=4949",
    }
    
    response = requests.post(url, headers={"ngrok-skip-browser-warning": "true"}, json=payload)
    data = response.json()
    
    # Assert depending on the expected behavior of your server (e.g., 401 or 400 Bad Request)
    assert response.status_code in [400, 401]
    assert "error" in data

# UNCOMMENT AND FILL IN with a newly generated CLI Token to test the success case! #
def test_auth_api_valid_token():
    """
    Test hitting the actual backend with a legitimate token to confirm
    that a correct string yields a 200 status code and receives a session_token.
    """
    url = f"{BASE_URL}/cli/profile/verifyCliToken"
    payload = {
        "cli_verification_token": "fe398f68-9345-4be0-baba-b1c6b5349f31",  # Add a real token here
        "wireguard_endpoint": "10.24.37.4:3000",
        "wireguard_public_key": "fainfiaa0f=4949",
    }
    
    response = requests.post(url, headers={"ngrok-skip-browser-warning": "true"}, json=payload)
    data = response.json()
    
    assert response.status_code == 200
    assert "session_token" in data
    assert len(data["session_token"]) > 0

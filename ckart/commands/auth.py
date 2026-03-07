import os

import requests

from ckart import output
from ckart.env import set_persistent_env_var


def handle(args):
    BASE_URL = os.getenv("MGMT_SERVER")
    env_path = os.path.join(os.path.expanduser("~"), ".ckart-cli", ".env")
    token = args.token
    url = f"{BASE_URL}/cli/profile/verifyCliToken"
    try:
        response = requests.post(
            url,
            headers={"ngrok-skip-browser-warning": "true"},
            json={
                "cli_verification_token": token,
                "wireguard_endpoint": os.getenv("WG_ENDPOINT", "10.24.37.4:3000"),
                "wireguard_public_key": os.getenv("WG_PUBLIC_KEY", "fainfiaa0f=4949"),
            },
        )
        data = response.json()
        if response.status_code == 200:
            session_token = data.get("session_token")
            if session_token:
                env_path = os.path.join(
                    os.path.expanduser(path="~"), ".ckart-cli", ".env"
                )
                set_persistent_env_var(
                    "CKART_SESSION", session_token, env_file=env_path
                )
                output.success("Authentication successful. Session token saved.")
                output.info("You can now use other ckart commands.")
            else:
                output.error(
                    "No session token received from server. Please verify your CLI token and try again."
                )
        elif response.status_code == 401:
            output.error(
                "Invalid authentication token. Please check your token on the website and try again."
            )
        else:
            output.error(f"Authentication failed: {data.get('error', 'Unknown error')}")
    except requests.RequestException as e:
        output.error(f"Failed to connect to server: {e}")

import os
import traceback

import requests
from dotenv import load_dotenv

from ckart.env import set_persistent_env_var

# load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))


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
                print("[+] Authentication successful. Session token saved.")
                print("[i] You can now use other ckart commands.")
            else:
                print(
                    "[-] No session token received from server. Please check your token and try again."
                )
        elif response.status_code == 401:
            print(
                "[-] Invalid authentication token. Please check your token and try again."
            )
        else:
            print(f"[-] Authentication failed: {data.get('error', 'Unknown error')}")
    except requests.RequestException as e:
        print(f"[-] Failed to connect to server: {e}")

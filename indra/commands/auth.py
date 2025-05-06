import requests
import os
import platform
import subprocess

from indra.env import set_persistent_env_var

BASE_URL = os.getenv("MGMT_SERVER")

def handle(args):
    token = args.token
    url = f"{BASE_URL}/cli/profile/verifyCliToken"

    print(f"Authenticating with token: {token}")
    
    try:
        response = requests.post(url, json={
            "cli_verification_token": token,
            "wireguard_endpoint":os.getenv("WG_ENDPOINT","10.24.37.4:3000"),
            "wireguard_public_key":os.getenv("WG_PUBLIC_KEY","fainfiaa0f=4949"),
            })

        data = response.json()

        if response.status_code == 200:
            session_token = data.get("session_token")
            if session_token:
                set_persistent_env_var("INDRA_SESSION", session_token)
                print("\nAuthentication successful. Session token saved.")
            else:
                print(" No session token received from server.")
        else:
            print(f"Authentication failed: {data.get('error', 'Unknown error')}")
    except requests.RequestException as e:
        print(f" Error connecting to server")

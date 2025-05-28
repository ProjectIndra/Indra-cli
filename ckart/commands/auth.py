import requests
import os
from ckart.env import set_persistent_env_var
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))
BASE_URL = os.getenv("MGMT_SERVER")

def handle(args):
    token = args.token
    print(f"URL: {BASE_URL}")
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
                set_persistent_env_var("CKART_SESSION", session_token)
                config_path = r"C:\\Users\\%USERNAME%\\Documents\\WireGuard\\demo-client.conf"
                config_path = os.path.expandvars(config_path)

                set_persistent_env_var("MGMT_SERVER", "https://backend.computekart.com")
                set_persistent_env_var("LISTEN_PORT", 51820)
                set_persistent_env_var("WIREGUARD_EXE", r"C:\\Program Files\\WireGuard\\wireguard.exe")
                set_persistent_env_var("CONFIG_PATH", config_path)
                set_persistent_env_var("CONFIG_NAME", "demo-client")

                print("[+] Environment variables written to .env")
                print("\n[+] Authentication successful. Session token saved.")
            else:
                print("[-] No session token received from server.")
        else:
            print(f"[-] Authentication failed: {data.get('error', 'Unknown error')}")
            return
    except requests.RequestException as e:
        print(f"[-] Error connecting to server.{e}")

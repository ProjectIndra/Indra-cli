import requests
import os
import subprocess

BASE_URL = os.getenv("MGMT_SERVER")
BASHRC = os.path.expanduser("~/.bashrc")

def read_old_session_token():
    """Reads the old session token from ~/.bashrc if it exists."""
    if not os.path.exists(BASHRC):
        return None

    with open(BASHRC, "r") as f:
        for line in f:
            if line.startswith("export MGMT_SESSION_TOKEN="):
                return line.strip().split("=", 1)[1].replace('"', '')
    return None

def save_and_source_env_variable(name, value):
    """Appends export to ~/.bashrc and sources it."""
    with open(BASHRC, "a") as f:
        f.write(f'\nexport {name}="{value}"\n')
    print(f"\n✅ Session token saved to {BASHRC}")

    # Auto-source bashrc in current shell (only works in interactive shells)
    subprocess.call(f'source {BASHRC}', shell=True, executable='/bin/bash')
    print("⚡ Applied immediately. You can use it in this terminal now.")

def handle(args):
    new_token = args.token
    old_token = read_old_session_token()

    url = f"{BASE_URL}/cli/auth"

    payload = {
        "auth_token": new_token,
        "old_session_token": old_token
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()
        print(data)

        if response.status_code == 200:
            session_token = data.get("session_token")
            if session_token:
                save_and_source_env_variable("MGMT_SESSION_TOKEN", session_token)
                print("\n✅ Authentication successful. Session token saved and loaded.")
            else:
                print("❌ No session token received from server.")
        else:
            print(f"❌ Authentication failed: {data.get('error', 'Unknown error')}")
    except requests.RequestException as e:
        print(f"❌ Error connecting to server: {e}")

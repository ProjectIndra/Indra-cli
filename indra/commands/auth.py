import requests
import os
import platform
import subprocess

BASE_URL = os.getenv("MGMT_SERVER")

def save_env_variable(name, value):
    system = platform.system()
    if system == "Windows":
        subprocess.run(["setx", name, value], shell=True)
    elif system in ["Linux", "Darwin"]:  # macOS is Darwin
        shell_rc = os.path.expanduser("~/.bashrc")
        if os.environ.get("SHELL", "").endswith("zsh"):
            shell_rc = os.path.expanduser("~/.zshrc")

        with open(shell_rc, "a") as f:
            f.write(f'\nexport {name}="{value}"\n')
        print(f"\n✅ Session token saved to {shell_rc}")
        print("⚠️  Please restart your terminal or run `source ~/.bashrc` to apply it.")
    else:
        print("Unsupported OS for persistent environment variable saving.")

def handle(args):
    token = args.token
    url = f"{BASE_URL}/cli/auth"
    
    try:
        response = requests.post(url, json={"token": token})
        data = response.json()
        print(data)

        if response.status_code == 200:
            session_token = data.get("session_token")
            if session_token:
                save_env_variable("MGMT_SESSION_TOKEN", session_token)
                print("\n✅ Authentication successful. Session token saved.")
            else:
                print("❌ No session token received from server.")
        else:
            print(f"❌ Authentication failed: {data.get('error', 'Unknown error')}")
    except requests.RequestException as e:
        print(f"❌ Error connecting to server: {e}")

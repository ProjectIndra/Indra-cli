import os

import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))


def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if not base_url:
        print("[-] Error: MGMT_SERVER URL not set in environment variables.")
        return

    url = f"{base_url}/"  # Adjust if your API uses a different endpoint

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        print("[+] MGMT Server is ONLINE!")
        if response.text.strip():
            print("[Server Response]:", response.text.strip())
    except requests.exceptions.ConnectionError:
        print(
            "[-] MGMT Server is OFFLINE or unreachable. Please check your network connection or server address."
        )
    except requests.exceptions.Timeout:
        print("[-] MGMT Server did not respond in time. Please try again later.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to check server status: {e}")

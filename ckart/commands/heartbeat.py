import os
import requests
from dotenv import load_dotenv

load_dotenv()

def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if not base_url:
        print("[-] Error: MGMT_SERVER URL not set in environment variables.")
        return

    url = f"{base_url}/"  # Adjust if your API uses a different endpoint

    try:
        response = requests.get(url, timeout=5)  # Set a short timeout
        response.raise_for_status()  # Raise error for HTTP 4xx/5xx responses
        
        print("[+] MGMT Server is ONLINE!")
        print(response.text)  # Show heartbeat data (if available)

    except requests.exceptions.ConnectionError:
        print("[-] Error: MGMT Server is OFFLINE or unreachable.")

    except requests.exceptions.Timeout:
        print("[-] Error: MGMT Server did not respond in time.")

    except requests.exceptions.RequestException as e:
        print(f"[-] Error: {e}")

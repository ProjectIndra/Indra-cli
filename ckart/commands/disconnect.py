import os

import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))

BASE_URL = os.getenv("MGMT_SERVER")


def handle(args):
    """Disconnect from the VM WireGuard network."""
    url = f"{BASE_URL}/cli/vms/disconnect?vm_id={args.disconnect}"
    token = os.getenv("CKART_SESSION")
    try:
        response = requests.get(url, headers={"Authorization": f"BearerCLI {token}"})
        data = response.json()
        if response.status_code == 200:
            print(f"[+] VM '{args.disconnect}' disconnected from WireGuard network.")
        elif response.status_code == 404:
            print(
                f"[-] VM '{args.disconnect}' not found. Please check the VM ID and try again."
            )
        elif response.status_code == 500:
            print(
                f"[-] Server error: {data.get('error', f'Error disconnecting VM {args.disconnect}')}"
            )
        else:
            print(f"[-] {data.get('error', 'Unknown error occurred.')}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to disconnect VM '{args.disconnect}': {e}")

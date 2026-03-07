import os

import requests
from dotenv import load_dotenv

from ckart import output

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
            output.success(
                f"VM '{args.disconnect}' disconnected from WireGuard network."
            )
        elif response.status_code == 404:
            output.error(
                f"VM '{args.disconnect}' not found. Please verify the VM ID and retry."
            )
        elif response.status_code == 500:
            output.error(
                f"Server error: {data.get('error', f'Error disconnecting VM {args.disconnect}')}"
            )
        else:
            output.error(data.get("error", "Unknown error occurred."))
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to disconnect VM '{args.disconnect}': {e}")

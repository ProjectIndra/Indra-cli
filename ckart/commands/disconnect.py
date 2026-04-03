import os
import requests
from ckart import output



def handle(args):
    """Disconnect from the VM WireGuard network."""
    BASE_URL = os.getenv("MGMT_SERVER")
    token = os.getenv("CKART_SESSION")

    if args.disconnect != None:
        url = f"{BASE_URL}/cli/vms/disconnect?vm_id={args.disconnect}"
    else:
        output.error("Please provide a VM ID to disconnect.")
        return

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

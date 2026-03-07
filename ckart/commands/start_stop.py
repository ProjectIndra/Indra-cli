import os

import requests
from dotenv import load_dotenv

from ckart import output

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))


def handle(args):
    base_url = os.getenv("MGMT_SERVER")
    if not base_url:
        output.error("MGMT_SERVER URL not set in environment variables.")
        return

    # Determine API endpoint based on command
    if args.start:
        command = "start"
        vm_id = args.start
    elif args.stop:
        command = "stop"
        vm_id = args.stop
    else:
        output.error("Incorrect command; use 'ckart vms -h' for help.")
        return

    endpoint = f"/vms/{command}"
    url = f"{base_url}{endpoint}"
    token = os.getenv("CKART_SESSION")

    try:
        response = requests.post(
            url,
            headers={"Authorization": f"BearerCLI {token}"},
            json={"vm_id": vm_id, "provider_id": ""},
        )
        data = response.json()
        if response.status_code == 200:
            output.success(f"VM '{vm_id}' {command}ed successfully.")
        elif response.status_code == 404:
            output.error(
                f"VM '{vm_id}' not found. Please check the VM ID and try again."
            )
        elif response.status_code == 500:
            output.error(
                f"Server error: {data.get('error', f'Error {command}ing VM {vm_id}')}"
            )
        else:
            output.error(data.get("error", "Unknown error occurred."))
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to {command} VM '{vm_id}': {e}")

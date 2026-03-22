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

    if not args.remove:
        output.error("VM name is required.")
        return

    # Determine API endpoint based on force flag
    endpoint = "/vms/forceRemoveCLI" if args.force else "/vms/removeCLI"
    url = f"{base_url}{endpoint}?vm_name={args.remove}"
    token = os.getenv("CKART_SESSION")

    try:
        response = requests.post(url, headers={"Authorization": f"BearerCLI {token}"}, json={"vm_name": args.remove})
        data = response.json()
        if response.status_code == 200:
            output.success(f"VM '{args.remove}' removed successfully.")
        elif response.status_code == 404:
            output.error(
                f"VM '{args.remove}' not found. Please check the VM name and try again."
            )
        elif response.status_code == 500:
            output.error(
                f"Server error: {data.get('error', f'Error removing VM {args.remove}')}"
            )
        else:
            output.error(data.get("error", "Unknown error occurred."))
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to remove VM '{args.remove}': {e}")


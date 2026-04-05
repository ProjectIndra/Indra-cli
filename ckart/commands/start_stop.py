import os
import requests
from ckart import output
from ckart.utils import resolve_prefix


def handle(args):
    base_url = os.getenv("MGMT_SERVER")
    token = os.getenv("CKART_SESSION")

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

    # Fetch providerId from /vms/allVms
    allVms_url = f"{base_url}/vms/allVms"
    provider_id = None
    try:
        allVms_response = requests.get(
            allVms_url, headers={"Authorization": f"BearerCLI {token}"}
        )
        allVms_response.raise_for_status()
        vms_data = allVms_response.json().get("all_vms", [])
        
        vm_obj, err = resolve_prefix(vms_data, vm_id, key="internalVmName")
        if err:
            output.error(err)
            return
        provider_id = vm_obj["providerId"]
        
        if not provider_id:
            output.error(f"VM '{vm_id}' not found in your account.")
            return

    except requests.exceptions.RequestException as e:
        output.error(f"Failed to fetch VM details: {e}")
        return

    endpoint = f"/vms/{command}"
    url = f"{base_url}{endpoint}"

    try:
        response = requests.post(
            url,
            headers={"Authorization": f"BearerCLI {token}"},
            json={"vm_id": vm_id, "provider_id": provider_id},
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

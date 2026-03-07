import os
import requests
from ckart import output



def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if not base_url:
        output.error("MGMT_SERVER URL not set in environment variables.")
        return

    endpoint = "/vms/allVms" if args.all else "/vms/allActiveVms"
    url = f"{base_url}{endpoint}"
    token = os.getenv("CKART_SESSION")

    try:
        response = requests.get(url, headers={"Authorization": f"BearerCLI {token}"})
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()
        table_data = []

        if not args.all:
            active_vms = data.get("active_vms", [])
            if not active_vms:
                output.warning(
                    "No active VMs found. Use 'ckart vms --create <provider_id>' to launch a new VM."
                )
                return
            table_data = [
                [
                    vm.get("internalVmName", "N/A"),
                    vm.get("vmName", "N/A"),
                    vm.get("providerId", "N/A"),
                    "Connected" if vm.get("wireguard_status") else "Disconnected",
                ]
                for vm in active_vms
            ]
            headers = ["VM ID", "VM Name", "ProviderId", "WireGuard Status"]
            output.success("Active VMs:")
            output.table(table_data, headers=headers)
            output.plain()
        elif args.all:
            all_vms = data.get("all_vms", [])
            if not all_vms:
                output.warning(
                    "No VMs found. Use 'ckart vms --create <provider_id>' to launch a new VM."
                )
                return
            table_data = [
                [
                    vm.get("internalVmName", "N/A"),
                    vm.get("vmName", "N/A"),
                    vm.get("providerId", "N/A"),
                    vm.get("status", "N/A"),
                    "Connected" if vm.get("wireguard_status") else "Disconnected",
                ]
                for vm in all_vms
            ]
            headers = ["VM ID", "VM Name", "Provider Id", "Status", "WireGuard Status"]
            output.success("All VMs:")
            output.table(table_data, headers=headers)
            output.plain()
        else:
            output.warning("Invalid arguments. Use 'ckart vms -h' for help.")

    except requests.exceptions.RequestException as e:
        output.error(f"Failed to fetch VMs: {e}")

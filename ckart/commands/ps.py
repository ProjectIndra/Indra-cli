import os
import requests
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if not base_url:
        print("Error: MGMT_SERVER URL not set in environment variables.")
        return

    endpoint = "/vms/allVms" if args.all else "/vms/allActiveVms"
    url = f"{base_url}{endpoint}"
    token = os.getenv("CKART_SESSION")

    try:
        response = requests.get(url, headers={"Authorization": f"BearerCLI {token}"})
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        data = response.json()
        # Extract relevant fields
        table_data = []

        if(not args.all):
            active_vms = data.get("active_vms",[])
            if not active_vms:
                print("[-] No active VMs found.")
                return
            table_data = [
                [
                    vm.get("vm_id", "N/A"),
                    vm.get("vm_name", "N/A"),
                    vm.get("provider_name", "N/A"),
                    # vm.get("wireguard_ip", "N/A"),
                    " Connected" if vm.get("wireguard_status") else " Disconnected"
                ]
                for vm in active_vms
            ]
            # Define headers
            headers = ["VM ID", "VM Name", "Provider", "WireGuard Status"]
            # Print table
            print("\n[+] All Active VMs:")
            print(tabulate(table_data, headers=headers))
            print("\n")
        elif args.all:
            all_vms = data.get("all_vms",[])
            if not all_vms:
                print("[+] No VMs found.")
                return
            table_data = [
                [
                    vm.get("vm_id", "N/A"),
                    vm.get("vm_name", "N/A"),
                    vm.get("provider_name", "N/A"),
                    vm.get("status", "N/A"),
                    # vm.get("wireguard_ip", "N/A"),
                    "Connected" if vm.get("wireguard_status") else "Disconnected"
                ]
                for vm in all_vms
            ]
            # Define headers
            headers = ["VM ID", "VM Name", "Provider","Status", "WireGuard Status"]
            # Print table
            print("\n[+] All VMs:")
            print(tabulate(table_data, headers=headers))
            print("\n")
        else:
            print("[-] Argument parsing has gone wrong.")

    except requests.exceptions.RequestException as e:
        print(f"[-] Error fetching VMs.")
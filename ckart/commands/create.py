import os
import requests
from ckart import output
from ckart.utils import resolve_prefix


def get_input(prompt, type_func=str):
    """Helper function to get user input safely."""
    while True:
        try:
            return type_func(input(f"{prompt}: "))
        except ValueError:
            output.warning("Invalid input. Please try again.")


def handle(args):
    base_url = os.getenv("MGMT_SERVER")
    token = os.getenv("CKART_SESSION")

    user_prefix = args.create
    try:
        list_url = f"{base_url}/providers/all" 
        list_res = requests.get(list_url, headers={"Authorization": f"BearerCLI {token}"})
        list_res.raise_for_status()
        providers = list_res.json().get("providers", [])

        provider_obj, err = resolve_prefix(providers, user_prefix, key="providerId")
        if err:
            output.error(err)
            return
            
        provider_id = provider_obj["providerId"]
        output.info(f"Using Provider: {provider_id}")
        
    except Exception as e:
        output.error(f"Could not verify provider ID: {e}")
        return

    # Step 2: Ask for vCPU, RAM, and Storage and verify
    vcpus = get_input("Enter required vCPUs", int)
    ram = get_input("Enter required RAM (in GB)", int)
    storage = get_input("Enter required Storage (in GB)", int)

    # Step 3: Ask for VM Name & Remarks
    vm_name = get_input("Enter VM Name")
    if not vm_name:
        output.error("VM name cannot be empty.")
        return

    remarks = get_input("Enter Remarks")

    # Hardcoded VM Image
    vm_image = get_input("Enter Image (example: ubuntu)", str)

    # Step 4: Final VM creation
    create_vm_url = f"{base_url}/vms/launch"
    # client_id = 1  # Hardcoded for now

    payload = {
        "vm_name": vm_name,
        "provider_id": provider_id,
        "vcpus": str(int(vcpus)),
        "ram": str(int(ram) * 1024),
        "storage": str(int(storage) * 1024),
        "vm_image": vm_image,
        "remarks": remarks,
    }

    try:
        response = requests.post(
            create_vm_url, json=payload, headers={"Authorization": f"BearerCLI {token}"}
        )
        data = response.json()
        if response.status_code == 200:
            output.success("VM created successfully!")
            output.info(data.get("message", ""))
        elif response.status_code == 400:
            output.error("Bad request. Please check your values and try again.")
            output.error(data.get("error", "Unknown error."))
        elif response.status_code == 500:
            output.error("Server error. Could not create VM; try again later.")
            output.error(data.get("error", "Failed to reach provider."))
        else:
            output.error(data.get("error", "Unknown error occurred."))

    except requests.exceptions.RequestException as e:
        output.error(f"Failed to create VM: {e}")

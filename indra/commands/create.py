import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_input(prompt, type_func=str):
    """Helper function to get user input safely."""
    while True:
        try:
            return type_func(input(f"{prompt}: "))
        except ValueError:
            print("Invalid input. Please try again.")

def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    provider_id = args.create  # Comes from CLI argument
    token = os.getenv("INDRA_SESSION")

    # Step 1: Verify provider ID
    # verify_provider_url = f"{base_url}/cli/vms/create/verify_provider?provider_id=provider-{provider_id}"
    # response = requests.get(verify_provider_url, headers={"Authorization": f"BearerCLI {token}"})
    # print(response.json())
    # if response.status_code == 500:
    #     print("Invalid Provider ID. Try again.")
    #     return
    # elif response.status_code == 200:
    #     print("Provider verified!")
    # else:
    #     print("Provider not found. Try again")
    #     return

    # Step 2: Ask for vCPU, RAM, and Storage and verify
    vcpus = get_input("Enter required vCPUs", int)
    ram = get_input("Enter required RAM (in GB)", int)
    storage = get_input("Enter required Storage (in GB)", int)

    # verify_specs_url = f"{base_url}/vms/create/verify_specs?vcpus={vcpus}&ram={ram}&storage={storage}"
    # json_data = {
    #     "provider_id": provider_id,
    #     "vcpus": vcpus,
    #     "ram": ram * 1024,  # Convert GB to MB
    #     "storage": storage * 1024  # Convert GB to MB
    # }
    # response = requests.post(verify_specs_url,json=json_data,  headers={"Authorization": f"BearerCLI {token}"})
    # print(response.json())
    
    # if response.status_code == 500:
    #     print("Invalid Specs. Try again.")
    #     return
    # elif response.status_code == 200:
    #     print("Specs verified!")
    # else:
    #     print("Specs not found. Try again.")

    # Step 3: Ask for VM Name & Remarks
    vm_name = get_input("Enter VM Name")
    remarks = get_input("Enter Remarks")

    # Hardcoded VM Image
    vm_image = get_input("Enter Image (example: ubuntu)", str)

    # Step 4: Final VM creation
    create_vm_url = f"{base_url}/vms/launch"
    # client_id = 1  # Hardcoded for now

    payload = {
        "vm_name": vm_name,
        "provider_id": provider_id,
        "vcpus": vcpus,
        "ram": ram,
        "storage": storage,
        "vm_image_type": vm_image,
        # "client_id": client_id,
        "remarks": remarks
    }

    response = requests.post(create_vm_url, json=payload, headers={"Authorization": f"BearerCLI {token}"})
    data=response.json()
    print(data)

    if response.status_code == 200:
            print(data.get("message"))
    elif response.status_code == 500:
        print(data.get('error',"Failed to reach provider"))
        print("Invalid VM creation request. Try again.")
        return
    else:
        print(f"{data.get('error')}")
        return


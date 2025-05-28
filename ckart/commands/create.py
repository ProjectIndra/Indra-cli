import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))

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
    token = os.getenv("CKART_SESSION")

    # Step 2: Ask for vCPU, RAM, and Storage and verify
    vcpus = get_input("Enter required vCPUs", int)
    ram = get_input("Enter required RAM (in GB)", int)
    storage = get_input("Enter required Storage (in GB)", int)

    # Step 3: Ask for VM Name & Remarks
    vm_name = get_input("Enter VM Name")
    if not vm_name:
        print("VM Name cannot be empty. Please try again.")
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
        "vcpus": vcpus,
        "ram": ram*1024,
        "storage": storage*1024,
        "vm_image_type": vm_image,
        "remarks": remarks
    }

    response = requests.post(create_vm_url, json=payload, headers={"Authorization": f"BearerCLI {token}"})
    data=response.json()
    # print(data)

    if response.status_code == 200:
        print("\n[+] VM created successfully!")
        print(f"[+] {data.get("message")}")
    elif response.status_code == 500:
        print("\n[-] Invalid VM creation request. Try again.")
        print(data.get('error',"Failed to reach provider"))
        return
    else:
        print(f"[-] {data.get('error')}")
        return


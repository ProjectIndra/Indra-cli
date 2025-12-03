import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))


def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if not base_url:
        print("[-] Error: MGMT_SERVER URL not set in environment variables.")
        return

    if not args.remove:
        print("[-] Error: VM Name is required.")
        return

    # Determine API endpoint based on force flag
    endpoint = "/vms/forceRemoveCLI" if args.force else "/vms/removeCLI"
    url = f"{base_url}{endpoint}?vm_name={args.remove}"
    token= os.getenv("CKART_SESSION")

    try:
        response = requests.get(url, headers={"Authorization": f"BearerCLI {token}"})
        data = response.json()
        if response.status_code == 200:
            print(f"[+] VM '{args.remove}' removed successfully.")
        elif response.status_code == 404:
            print(f"[-] VM '{args.remove}' not found. Please check the VM name and try again.")
        elif response.status_code == 500:
            print(f"[-] Server error: {data.get('error', f'Error removing VM {args.remove}')}" )
        else:
            print(f"[-] {data.get('error', 'Unknown error occurred.')}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to remove VM '{args.remove}': {e}")
    try:
        response = requests.get(url, headers={"Authorization": f"BearerCLI {token}"})
        data = response.json()
        
        if response.status_code == 200:
            print(f"[+] {data.get('message')}")
        elif response.status_code == 500:
               print(f"[-] {data.get('error',f'Error removing VM {args.remove}')}")
               return
        else:
            print(f"[-] {data.get('error')}")
            return
    except requests.exceptions.RequestException as e:
        print(f"[-] Error removing VM {args.remove}: {e}")

import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))

BASE_URL = os.getenv("MGMT_SERVER")

def handle(args):
    """Disconnect from the VM WireGuard network."""
    url = f"{BASE_URL}/cli/vms/disconnect?vm_id={args.disconnect}"
    token = os.getenv("CKART_SESSION")
    try:
        response = requests.get(url, headers={"Authorization": f"BearerCLI {token}"})
        data=response.json()
        
        if response.status_code == 200:
            print(f"[-] {data.get('message')}")
        elif response.status_code == 500:
               print(f"[-] {data.get('error',f'Error Disconnecting VM {args.disconnect}')}")
               return
        else:
            print(f"[-] {data.get('error')}")
            return
        
        print(f"\n[+] Disconnected VM {args.disconnect} from WireGuard!\n")
    
    except requests.exceptions.RequestException as e:
        print(f"[-] Error disconnecting VM {args.disconnect}.")

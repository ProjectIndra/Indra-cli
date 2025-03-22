import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("MGMT_SERVER")

def disconnect_vm(args):
    """Disconnect from the VM WireGuard network."""
    url = f"{BASE_URL}/cli/vms/disconnect?vm_id={args.vm_id}"
    
    try:
        response = requests.get(url)
        data=response.json()
        print(data)
        
        if response.status_code == 200:
            print(data.get("message"))
        elif response.status_code == 500:
               print(f"{data.get('error',f"Error Disconnecting VM {args.vm_id}")}")
               return
        else:
            print(f"{data.get('error')}")
            return
        
        print(f"\n**Disconnected VM {args.vm_id} from WireGuard!**\n")
    
    except requests.exceptions.RequestException as e:
        print(f"Error disconnecting VM: {e}")

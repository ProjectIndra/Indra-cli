import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))


def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    # Determine API endpoint based on command
    if args.start:
        command = "start"
        vm_id = args.start
    elif args.stop:
        command = "stop"
        vm_id = args.stop
    else:
        print("[-] Incorrect Command")
        return 
    # print(vm_id, command)
    
    endpoint = f"/vms/{command}"
    url = f"{base_url}{endpoint}"
    token= os.getenv("CKART_SESSION")

    try:
        response = requests.post(url,headers={"Authorization": f"BearerCLI {token}"}, json={"vm_id": vm_id, "provider_id":""})
        data= response.json()
        
        if response.status_code == 200:
            print(f"[+] {data.get('message')}")
        elif response.status_code == 500:
               print(f"[-] {data.get('error',f'Error removing VM {vm_id}')}")
               return
        else:
            print(f"[-] {data.get('error')}")
            return
    except requests.exceptions.RequestException as e:
        print(f"[-] Error {command}ing VM {vm_id}: {e}")

import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))


def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    # Determine API endpoint based on command
    if args.start:
        command = "startCLI"
        vm_name = args.start
    elif args.stop:
        command = "stopCLI"
        vm_name = args.stop
    else:
        print("[-] Incorrect Command")
        return 
    # print(vm_id, command)
    
    endpoint = f"/vms/{command}"
    url = f"{base_url}{endpoint}?vm_name={vm_name}"
    token= os.getenv("CKART_SESSION")

    try:
        response = requests.get(url,headers={"Authorization": f"BearerCLI {token}"})
        data= response.json()
        
        if response.status_code == 200:
            print(f"[+] {data.get('message')}")
        elif response.status_code == 500:
               print(f"[-] {data.get('error',f'Error removing VM {vm_name}')}")
               return
        else:
            print(f"[-] {data.get('error')}")
            return
    except requests.exceptions.RequestException as e:
        print(f"[-] Error {command}ing VM {vm_name}: {e}")

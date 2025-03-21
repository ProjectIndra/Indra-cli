import os
import requests
from dotenv import load_dotenv

load_dotenv()

def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if not base_url:
        print("Error: MGMT_SERVER URL not set in environment variables.")
        return

    if not args.vm_id:
        print("Error: VM ID is required.")
        return

    # Determine API endpoint based on command
    command = args.command  # Either "start" or "stop"
    endpoint = f"/cli/vms/{command}"
    url = f"{base_url}{endpoint}?vm_id={args.vm_id}"

    try:
        response = requests.get(url)
        data= response.json()
        
        if response.status_code == 200:
            print(data.get("message"))
        elif response.status_code == 500:
               print(f"{data.get('error',f"Error removing VM {args.vm_id}")}")
               return
        else:
            print(f"{data.get('error')}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Error {command}ing VM {args.vm_id}: {e}")

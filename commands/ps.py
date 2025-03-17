import requests
import json
import dotenv
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def handle(args):
    base_url = os.getenv("MGMT_SERVER")
    
    if not base_url:
        print("Error: MGMT_SERVER URL not set in environment variables.")
        return
    
    endpoint = "/allvms" if args.all else "/vms"
    url = f"{base_url}{endpoint}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        data = response.json()
        
        if not data:
            print("No VMs found.")
            return
        
        print("Listing VMs:")
        for vm in data:
            print(f"- ID: {vm.get('id', 'N/A')}, Name: {vm.get('name', 'N/A')}, Status: {vm.get('status', 'N/A')}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching VMs: {e}")

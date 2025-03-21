import os
import requests
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

def print_provider(data):
    provider = data["provider"]
    tabulate_data = []
    for key, value in provider.items():
        tabulate_data.append([key, value])
    print(tabulate(tabulate_data, headers=["Attribute", "Value"]))
    

def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if not base_url:
        print("Error: MGMT_SERVER URL not set in environment variables.")
        return

    # Determine API endpoint
    if args.provider is not None and args.query:
        vcpus, ram, storage = args.query
        endpoint = f"/cli/providers?provider_id={args.provider}&vcpus={vcpus}&ram={ram}&storage={storage}"
    elif args.all:
        endpoint = "/cli/providers/lists"
    else:
        print("Error: No provider ID or flag provided.")
        return

    url = f"{base_url}{endpoint}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()

        if not data:
            print("No providers found.")
            return
        print(data)

        if args.provider is not None and args.query:
            print_provider(data)
        elif args.all:
            print_provider_list(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching providers: {e}")

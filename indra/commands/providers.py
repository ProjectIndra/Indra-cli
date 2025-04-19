import os
import requests
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

# Function to show available provider commands
def print_provider_commands():
    commands = [
        ["indra providers -a/--all", "List all providers"],
        ["indra providers -d/--details 1", "Show details of provider with ID 1"],
        ["indra providers 1 -q/--query 4 8 100", "Query provider 1 with 4 vCPUs, 8GB RAM, 100GB storage"],
    ]

    print("\n🔹 Available Provider Commands:\n")
    print(tabulate(commands, headers=["Command", "Description"]), "\n")

# Function to print all providers (-a or --all)
def print_all_providers(data):
    active_providers = data.get("all_providers", [])
    print(data)
    if not active_providers:
        print("No active providers found.")
        return
    
    table_data = [
        [
            provider.get("provider_id", "N/A"),
            provider.get("provider_name", "N/A"),
            provider.get("provider_allowed_vcpu", "N/A"),
            provider.get("provider_allowed_ram", "N/A"),
            provider.get("provider_allowed_storage", "N/A"),
            provider.get("provider_allowed_networks", "N/A"),
            provider.get("provider_rating", "N/A"),
            provider.get("provider_type", "N/A"),
            provider.get("user_id", "N/A"),
            provider.get("provider_status", "N/A"),
        ]
        for provider in active_providers
    ]

    headers = ["Provider ID", "Provider Name", "Max CPU", "Max RAM", "Max Storage","Max Networks","Rating","Type","UserId", "Status"]
    print("\n🔹 List of All Providers:\n")
    print(tabulate(table_data, headers=headers), "\n")

# Function to print details of a specific provider (-d or --details)
def print_provider_details(data):
    if not data:
        print("Provider not found.")
        return
    table_data = [[key, value] for key, value in data.items()]
    
    print("\n🔹 Provider Details:\n")
    print(tabulate(table_data, headers=["Attribute", "Value"]))
    print("\n")

# Function to print provider query results (provider_id -q vcpus ram storage)
def print_provider_query_results(data, provider_id):
    can_create = data.get("can_create", False)
    if not can_create:
        print(f"Matching providers found cannot create vm for the given query for {provider_id}.")
        print(f"error: {data}")
    else:
        print(f"Matching provider found for {provider_id}")



# Function to handle provider-related CLI commands
def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    # Determine API endpoint based on arguments
    if args.provider is None and not args.all and args.details is None and args.query is None:
        print_provider_commands()
        return
    if args.provider is not None and args.query:
        vcpus, ram, storage = args.query
        endpoint = f"/providers/query"
        type="POST"
    elif args.details is not None:
        endpoint = f"/providers/details?provider_id={args.details}"
        type="GET"
    elif args.all:
        endpoint = "/providers/lists"
        type="GET"
    else:
        print("Error: Invalid command usage. Provide a valid flag or provider ID.")
        print_provider_commands()
        return

    url = f"{base_url}{endpoint}"
    token = os.getenv("INDRA_SESSION")
    json_data={
        "provider_id": args.provider,
        "vcpus": args.query[0] if args.query else None,
        "ram": args.query[1] * 1024 if args.query else None,
        "storage": args.query[2] * 1024 if args.query else None,
        "details": args.details
    }
    # print(args.query[1])

    try:
        if(type == "POST"):
            response = requests.post(url=url,json=json_data, headers={"Authorization": f"BearerCLI {token}","Content-Type": "application/json"})
        elif(type == "GET"):
            response = requests.get(url=url,json=json_data, headers={"Authorization": f"BearerCLI {token}","Content-Type": "application/json"})
        else:
            return
        response.raise_for_status()  # Handle HTTP errors (4xx, 5xx)
        data = response.json()
        print(data)
        if not data:
            print("No providers found.")
            return

        # Call appropriate print function based on command
        if args.provider is not None and args.query:
            print_provider_query_results(data=data, provider_id=args.provider)
        elif args.details is not None:
            print_provider_details(data=data)
        elif args.all:
            print_all_providers(data=data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching providers: {e}")

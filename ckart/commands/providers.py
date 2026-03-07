import os
import requests
from ckart import output


# Function to show available provider commands
def print_provider_commands():
    commands = [
        ["ckart providers -a/--all"                                                     , "List all providers"],
        ["ckart providers -d/--details <providerID>"                                    , "Show details of provider with providerID",],
        ["ckart providers <providerID> -q/--query <vCPU> <RAM>(GB) <Storage>(GB)"       , "Query provider 1 with 4 vCPUs, 8GB RAM, 100GB storage"],
    ]

    output.plain("\nAvailable provider commands:\n")
    output.table(commands, headers=["Command", "Description"])
    output.plain()


# Function to print all providers (-a or --all)
def print_all_providers(data):
    active_providers = data.get("all_providers", [])
    if not active_providers:
        output.warning("No providers found. Please add a provider or try again later.")
        return
    table_data = [
        [
            provider.get("providerId", "N/A"),
            provider.get("providerName", "N/A"),
            provider.get("providerAllowedVcpu", "N/A"),
            provider.get("providerAllowedRam", "N/A"),
            provider.get("providerAllowedStorage", "N/A"),
            provider.get("providerAllowedNetworks", "N/A"),
            provider.get("providerStatus", "N/A"),
        ]
        for provider in active_providers
    ]
    headers = [
        "Provider ID",
        "Provider Name",
        "Max CPU",
        "Max RAM",
        "Max Storage",
        "Max Networks",
        "Status",
    ]
    output.success("List of all providers:")
    output.table(table_data, headers=headers)
    output.plain()


# Function to print details of a specific provider (-d or --details)
def print_provider_details(data):
    if not data:
        output.error("Provider not found.")
        return
    table_data = [[key, value] for key, value in data.items()]

    output.success("Provider details:")
    output.table(table_data, headers=["Attribute", "Value"])
    output.plain()


# Function to print provider query results (provider_id -q vcpus ram storage)
def print_provider_query_results(data, provider_id):
    can_create = data.get("can_create", False)
    if not can_create:
        output.error(
            f"Matching providers found cannot create VM with the requested resources for {provider_id}."
        )
        output.error(f"Error payload: {data}")
    else:
        output.success(f"Matching provider found for {provider_id}.")


# Function to handle provider-related CLI commands
def handle(args):
    base_url = os.getenv("MGMT_SERVER")

    if args.help:
        print_provider_commands()
        return

    # Determine API endpoint based on arguments
    if (
        args.provider is None
        and not args.all
        and args.details is None
        and args.query is None
    ):
        print_provider_commands()
        return
    if args.provider is not None and args.query:
        vcpus, ram, storage = args.query
        endpoint = "/providers/query"
        type = "POST"
    # elif args.details is not None:
    #     endpoint = f"/providers/details?provider_id={args.details}"
    #     type="POST"
    elif args.all:
        endpoint = "/providers/lists"
        type = "GET"
    else:
        output.error("Invalid command usage. Provide a valid flag or provider ID.")
        print_provider_commands()
        return

    url = f"{base_url}{endpoint}"
    token = os.getenv("CKART_SESSION")
    json_data = {
        "provider_id": args.provider,
        "vcpus": args.query[0] if args.query else None,
        "ram": args.query[1] * 1024 if args.query else None,
        "storage": args.query[2] * 1024 if args.query else None,
        "details": args.details,
    }

    try:
        if type == "POST":
            response = requests.post(
                url=url,
                json=json_data,
                headers={
                    "Authorization": f"BearerCLI {token}",
                    "Content-Type": "application/json",
                },
            )
        elif type == "GET":
            response = requests.get(
                url=url,
                json=json_data,
                headers={
                    "Authorization": f"BearerCLI {token}",
                    "Content-Type": "application/json",
                },
            )
        else:
            return
        response.raise_for_status()  # Handle HTTP errors (4xx, 5xx)
        data = response.json()
        if not data:
            output.warning(
                "No providers found. Please add a provider or try again later."
            )
            return
        if args.provider is not None and args.query:
            print_provider_query_results(data=data, provider_id=args.provider)
        elif args.all:
            print_all_providers(data=data)
    except requests.exceptions.RequestException as e:
        output.error(f"Failed to fetch providers: {e}")

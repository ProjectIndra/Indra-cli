import argparse
from tabulate import tabulate
import os
from dotenv import load_dotenv
from ckart.commands import connect, create, ps, rm, heartbeat, providers, start_stop, disconnect, auth

load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))


def main():

    parser = argparse.ArgumentParser(prog="ckart", description="ckart CLI to manage VMs")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Auth Command
    auth_parser = subparsers.add_parser("auth", help="Authenticate cli session.")
    auth_parser.add_argument("token", type=str, help="Authentication token")
    auth_parser.set_defaults(func=auth.handle)

    # 'vms' command
    vms_parser = subparsers.add_parser("vms", help="Manage VMs.", add_help=False)
    vms_parser.add_argument("-a", "--all", action="store_true", help="Show all VMs")
    vms_parser.add_argument("--create", type=str, help="Create a new VM with the given Provider ID")
    vms_parser.add_argument("--connect", type=str, help="Connect to VM WireGuard network")
    vms_parser.add_argument("--disconnect", type=str, help="Disconnect from VM WireGuard network")
    vms_parser.add_argument("--start", type=str, help="Start a VM")
    vms_parser.add_argument("--stop", type=str, help="Stop a VM")
    vms_parser.add_argument("-rm","--remove", type=str, help="Remove a VM")
    vms_parser.add_argument("-f","--force", action="store_true", help="Force remove a VM")
    vms_parser.add_argument("-h", "--help", action="store_true", help="Show help for 'ckart vms'")

    def vms_handle(args):
        if args.help:
            commands =[
                ["ckart vms", "Show all active VMs"],
                ["ckart vms -a or ckart vms --all", "List all VMs"],
                ["ckart vms --create <provider_name>", "Create a new VM"],
                ["ckart vms --connect <vm_name>", "Connect to WireGuard network"],
                ["ckart vms --disconnect <vm_name>", "Disconnect from WireGuard network"],
                ["ckart vms --start <vm_name>", "Start a VM"],
                ["ckart vms --stop <vm_name>", "Stop a VM"],
                ["ckart vms --remove <vm_name>", "Remove a VM"],
                ["ckart vms --remove -f or --force <vm_name>", "Force remove a VM"],
                ["ckart vms -h or ckart vms --help", "Show help for 'ckart vms'"],
            ]
            print("\nAvailable commands for 'ckart vms':\n")
            print(tabulate(commands, headers=["Command", "Description"]),"\n")
        elif args.create:
            create.handle(args)
        elif args.all:
            ps.handle(args)
        elif args.connect:
            connect.handle(args)
        elif args.disconnect:
            disconnect.handle(args)
        elif args.start:
            start_stop.handle(args)
        elif args.stop:
            start_stop.handle(args)
        elif args.remove:
            rm.handle(args)
        else:
            ps.handle(args)

    vms_parser.set_defaults(func=vms_handle)

    # Heartbeat Command
    heartbeat_parser = subparsers.add_parser("heartbeat", help="Check if server is online.")
    heartbeat_parser.set_defaults(func=heartbeat.handle)

    # Provider Command
    provider_parser = subparsers.add_parser("providers", help="Manage providers.")
    provider_parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Get details of all providers"
    )
    provider_parser.add_argument(
        "-d", "--details",
        type=str,
        metavar="provider_id",
        help="Get details of a specific provider"
    )
    provider_parser.add_argument(
        "provider",
        type=str,
        nargs="?",
        help="Provider ID for querying specific provider"
    )
    provider_parser.add_argument(
        "-q", "--query",
        nargs=3,  # Expects three values: vcpus, ram, storage
        metavar=("vcpus", "ram", "storage"),
        type=int,
        help="Query providers with specific vCPUs, RAM, and Storage"
    )
    provider_parser.set_defaults(func=providers.handle)


        # Handle help manually to customize output
    if len(os.sys.argv) == 1:
        print("\nWelcome to ckart CLI.")
        print('Use "ckart -h" to learn more about ckart commands.\n')
        return

    if "-h" in os.sys.argv or "--help" in os.sys.argv:
        commands = [ 
            ["ckart heartbeat", "Check if server is online"], 
            ["ckart auth <token>", "Authenticate CLI session."], 
            ["ckart vms -h", "List all sub-commands to manage VMs"], 
            ["ckart providers", "List all sub-commands to manage Providers"], 
            ["ckart -h", "Help - list all commands for ckart CLI."], 
        ]
        print("\nAvailable commands for ckart CLI:\n")
        print(tabulate(commands, headers=["Command", "Description"]),"\n")
        return

    # Parse the arguments
    args = parser.parse_args()

    if os.getenv("CKART_SESSION") is None and args.command != "auth":
        print("Welcome to ckart CLI!")
        print("[-] No session found. Please login using 'ckart auth <token>'")
        print("[-] You can get this token from the ckart web app.")
        print("[-] For more information, visit: https://computekart.com/docs")
        exit(1)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

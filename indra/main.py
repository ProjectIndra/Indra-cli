import argparse
from tabulate import tabulate 
from indra.commands import create, ps, rm, run, heartbeat, providers, start_stop, connect, disconnect, auth

def main():
    parser = argparse.ArgumentParser(prog="indra", description="Indra CLI to manage VMs")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'vms' command
    vms_parser = subparsers.add_parser("vms", help="Manage VMs")
    vms_parser.add_argument("-l", "--list", action="store_true", help="List all commands for 'indra vms'")
    vms_parser.add_argument("-a", "--all", action="store_true", help="Show all VMs")
    vms_parser.add_argument("--create", type=str, help="Create a new VM with the given Provider ID")
    vms_parser.add_argument("--connect", type=str, help="Connect to VM WireGuard network")
    vms_parser.add_argument("--disconnect", type=str, help="Disconnect from VM WireGuard network")
    vms_parser.add_argument("--start", type=str, help="Start a VM")
    vms_parser.add_argument("--stop", type=str, help="Stop a VM")

    def vms_handle(args):
        if args.list:
            commands =[
                ["indra vms", "Show all active VMx"],
                ["indra vms -l or indra vms --list", "List all commands for 'indra vms'"],
                ["indra vms -a or indra vms --all", "List all VMs"],
                ["indra vms --create <provider_id>", "Create a new VM"],
                ["indra vms --connect <vm_id>", "Connect to WireGuard network"],
                ["indra vms --disconnect <vm_id>", "Disconnect from WireGuard network"],
                ["indra vms --start <vm_id>", "Start a VM"],
                ["indra vms --stop <vm_id>", "Stop a VM"],
            ]
            print("\nAvailable commands for 'indra vms':\n")
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
        else:
            ps.handle(args)

    vms_parser.set_defaults(func=vms_handle)

    # Heartbeat Command
    heartbeat_parser = subparsers.add_parser("heartbeat", help="Check if MGMT server is online")
    heartbeat_parser.set_defaults(func=heartbeat.handle)

    # Provider Command
    provider_parser = subparsers.add_parser("providers", help="Manage providers")
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

    # VM Removal Command
    rm_parser = subparsers.add_parser("rm", help="Remove a VM")
    rm_parser.add_argument("vm_name", type=str, help="VM Name to remove")
    rm_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force remove the VM"
    )
    rm_parser.set_defaults(func=rm.handle)

    # Auth Command
    auth_parser = subparsers.add_parser("auth", help="Authenticate with backend")
    auth_parser.add_argument("token", type=str, help="Authentication token")
    auth_parser.set_defaults(func=auth.handle)

    # Parse the arguments
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

import argparse
import os

from tabulate import tabulate

from ckart.commands import (
    auth,
    connect,
    create,
    disconnect,
    heartbeat,
    providers,
    ps,
    rm,
    start_stop,
    tunnel,
)
from ckart.env import load_env

# load_dotenv(os.path.expanduser("~/.ckart-cli/.env"))
# load_env(".env")
# env_path = os.path.expanduser("$HOME\.ckart-cli\.env")
env_path = os.path.join(os.path.expanduser(path="~"), ".ckart-cli", ".env")
print(f"Loading environment variables from: {env_path}")
load_env(env_path)
# print(os.getenv("MGMT_SERVER"))


def main():
    parser = argparse.ArgumentParser(
        prog="ckart", description="ckart CLI to manage VMs"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Auth Command
    auth_parser = subparsers.add_parser("auth", help="Authenticate cli session.")
    auth_parser.add_argument("token", type=str, help="Authentication token")
    auth_parser.set_defaults(func=auth.handle)

    # 'vms' command
    vms_parser = subparsers.add_parser("vms", help="Manage VMs.", add_help=False)
    vms_parser.add_argument("-a", "--all", action="store_true", help="Show all VMs")
    vms_parser.add_argument(
        "--create", type=str, help="Create a new VM with the given Provider ID"
    )
    vms_parser.add_argument(
        "--connect", type=str, help="Connect to VM WireGuard network"
    )
    vms_parser.add_argument(
        "--disconnect", type=str, help="Disconnect from VM WireGuard network"
    )
    vms_parser.add_argument("--start", type=str, help="Start a VM")
    vms_parser.add_argument("--stop", type=str, help="Stop a VM")
    vms_parser.add_argument("-rm", "--remove", type=str, help="Remove a VM")
    vms_parser.add_argument(
        "-f", "--force", action="store_true", help="Force remove a VM"
    )
    vms_parser.add_argument(
        "-h", "--help", action="store_true", help="Show help for 'ckart vms'"
    )

    def vms_handle(args):
        if args.help:
            commands = [
                ["ckart vms", "Show all active VMs"],
                ["ckart vms -a or ckart vms --all", "List all VMs"],
                ["ckart vms --create <provider_id>", "Create a new VM"],
                ["ckart vms --connect <vm_id>", "Connect to WireGuard network"],
                [
                    "ckart vms --disconnect <vm_id>",
                    "Disconnect from WireGuard network",
                ],
                ["ckart vms --start <vm_id>", "Start a VM"],
                ["ckart vms --stop <vm_id>", "Stop a VM"],
                ["ckart vms --remove <vm_id>", "Remove a VM"],
                ["ckart vms --remove -f or --force <vm_id>", "Force remove a VM"],
                ["ckart vms -h or ckart vms --help", "Show help for 'ckart vms'"],
            ]
            print("\nAvailable commands for 'ckart vms':\n")
            print(tabulate(commands, headers=["Command", "Description"]), "\n")
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
    heartbeat_parser = subparsers.add_parser(
        "heartbeat", help="Check if server is online."
    )
    heartbeat_parser.set_defaults(func=heartbeat.handle)

    # Provider Command
    provider_parser = subparsers.add_parser("providers", help="Manage providers.")
    provider_parser.add_argument(
        "-a", "--all", action="store_true", help="Get details of all providers"
    )
    provider_parser.add_argument(
        "-d",
        "--details",
        type=str,
        metavar="provider_id",
        help="Get details of a specific provider",
    )
    provider_parser.add_argument(
        "provider",
        type=str,
        nargs="?",
        help="Provider ID for querying specific provider",
    )
    provider_parser.add_argument(
        "-q",
        "--query",
        nargs=3,  # Expects three values: vcpus, ram, storage
        metavar=("vcpus", "ram", "storage"),
        type=int,
        help="Query providers with specific vCPUs, RAM, and Storage",
    )
    provider_parser.set_defaults(func=providers.handle)

    # Tunnel command
    tunnel_parser = subparsers.add_parser("tunnel", help="Manage Tunnel feature")
    tunnel_parser.add_argument(
        "--list",
        action="store_true",
        help="List all tunnel clients",
    )
    tunnel_parser.add_argument(
        "--add",
        metavar="token",
        type=str,
        help="Register/add tunnel using the provided token",
    )
    tunnel_parser.add_argument(
        "--connect",
        action="store_true",
        help="Expose local host and port to public URL",
    )
    tunnel_parser.add_argument(
        "--download",
        action="store_true",
        help="Download tunnel client jar",
    )
    tunnel_parser.add_argument(
        "--config",
        metavar="token",
        type=str,
        help="Set tunnel token in .env file",
    )
    tunnel_parser.add_argument(
        "--create",
        action="store_true",
        help="Create a new tunnel client and auto-config it",
    )
    tunnel_parser.add_argument(
        "--delete",
        metavar="tunnel_id",
        type=str,
        help="Delete a tunnel",
    )
    tunnel_parser.set_defaults(func=tunnel.handle)

    # Handle help manually to customize output only for top-level help
    if len(os.sys.argv) == 1:
        print("\nWelcome to ckart CLI.")
        print('Use "ckart -h" to learn more about ckart commands.\n')
        return

    # Only show global help if -h/--help is the only argument or is directly after the program name
    if len(os.sys.argv) == 2 and (os.sys.argv[1] == "-h" or os.sys.argv[1] == "--help"):
        commands = [
            ["ckart heartbeat", "Check if server is online"],
            ["ckart auth <token>", "Authenticate CLI session."],
            ["ckart vms -h", "List all sub-commands to manage VMs"],
            ["ckart providers", "List all sub-commands to manage Providers"],
            ["ckart tunnel --list", "List tunnel clients"],
            ["ckart tunnel --download", "Download tunnel client"],
            ["ckart tunnel --connect", "Expose local host to public URL"],
            ["ckart tunnel --config <token>", "Configure tunnel token"],
            ["ckart tunnel --create", "Create new tunnel client"],
            ["ckart tunnel --delete <id>", "Delete a tunnel"],
            ["ckart -h", "Help - list all commands for ckart CLI."],
        ]
        print("\nAvailable commands for ckart CLI:\n")
        print(tabulate(commands, headers=["Command", "Description"]), "\n")
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

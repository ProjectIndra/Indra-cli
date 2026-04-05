import argparse
import os
from ckart import output
from ckart.banner import show_banner
from ckart.commands import (
    auth,
    vms,
    heartbeat,
    providers,
    tunnel,
)
from ckart.env import load_env
import requests
import json

ENV = os.path.join(os.path.expanduser(path="~"), ".ckart-cli", ".env")
load_env(ENV)
_orig_request = requests.Session.request



def _debug_request(self, method, url, **kwargs):
    response = _orig_request(self, method, url, **kwargs)
    if os.getenv("MODE") == "DEBUG":
        output.plain(f"[DEBUG] {method.upper()} {url}")
        output.plain(f"[DEBUG] Status Code: {response.status_code}")
        try:
            output.plain(f"[DEBUG] Response JSON:\n{json.dumps(response.json(), indent=2)}")
        except Exception:
            output.plain(f"[DEBUG] Response Text:\n{response.text}")
    return response

requests.Session.request = _debug_request



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
    vms_parser.add_argument("-p", "--provider", type=str, help="Provider ID of the VM")
    vms_parser.add_argument(
        "-f", "--force", action="store_true", help="Force remove a VM"
    )
    vms_parser.add_argument(
        "-h", "--help", action="store_true", help="Show help for 'ckart vms'"
    )
    vms_parser.set_defaults(func=vms.handle)

    # Heartbeat Command
    heartbeat_parser = subparsers.add_parser(
        "heartbeat", help="Check if server is online."
    )
    heartbeat_parser.set_defaults(func=heartbeat.handle)

    # Provider Command
    provider_parser = subparsers.add_parser("providers", help="Manage providers.", add_help=False)
    provider_parser.add_argument(
        "-h", "--help", action="store_true", help="Show help for 'ckart providers'"
    )
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
    tunnel_parser = subparsers.add_parser("tunnel", help="Manage Tunnel feature", add_help=False)
    tunnel_parser.add_argument(
        "-h", "--help", action="store_true", help="Show help for 'ckart tunnel'"
    )
    tunnel_parser.add_argument(
        "--list",
        action="store_true",
        help="List all tunnel clients",
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
        help="Set tunnel token for auto-configuration",
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
        show_banner()
        output.plain("\nWelcome to ckart CLI.")
        output.plain('Use "ckart -h" to learn more about ckart commands.\n')
        return

    # Only show global help if -h/--help is the only argument or is directly after the program name
    if len(os.sys.argv) == 2 and (os.sys.argv[1] == "-h" or os.sys.argv[1] == "--help"):
        commands = [
            ["ckart heartbeat"      , "Check if server is online"],
            ["ckart auth <token>"   , "Authenticate CLI session from Manage CLIs page on computekart.com."],
            ["ckart vms -h"         , "List all sub-commands to manage VMs"],
            ["ckart providers -h"   , "List all sub-commands to manage Providers"],
            ["ckart tunnel -h"      , "List all sub-commands to manage Tunnel feature"],
            ["ckart -h"             , "Help - list all commands for ckart CLI."],
        ]
        output.plain("\nAvailable commands for ckart CLI:\n")
        output.table(commands, headers=["Command", "Description"])
        output.plain()
        return

    # Parse the arguments
    args = parser.parse_args()

    if os.getenv("CKART_SESSION") is None and args.command != "auth":
        output.plain("Welcome to ckart CLI!")
        output.error("No session found. Please login using 'ckart auth <token>'")
        output.info(
            "You can get this token from the ckart web app under Manage CLIs section."
        )
        output.info("For more information, visit: https://computekart.com/docs")
        exit(1)

    if hasattr(args, "func"):
        try:
            args.func(args)
        except KeyboardInterrupt:
            output.warning("Operation cancelled by user (Ctrl+C).")
            return
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Process interrupted by user.")
        os.sys.exit(0)

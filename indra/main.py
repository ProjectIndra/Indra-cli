import argparse
from indra.commands import ps, rm, add, run, heartbeat, providers, start_stop

def main():
    parser = argparse.ArgumentParser(prog="indra", description="Indra CLI to manage VMs")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'ps' command
    ps_parser = subparsers.add_parser("vms", help="List running VMs")
    ps_parser.add_argument("-a", "--all", action="store_true", help="Show all VMs")
    ps_parser.set_defaults(func=ps.handle)

    # Start VM Command
    start_parser = subparsers.add_parser("start", help="Start a VM")
    start_parser.add_argument("vm_id", type=int, help="VM ID to start")
    start_parser.set_defaults(command="start", func=start_stop.handle)

    # Stop VM Command
    stop_parser = subparsers.add_parser("stop", help="Stop a VM")
    stop_parser.add_argument("vm_id", type=int, help="VM ID to stop")
    stop_parser.set_defaults(command="stop", func=start_stop.handle)

    # # 'add' command
    # add_parser = subparsers.add_parser("add", help="Add a new VM")
    # add_parser.set_defaults(func=add.handle)

    # # 'run' command
    # run_parser = subparsers.add_parser("run", help="Run a VM")
    # run_parser.set_defaults(func=run.handle)

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
        type=int,
        metavar="provider_id",
        help="Get details of a specific provider"
    )
    provider_parser.add_argument(
        "provider",
        type=int,
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
    rm_parser.add_argument("vm_id", type=int, help="VM ID to remove")
    rm_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force remove the VM"
    )
    rm_parser.set_defaults(func=rm.handle)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

import argparse
from indra.commands import ps, rm, add, run, heartbeat, providers

def main():
    parser = argparse.ArgumentParser(prog="indra", description="Indra CLI to manage VMs")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'ps' command
    ps_parser = subparsers.add_parser("ps", help="List running VMs")
    ps_parser.add_argument("-a", "--all", action="store_true", help="Show all VMs")
    ps_parser.set_defaults(func=ps.handle)

    # # 'rm' command
    # rm_parser = subparsers.add_parser("rm", help="Remove a VM")
    # rm_parser.add_argument("token", type=str, help="Token of the VM to remove")
    # rm_parser.set_defaults(func=rm.handle)

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
    provider_parser = subparsers.add_parser("providers", help="Get provider details")

    # Optional argument: Fetch all providers
    provider_parser.add_argument("-a",
        "--all", 
        action="store_true", 
        help="Get details of all providers"
    )

    # Positional argument: Fetch specific provider (if provided)
    provider_parser.add_argument(
        "provider", 
        type=int, 
        nargs="?",
        help="Provider ID to fetch specific provider details"
    )
    provider_parser.add_argument(
        "-q", "--query",
        nargs=3,  # Expect two values: vcpus and ram
        metavar=("vcpus", "ram", "storage"),
        type=int,
        help="Query providers with specific vCPUs and RAM"
    )
    provider_parser.set_defaults(func=providers.handle)


    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

import argparse
from commands import ps, rm, add, run

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

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

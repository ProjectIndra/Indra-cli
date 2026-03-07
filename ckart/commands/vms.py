from ckart.commands import connect, create, disconnect, ps, rm, start_stop
from ckart import output


def handle(args):
    if args.help:
        commands = [
            ["ckart vms"											, "Show all active VMs"],
            ["ckart vms -a or ckart vms --all"						, "List all VMs"],
            ["ckart vms --create <provider_id>"						, "Create a new VM"],
            ["ckart vms --connect <vm_id>"							, "Connect to WireGuard network"],
            ["ckart vms --disconnect <vm_id>"						, "Disconnect from WireGuard network",],
            ["ckart vms --start <vm_id>"							, "Start a VM"],
            ["ckart vms --stop <vm_id>"								, "Stop a VM"],
            ["ckart vms --remove <vm_id>"							, "Remove a VM"],
            ["ckart vms --remove -f or --force <vm_id>"				, "Force remove a VM"],
            ["ckart vms -h or ckart vms --help"						, "Show help for 'ckart vms'"],
        ]
        output.plain("\nAvailable commands for 'ckart vms':\n")
        output.table(commands, headers=["Command", "Description"])
        output.plain()
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

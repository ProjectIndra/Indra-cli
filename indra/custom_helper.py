import argparse

class CustomHelpFormatter(argparse.HelpFormatter):
    def add_arguments(self, actions):
        # Skip the default "positional arguments" and "optional arguments" grouping
        for action in actions:
            if action.help != argparse.SUPPRESS:
                self._add_item(self._format_action, [action])

    def _format_usage(self, usage, actions, groups, prefix):
        # Custom usage line
        return super()._format_usage(usage, actions, groups, prefix)

    def format_help(self):
        help_str = super().format_help()
        lines = help_str.splitlines()

        # Find where to insert the command table
        usage_line = lines[0]
        description = lines[1] if len(lines) > 1 else ""
        command_table = (
            "\n    Commands         Description\n"
            "    ----------------------------------------------------\n"
            "    auth             Authenticate cli session.\n"
            "    vms              Manage VMs.\n"
            "    heartbeat        Check if server is online.\n"
            "    providers        Manage providers.\n"
        )
        remaining = "\n".join(lines[2:])

        return f"{usage_line}\n{description}\n{command_table}\n"

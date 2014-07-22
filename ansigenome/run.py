import os

import constants as c
import ui as ui
import utils as utils


class Run(object):
    def __init__(self, args, options):
        self.options = options
        self.roles_path = args[0]
        self.command = options.command

        self.execute_command()

    def execute_command(self):
        """
        Execute the shell command.
        """
        stderr = ""
        role_count = 0
        for role in utils.roles_dict(self.roles_path):
            self.command = self.command.replace("%role_name", role)
            (_, err) = utils.capture_shell("cd {0} && {1}".
                                           format(os.path.join(
                                                  self.roles_path, role),
                                                  self.command))

            stderr = err
            role_count += 1

        utils.exit_if_no_roles(role_count, self.roles_path)

        if len(stderr) > 0:
            ui.error(c.MESSAGES["run_error"], stderr[:-1])
        else:
            if not self.options.quiet:
                ui.ok(c.MESSAGES["run_success"].replace(
                    "%role_count", str(role_count)), self.options.command)

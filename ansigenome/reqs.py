import os

import utils as utils


default_yml_item = """

- src: '%src'
  scm: '%scm'
  version: '%version'
"""


class Reqs(object):
    """
    Create a requirements file meant to hold a list of all of your roles.
    """
    def __init__(self, args, options, config):
        self.roles = utils.roles_dict(args[0])
        self.out_file = options.out_file

        utils.exit_if_no_roles(len(self.roles.keys()), args[0])

        if options.format:
            self.format = options.format
        else:
            self.format = config["options"]["reqs_format"]

        self.src = config["scm"]["host"]
        self.scm = config["scm"]["type"]
        self.repo_prefix = config["scm"]["repo_prefix"]
        self.interactive_version = options.interactive_version

        if self.format == "yml" or self.format == "yaml":
            self.export_yml_reqs()
        else:
            self.export_txt_reqs()

    def export_yml_reqs(self):
        """
        Export the yaml version to stdout or requirements file.
        """
        role_lines = "---"

        for galaxy_role, role in sorted(self.roles.items()):
            yml_item = default_yml_item

            if self.src:
                if self.repo_prefix:
                    role = self.repo_prefix + role

                src = os.path.join(self.src, role)
            else:
                src = galaxy_role
            yml_item = yml_item.replace("%src", src)

            if self.scm:
                yml_item = yml_item.replace("%scm", self.scm)
            else:
                yml_item = yml_item.replace("scm: '%scm'\n", "")

            version = self.get_user_version(role)
            if version:
                yml_item = yml_item.replace("%version", version)
            else:
                yml_item = yml_item.replace("  version: '%version'\n", "")

            role_lines += "{0}".format(yml_item)

        if self.out_file:
            utils.string_to_file(self.out_file, role_lines)
        else:
            print role_lines

    def export_txt_reqs(self):
        """
        Export the text version to stdout or requirements file.
        """
        role_lines = ""

        for role in sorted(self.roles.keys()):
            version = self.get_user_version(role)

            if version:
                version = "," + version

            role_lines += "{0}{1}\n".format(role, version)

        if self.out_file:
            utils.string_to_file(self.out_file, role_lines)
        else:
            print role_lines

    def get_user_version(self, role):
        """
        Get the user defined version from stdin.
        """
        if self.interactive_version:
            return raw_input("{0}'s version []: ".format(role))

        return ""

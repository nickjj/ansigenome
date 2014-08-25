import os
import utils as utils


default_yml_item = """

- src: 'https://github.com/%github_username/%repo_name'
  version: '%branch'
"""


class Export(object):
    """
    Create a requirements file meant to hold a list of all of your roles.
    """
    def __init__(self, args, options):
        self.roles = utils.roles_dict(args[0])
        self.out_directory = options.out_dir
        self.github_username = options.github_username
        self.branch = options.branch
        self.repo_prefix = options.repo_prefix
        self.out_path = os.path.join(self.out_directory, "requirements")

        if options.yaml:
            self.out_path += ".yml"
            self.export_yml_requirements()
        else:
            self.out_path += ".txt"
            self.export_txt_requirements()

    def export_yml_requirements(self):
        """
        Export the yaml version of the requirements file.

        This only supports github.com for now because the documentation on
        how to use bitbucket seems a bit unstable.
        """
        updated_roles = "---"

        for _, role in self.roles.items():
            if self.repo_prefix:
                role = self.repo_prefix + role

            yml_item = default_yml_item

            yml_item = yml_item.replace("%github_username",
                                        self.github_username)
            yml_item = yml_item.replace("%branch", self.branch)
            yml_item = yml_item.replace("%repo_name", role)

            updated_roles += "{0}".format(yml_item)

        utils.string_to_file(self.out_path, updated_roles)

    def export_txt_requirements(self):
        """
        Export the text version of the requirements file.
        """
        updated_roles = ""

        for role in self.roles.keys():
            updated_roles += "{0},{1}\n".format(role, self.branch)

        utils.string_to_file(self.out_path, updated_roles)

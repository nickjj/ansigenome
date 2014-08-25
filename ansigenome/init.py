import os
import sys

import constants as c
import ui as ui
import utils as utils


default_mainyml_template = """---
# role: %repo_name

# %values go here
"""

default_travisyml_template = """---
language: "python"
python: "2.7"

env:
  - SITE_AND_INVENTORY="tests/main.yml -i tests/inventory"

install:
  - "pip install ansible"
  - "printf '[defaults]\\nroles_path = ../' > ansible.cfg"

script:
  - "ansible-playbook $SITE_AND_INVENTORY --syntax-check"
  - "ansible-playbook $SITE_AND_INVENTORY --connection=local -vvvv"
  - >
    ansible-playbook $SITE_AND_INVENTORY --connection=local
    | grep -q 'changed=0.*failed=0'
    && (echo 'Idempotence test: PASS' && exit 0)
    || (echo 'Idempotence test: FAIL' && exit 1)
"""

default_travis_main_template = """---
- hosts: localhost
  remote_user: travis
  sudo: true

  roles:
    - %repo_name
"""


class Init(object):
    """
    Create a new role, this is meant to replace ansible-galaxy init.
    """
    def __init__(self, args, options):
        self.output_path = args[0]
        self.role_name = os.path.basename(self.output_path)

        if options.repo_name:
            self.repo_name = options.repo_name
        else:
            self.repo_name = self.role_name

        self.exit_if_path_exists()
        self.create_skeleton()
        self.create_tests()

    def exit_if_path_exists(self):
        """
        Exit early if the path cannot be found.
        """
        if os.path.exists(self.output_path):
            ui.error(c.MESSAGES["path_exists"], self.output_path)
            sys.exit(1)

    def create_skeleton(self):
        """
        Create the role's directory and file structure.
        """
        for folder in c.ANSIBLE_FOLDERS:
            create_folder_path = os.path.join(self.output_path, folder)
            utils.mkdir_p(create_folder_path)

            mainyml_template = default_mainyml_template.replace(
                "%repo_name", self.repo_name)
            mainyml_template = mainyml_template.replace(
                "%values", folder)

            if not folder == "templates" and not folder == "meta":
                utils.string_to_file(os.path.join(create_folder_path,
                                                  "main.yml"),
                                     mainyml_template)

    def create_tests(self):
        """
        Create a travis test case which tests for idempotency.
        """
        utils.string_to_file(os.path.join(self.output_path, ".travis.yml"),
                             default_travisyml_template)
        utils.string_to_file(os.path.join(self.output_path, "tests",
                             "inventory"), "localhost\n")
        utils.string_to_file(os.path.join(self.output_path, "tests",
                             "main.yml"),
                             default_travis_main_template.
                             replace("%repo_name", self.repo_name))

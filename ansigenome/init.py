import os
import sys

from datetime import date

import constants as c
import ui as ui
import utils as utils


default_mainyml_template = """---

"""

default_travisyml_template = """---

language: 'python'
python: '2.7'

virtualenv:
  system_site_packages: true

before_install: True
install: True

script:
  - 'git clone --depth 1 %test_runner'
  - 'cd %basename ; ./runner -r %role_url'
"""

default_testyml_template = """---

#!/bin/bash

# test: Test %role
# Copyright (C) %year %author <%email>

. "lib/test"

assert_playbook_runs
assert_playbook_idempotent
"""


class Init(object):
    """
    Create a new role, this is meant to replace ansible-galaxy init.
    """
    def __init__(self, args, options, config):
        self.output_path = args[0]
        self.options = options
        self.config = config
        self.role_name = os.path.basename(self.output_path)
        self.normalized_role = utils.normalize_role(self.role_name,
                                                    self.config)

        self.exit_if_path_exists()
        self.create_skeleton()
        self.create_travis_config()
        self.create_test_case()

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
        utils.string_to_file(os.path.join(self.output_path, "VERSION"),
                             "master\n")

        for folder in c.ANSIBLE_FOLDERS:
            create_folder_path = os.path.join(self.output_path, folder)
            utils.mkdir_p(create_folder_path)

            mainyml_template = default_mainyml_template.replace(
                "%role_name", self.role_name)
            mainyml_template = mainyml_template.replace(
                "%values", folder)

            out_path = os.path.join(create_folder_path, "main.yml")

            if folder not in ("templates", "meta", "tests", "files"):
                utils.string_to_file(out_path, mainyml_template)

            if folder == "meta":
                utils.create_meta_main(out_path,
                                       self.config, self.role_name,
                                       self.options.galaxy_categories)

    def create_travis_config(self):
        """
        Create a travis test setup.
        """
        test_runner = self.config["options_test_runner"]

        role_url = "{0}".format(os.path.join(self.config["scm_host"],
                                             self.config["scm_user"],
                                             self.config["scm_repo_prefix"] +
                                             self.normalized_role))

        travisyml_template = default_travisyml_template.replace(
            "%test_runner", test_runner)
        travisyml_template = travisyml_template.replace(
            "%basename", test_runner.split("/")[-1])
        travisyml_template = travisyml_template.replace(
            "%role_url", role_url)

        utils.string_to_file(os.path.join(self.output_path, ".travis.yml"),
                             travisyml_template)

    def create_test_case(self):
        """
        Create a test case.
        """
        testyml_template = default_testyml_template.replace(
            "%role", self.normalized_role)
        testyml_template = testyml_template.replace(
            "%year", str(date.today().year))
        testyml_template = testyml_template.replace(
            "%author", self.config["author_name"])
        testyml_template = testyml_template.replace(
            "%email", self.config["author_email"])

        utils.mkdir_p(os.path.join(self.output_path,
                                   "tests", "inventory", "group_vars"))

        utils.mkdir_p(os.path.join(self.output_path,
                                   "tests", "inventory", "host_vars"))

        hosts = "placeholder_fqdn\n"
        utils.string_to_file(os.path.join(self.output_path,
                                          "tests", "inventory", "hosts"),
                             hosts)

        test_file = os.path.join(self.output_path, "tests", "test")
        utils.string_to_file(test_file, testyml_template)

        os.chmod(test_file, 0755)

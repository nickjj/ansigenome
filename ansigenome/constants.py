import os.path

import utils


GIT_AUTHOR = utils.capture_shell("git config user.name")[0][:-1]
GIT_EMAIL = utils.capture_shell("git config user.email")[0][:-1]

MODULE_DIR = os.path.join(os.path.dirname(__file__), os.path.pardir)

VALID_ACTIONS = ("config", "scan", "gendoc", "genmeta",
                 "reqs", "init", "run", "dump")

CONFIG_FILE = ".ansigenome.conf"

CONFIG_DEFAULT_PATH = os.path.expanduser("~")

CONFIG_QUESTIONS = [
    (
        "author", (
            ["name", "What's your name?", GIT_AUTHOR],
            ["company", "Which company do you belong to?", ""],
            ["url", "What's your website?", ""],
            ["email", "What's your e-mail address?", GIT_EMAIL],
            ["twitter", "What's your twitter name without the @?", ""]
        )
    ),
    (
        "license", (
            ["type", "Which license are you using?", "MIT"],
            ["url", "What's the license's URL?",
                    "https://tldrlegal.com/license/mit-license"]
        )
    ),
    (
        "scm", (
            ["type", "Which source control are you using?", "git"],
            ["host", "Which host are you using for SCM?",
                     "https://github.com"],
            ["user", "What's your user name on the above host?", "someone"],
            ["repo_prefix", "How are your roles prefixed in the url?",
                            "ansible-"]
        )

    ),
    (
        "options", (
            ["reqs_format", "Default requirements file format? yml | txt",
                            "yml"],
        ),
    ),
]

CONFIG_MUST_CONTAIN = {
    "author": {
        "name": "str",
        "company": "str",
        "url": "str",
        "email": "str",
        "twitter": "str",
    },
    "license": {
        "type": "str",
        "url": "str",
    },
    "scm": {
        "type": "str",
        "host": "str",
        "user": "str",
        "repo_prefix": "str",
    },
    "options": {
        "readme_template": "str",
        "travis": "bool",
        "quiet": "bool",
        "reqs_format": "str",
        "dump_with_readme": "bool",
        "test_runner": "str",
    },
}

ANSIBLE_FOLDERS = ("defaults", "handlers", "meta",
                   "tasks", "templates", "tests", "vars")

README_TEMPLATE_PATH = os.path.join(MODULE_DIR,
                                    "templates", "README.md.j2")

DEFAULT_META_FILE = """---

dependencies: []

galaxy_info:
  author: '%author_name'
  description: '%role_name described in 1 sentence...'
  company: '%author_company'
  license: '%license_type'
  min_ansible_version: '1.7.1'
  platforms:
    - name: Ubuntu
      versions:
        - precise
        - trusty
    - name: Debian
      versions:
        - wheezy
        - jessie
  categories: [%categories]

ansigenome_info:
  galaxy_id: ''

  travis: True

  synopsis: |
    %role_name described in a few paragraphs....

  usage: |
    Describe how to use %role_name...

  #custom: |
  #  Any custom output you want after the usage section...
"""


LOG_COLOR = {
    "ok": "green",
    "skipped": "cyan",
    "changed": "yellow",
    "missing_readme": "yellow",
    "missing_meta": "red",
}

MESSAGES = {
    "empty_roles_path": "No roles were found at this path:",
    "invalid_config": "'%key' was missing from the following config, please" +
    " fix it:",
    "path_missing": "The following path could not be found:",
    "path_exists": "The following path already exists:",
    "path_unmakable": "The following error occurred when trying to " +
    "create this path:",
    "url_unreachable": "The following url was unreachable:",
    "yaml_error": "%file contains 1 or more syntax errors:",
    "template_error": "%file contains 1 or more syntax errors:",
    "run_success": "%role_count roles were modified with this shell command:",
    "run_error": "There was an error running this shell command:",
    "dump_success": "The role stats were dumped as json to:",
    "help_config": "create a necessary config file to make ansigenome work",
    "help_scan": "scan a path containing Ansible roles and report back " +
    "useful stats",
    "help_gendoc": "generate a README from the meta file for each role",
    "help_genmeta": "augment existing meta files to be compatible with" +
    " Ansigenome",
    "help_reqs": "export a path of roles to a file to be consumed" +
    " by ansible-galaxy install -r",
    "help_init": "init new roles with a custom meta file and tests",
    "help_run": "run shell commands inside of each role's directory",
    "help_dump": "dump a json file containing every stat it gathers from " +
    "the scan path"
}

TEST_PATH = os.path.join(os.path.sep, "tmp", "ansigenome")

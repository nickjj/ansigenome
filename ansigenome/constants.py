import pkg_resources
import os.path

import utils


GIT_AUTHOR = utils.capture_shell("git config user.name")[0][:-1]
GIT_EMAIL = utils.capture_shell("git config user.email")[0][:-1]

PACKAGE_RESOURCE = pkg_resources.resource_filename(__name__, "data")

VALID_ACTIONS = ("config", "scan", "gendoc", "genmeta",
                 "export", "init", "run")

ALLOWED_GENDOC_FORMATS = ("rst", "md")
ALLOWED_GRAPH_FORMATS = ("png", "dot")
ALLOWED_REQS_FORMATS = ("txt", "yml")
ALLOWED_DUMP_FORMATS = ("json")

LICENSE_TYPES = [
    ["MIT", "https://tldrlegal.com/license/mit-license"],
    ["GPLv2", "https://tldrlegal.com/license/gnu-general-public-license-v2"],
    ["GPLv3", "https://tldrlegal.com/license/" +
              "gnu-general-public-license-v3-%28gpl-3%29"],
    ["LGPL", "https://tldrlegal.com/license/" +
             "gnu-lesser-general-public-license-v2.1-(lgpl-2.1)"],
    ["Apache-2.0", "https://tldrlegal.com/license/" +
                   "apache-license-2.0-%28apache-2.0%29"],
    ["BSDv2", "https://tldrlegal.com/license/bsd-2-clause-license-(freebsd)"],
    ["BSDv3", "https://tldrlegal.com/license/bsd-3-clause-license-(revised)"],
    ["Other", "https://tldrlegal.com/license/" +
              "do-what-the-f*ck-you-want-to-public-license-%28wtfpl%29"],
]

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
        "scm", (
            ["type", "Which source control are you using?", "git"],
            ["host", "Which host are you using for SCM?",
                     "https://github.com"],
            ["user", "What's your user name on the above host?", "someone"],
            ["repo_prefix", "How are your roles prefixed in the url?",
                            "ansible-"]
        )

    ),
]

CONFIG_MULTIPLE_CHOICE_QUESTIONS = [
    (
        "license", (
            [8, "Pick a license type by choosing a number:\n\n" +
             "  1. MIT\n  2. GPLv2\n  3. GPLv3\n" +
             "  4. LGPL\n  5. Apache-2.0\n" +
             "  6. BSDv2\n  7. BSDv3\n  8. Other\n\n"]
        )
    ),
]

CONFIG_DEFAULTS = {
    "author_name": "",
    "author_company": "",
    "author_url": "",
    "author_email": "",
    "author_twitter": "",
    "license_type": "",
    "license_url": "",
    "scm_type": "",
    "scm_host": "",
    "scm_user": "",
    "scm_repo_prefix": "",
    "options_readme_template": "",
    "options_travis": True,
    "options_quiet": False,
    "options_test_runner": "https://github.com/nickjj/rolespec",
    "default_format_gendoc": ALLOWED_GENDOC_FORMATS[0],
    "default_format_graph": ALLOWED_GRAPH_FORMATS[0],
    "default_format_reqs": ALLOWED_REQS_FORMATS[0],
    "default_format_dump": ALLOWED_DUMP_FORMATS,
    "graphviz_size": "15,8",
    "graphviz_dpi": 130,
    "graphviz_flags": "",
}

ANSIBLE_FOLDERS = ("defaults", "handlers", "meta",
                   "tasks", "templates", "tests", "vars", "files")

README_RST_TEMPLATE_PATH = os.path.join(PACKAGE_RESOURCE, "README.rst.j2")
README_MD_TEMPLATE_PATH = os.path.join(PACKAGE_RESOURCE, "README.md.j2")

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
    "invalid_config": "'%key' are missing from the following config, please" +
    " fix it:",
    "config_upgraded": "Your config file has been updated to include the" +
    " following new fields:",
    "path_missing": "The following path could not be found:",
    "path_exists": "The following path already exists:",
    "path_unmakable": "The following error occurred when trying to " +
    "create this path:",
    "url_unreachable": "The following url was unreachable:",
    "yaml_error": "%file contains 1 or more syntax errors:",
    "template_error": "Your template(s) contain 1 or more syntax errors:",
    "template_extender_missing": "The following template could not be found:",
    "png_missing_out": "You must supply -o <file> to write the png file",
    "dot_missing": "To export a PNG graph you must install graphviz",
    "run_success": "%role_count roles were modified with this shell command:",
    "run_error": "There was an error running this shell command:",
    "help_config": "create a necessary config file to make ansigenome work",
    "help_scan": "scan a path containing Ansible roles and report back " +
    "useful stats",
    "help_gendoc": "generate a README from the meta file for each role",
    "help_genmeta": "augment existing meta files to be compatible with" +
    " Ansigenome",
    "help_export": "export roles to a dependency graph, requirements file" +
    " and more",
    "help_init": "init new roles with a custom meta file and tests",
    "help_run": "run shell commands inside of each role's directory",
}

TEST_PATH = os.path.join(os.path.sep, "tmp", "ansigenome")

X11_COLORS = utils.file_to_list(os.path.join(PACKAGE_RESOURCE, "colors"))

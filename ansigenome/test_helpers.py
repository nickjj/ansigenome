import difflib
import json
import random
import os
import shutil
import string

from pprint import pprint

import ansigenome.utils as utils


CONFIG_TEMPLATE = """---

author_company: Acme Inc.
author_email: test@user.com
author_name: Test User
author_twitter: testuser
author_url: http://testuser

license_type: MIT
license_url: https://tldrlegal.com/license/mit-license

options_readme_template: ''
options_travis: true
options_quiet: false
options_test_runner: http://foo

default_format_gendoc: rst
default_format_graph: dot
default_format_reqs: txt
default_format_dump: json

scm_host: https://github.com
scm_repo_prefix: ansible-
scm_type: git
scm_user: testuser

graphviz_size: 15,8
graphviz_dpi: 130
graphviz_flags: ''
"""

DEFAULTS_TEMPLATE = """---
foo: bar
list:
  one: 1
  two: 2
  three: 3



# comment
baz: qux
"""

TASKS_TEMPLATE = """---
- set_fact:
  unix_is_cool: "who | grep -i blonde | date; cd ~; unzip; touch"

- set_almost_fact:
  command: "echo 'nope, not quite'"

- set_fact:
  duplicate: "not yet"

- set_fact:
  duplicate: "this should not be counted"
"""

META_TEMPLATE = """---
dependencies: []
galaxy_info: {}
ansigenome_info: {}
"""

META_TEMPLATE_FULL = """---

dependencies:
  - role: none.at_all
  - role: tear.drinker

galaxy_info:
  author: 'Chuck Norris'
  description: 'Just reading this makes you immune to death'
  company: 'Impossible'
  license: 'Death by chest hair inhalation if one does not agree'
  min_ansible_version: 'Everywhere and anything'
  platforms:
    - name: TheUniverse
  categories: [ deadly ]

ansigenome_info:
  galaxy_id: "infinity"

  travis: True

  license_url: 'There are no protocols that can withstand this license'

  authors:
    - name: 'Chuck Norris'
      url: "Ask me again for this and I'll penetrate your face with my fists"
      email: "I don't do e-mail, my mustache communicates via telekinesis"
      twitter: ''

  usage: |
    You don't use this role, it imposes itself on everyone and everything.

  custom: |
    There was a day where I once destroyed a country just by pooping.
"""


def rmrf(path):
    """
    Delete an entire path without warning.
    """
    shutil.rmtree(path)


def random_string(length=8):
    """
    Generate a random string.
    """
    return "".join(random.choice(
        string.ascii_lowercase) for _ in range(length))


def create_roles(path, number=2):
    """
    Create a number of roles.
    """
    role_names = []

    for i in range(number):
        full_path = os.path.join(path, random_string())

        utils.capture_shell("ansigenome init {0} -c system".format(full_path))

        role_names.append(os.path.basename(full_path))

    return role_names


def create_ansigenome_config(test_path):
    """
    Create a config file to use for each test.
    """
    utils.string_to_file(test_path, CONFIG_TEMPLATE)


def json_to_dict(input):
    """
    Return a dict from json.
    """
    return json.loads(input)


def print_out(title, out):
    """
    Print the output with borders.
    """
    print
    print "".join("=" * 79)
    print title
    print "".join("=" * 79)
    print out
    print "".join("=" * 79)


def populate_dict_with_files(test_path, roles, the_dict, path, tag=""):
    """
    Populate the dict to store the contents of each role's file.
    """
    print
    for role in roles:
        role_path = os.path.join(test_path, role)

        the_dict[role + tag] = utils.file_to_string(os.path.join(
            role_path, path)).splitlines(1)


def run_diff_on(the_dict, file, tag=""):
    """
    Print a context diff on 2 strings.
    """
    diff = []

    for key, values in the_dict.iteritems():
        if tag not in key:
            diff = list(difflib.context_diff(the_dict[key],
                        the_dict[key + tag]))
            print "DIFF for {0}'s {1}:".format(key, file)
            if len(diff) > 0:
                pprint(diff)
            else:
                print "[no differences]"
            print

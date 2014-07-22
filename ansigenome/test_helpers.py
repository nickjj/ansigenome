import json
import random
import os
import shutil
import string

import ansigenome.utils as utils


DEFAULTS_TEMPLATE = """---
foo: bar
list:
  one: 1
  two: 2
  three: 3



# comment
 a spaced variable should not be counted
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
galaxy_info: {}
dependencies: []
meta_info: {}
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

        utils.capture_shell("ansigenome init {0}".format(full_path))

        role_names.append(os.path.basename(full_path))

    return role_names


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

import errno
import json
import os
import re
import subprocess
import sys
import urllib2
import yaml

from jinja2 import Template

import constants as c
import ui as ui


# ------------------------------------------------------------------------
# file i/o
# ------------------------------------------------------------------------


def mkdir_p(path):
    """
    Emulate the behavior of mkdir -p.
    """
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            ui.error(c.MESSAGES["path_unmakable"], err)
            sys.exit(1)


def string_to_file(path, input):
    """
    Write a file from a given string.
    """
    mkdir_p(os.path.dirname(path))

    with open(path, "w+") as file:
        file.write(input)


def file_to_string(path):
    """
    Return the contents of a file when given a path.
    """
    if not os.path.exists(path):
        ui.error(c.MESSAGES["path_missing"], path)
        sys.exit(1)

    with open(path, "r") as contents:
        return contents.read()


def dict_to_json(input):
    """
    Return json from a dict.
    """
    return json.dumps(input)


def url_to_string(url):
    """
    Return the contents of a web site url as a string.
    """
    try:
        page = urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError) as err:
        ui.error(c.MESSAGES["url_unreachable"], err)
        sys.exit(1)

    return page


def template(source):
    """
    Return a jinja2 template instance from a path or url.
    """
    if "://" in source:
        contents = url_to_string(source)
    else:
        contents = file_to_string(source)

    try:
        return Template(contents)
    except Exception as err:
        file = os.path.basename(source)
        ui.error(c.MESSAGES["template_error"].replace("%file", file), err)
        sys.exit(1)


def files_in_path(path):
    """
    Return a list of all files in a path but exclude git folders.
    """
    aggregated_files = []

    for dir_, _, files in os.walk(path):
        for file in files:
            relative_dir = os.path.relpath(dir_, path)

            if ".git" not in relative_dir:
                relative_file = os.path.join(relative_dir, file)
                aggregated_files.append(relative_file)

    return aggregated_files


def exit_if_path_not_found(path):
    """
    Exit if the path is not found.
    """
    if not os.path.exists(path):
        ui.error(c.MESSAGES["path_missing"], path)
        sys.exit(1)


def ask(question, default):
    result = raw_input("{0} [{1}]: ".format(question, default))

    if not result:
        result = default

    return result

# ------------------------------------------------------------------------
# yaml
# ------------------------------------------------------------------------


def yaml_load(path, input="", err_quit=False):
    """
    Return a yaml dict from a file or string with error handling.
    """
    try:
        if len(input) > 0:
            return yaml.load(input)
        else:
            return yaml.load(file_to_string(path))
    except Exception as err:
        file = os.path.basename(path)
        ui.error("",
                 c.MESSAGES["yaml_error"].replace("%file", file), err,
                 "")

        if err_quit:
            sys.exit(1)

        return False


def to_nice_yaml(yaml_input, indentation=2):
    """
    Return condensed yaml into human readable yaml.
    """
    return yaml.safe_dump(yaml_input, indent=indentation,
                          allow_unicode=True, default_flow_style=False)

# ------------------------------------------------------------------------
# process capturing and detection
# ------------------------------------------------------------------------


def capture_shell(command):
    """
    Return the stdout/stderr from a command.
    """
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)

    return proc.communicate()

# ------------------------------------------------------------------------
# general
# ------------------------------------------------------------------------


def keys_in_dict(d, parent_key, keys):
    """
    Create a list of keys from a dict recursively.
    """
    for key, value in d.iteritems():
        if isinstance(value, dict):
            keys_in_dict(value, key, keys)
        else:
            if parent_key:
                prefix = parent_key + "."
            else:
                prefix = ""

            keys.append(prefix + key)

    return keys


def swap_yaml_string(file_path, swaps):
    """
    Swap a string in a yaml file without touching the existing formatting.
    """
    original_file = file_to_string(file_path)
    new_file = original_file
    changed = False

    for item in swaps:
        match = re.compile(r'(?<={0}: )(["\']?)(.*)\1'.format(item[0]),
                           re.MULTILINE)

        new_file = re.sub(match, item[1], new_file)

    if new_file != original_file:
        changed = True

    string_to_file(file_path, new_file)

    return (new_file, changed)


# ------------------------------------------------------------------------
# ansigenome specific
# ------------------------------------------------------------------------


def exit_if_no_roles(roles_count, roles_path):
    """
    Exit if there were no roles found.
    """
    if roles_count == 0:
        ui.warn(c.MESSAGES["empty_roles_path"], roles_path)
        sys.exit()


def roles_dict(path, repo_prefix=""):
    """
    Return a dict of role names and repo paths.
    """
    exit_if_path_not_found(path)

    aggregated_roles = {}

    roles = os.walk(path).next()[1]

    for role in roles:
        if is_role(os.path.join(path, role)):
            if isinstance(role, basestring):
                role_url_ready = role_name(role).replace("_", "-")
                role_repo = "{0}{1}".format(repo_prefix, role_url_ready)

                aggregated_roles[role] = role_repo

    return aggregated_roles


def role_name(role):
    """
    Return the role name from a folder name.
    """
    if "." in role:
        return role.split(".")[1]

    return role


def is_role(path):
    """
    Determine if a path is an ansible role.
    """
    seems_legit = False
    for folder in c.ANSIBLE_FOLDERS:
        if os.path.exists(os.path.join(path, folder)):
            seems_legit = True

    return seems_legit


def stripped_args(args):
    """
    Return the stripped version of the arguments.
    """
    stripped_args = []
    for arg in args:
        stripped_args.append(arg.strip())

    return stripped_args


def normalize_role(role, config):
    """
    Normalize a role name.
    """
    scm = config["scm"]

    if role.startswith(scm["repo_prefix"]):
        role_name = role.replace(scm["repo_prefix"], "")
    else:
        if "." in role:
            galaxy_prefix = "{0}.".format(scm["user"])
            role_name = role.replace(galaxy_prefix, "")
        else:
            role_name = role

    return role_name


def create_meta_main(create_path, config, role, categories):
    """
    Create a meta template.
    """
    meta_file = c.DEFAULT_META_FILE.replace(
        "%author_name", config["author"]["name"])
    meta_file = meta_file.replace(
        "%author_company", config["author"]["company"])
    meta_file = meta_file.replace("%license_type", config["license"]["type"])
    meta_file = meta_file.replace("%role_name", role)

    # Normalize the category so %categories always gets replaced.
    if not categories:
        categories = ""

    meta_file = meta_file.replace("%categories", categories)

    string_to_file(create_path, meta_file)

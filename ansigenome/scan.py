import re
import os
import sys

import constants as c
import ui as ui
import utils as utils

from ansigenome.export import Export


class Scan(object):
    """
    Loop over each role on the roles path and report back stats on them.
    """
    def __init__(self, args, options, config,
                 gendoc=False, genmeta=False, export=False):
        self.roles_path = args[0]

        self.options = options
        self.config = config
        self.gendoc = gendoc
        self.genmeta = genmeta
        self.export = export

        # set the readme output format
        self.readme_format = c.ALLOWED_GENDOC_FORMATS[0]

        self.roles = utils.roles_dict(self.roles_path, "")

        if self.options.limit:
            self.limit_roles()

        utils.exit_if_no_roles(len(self.roles.keys()), self.roles_path)

        self.regex_facts = re.compile(r"set_fact:\w+")
        self.paths = {}

        # default values for the role report
        self.defaults = ""
        self.dependencies = []
        self.all_files = []
        self.yaml_files = []

        # only load and validate the readme when generating docs
        if self.gendoc:
            # only change the format if it is different than the default
            if not self.options.format == self.readme_format:
                self.readme_format = self.options.format

            extend_path = self.config["options_readme_template"]

            if self.readme_format == "rst":
                readme_source = c.README_RST_TEMPLATE_PATH
            else:
                readme_source = c.README_MD_TEMPLATE_PATH

            self.readme_template = utils.template(readme_source, extend_path,
                                                  self.readme_format)

        self.report = {
            "totals": {
                "roles": 0,
                "dependencies": 0,
                "defaults": 0,
                "facts": 0,
                "files": 0,
                "lines": 0,
            },
            "state": {
                "ok_role": 0,
                "skipped_role": 0,
                "changed_role": 0,
                "missing_readme_role": 0,
                "missing_meta_role": 0,
            },
            "roles": {},
            "stats": {
                "longest_role_name_length": len(max(self.roles, key=len)),
            }
        }

        self.scan_roles()

        if self.export:
            self.export_roles()

    def limit_roles(self):
        """
        Limit the roles being scanned.
        """
        new_roles = {}
        roles = self.options.limit.split(",")

        for key, value in self.roles.iteritems():
            for role in roles:
                role = role.strip()
                if key == role:
                    new_roles[key] = value

        self.roles = new_roles

    def scan_roles(self):
        """
        Iterate over each role and report its stats.
        """
        for key, value in sorted(self.roles.iteritems()):
            self.paths["role"] = os.path.join(self.roles_path, key)
            self.paths["meta"] = os.path.join(self.paths["role"], "meta",
                                              "main.yml")
            self.paths["readme"] = os.path.join(self.paths["role"],
                                                "README.{0}"
                                                .format(self.readme_format))
            self.paths["defaults"] = os.path.join(self.paths["role"],
                                                  "defaults", "main.yml")

            self.report["roles"][key] = self.report_role(key)

            # we are writing a readme file which means the state of the role
            # needs to be updated before it gets output by the ui
            if self.gendoc:
                if self.valid_meta(key):
                    self.make_meta_dict_consistent()
                    self.set_readme_template_vars(key, value)
                    self.write_readme(key)
            # only load the meta file when generating meta files
            elif self.genmeta:
                self.make_or_augment_meta(key)
                if self.valid_meta(key):
                    self.make_meta_dict_consistent()
                    self.write_meta(key)
            else:
                self.update_scan_report(key)

            if not self.config["options_quiet"] and not self.export:
                ui.role(key,
                        self.report["roles"][key],
                        self.report["stats"]["longest_role_name_length"])

        self.tally_role_columns()

        # below this point is only UI output, so we can return
        if self.config["options_quiet"] or self.export:
            return

        ui.totals(self.report["totals"],
                  len(self.report["roles"].keys()),
                  self.report["stats"]["longest_role_name_length"])

        if self.gendoc:
            ui.gen_totals(self.report["state"], "readme")
        elif self.genmeta:
            ui.gen_totals(self.report["state"], "meta")
        else:
            ui.scan_totals(self.report["state"])

    def export_roles(self):
        """
        Export the roles to one of the export types.
        """
        # prepare the report by removing unnecessary fields
        del self.report["state"]
        del self.report["stats"]
        for role in self.report["roles"]:
            del self.report["roles"][role]["state"]

            defaults_path = os.path.join(self.roles_path, role,
                                         "defaults", "main.yml")
            if os.path.exists(defaults_path):
                defaults = self.report["roles"][role]["defaults"]
                self.report["roles"][role]["defaults"] = \
                    utils.yaml_load("", defaults)

        Export(self.roles_path, self.report, self.config, self.options)

    def report_role(self, role):
        """
        Return the fields gathered.
        """
        self.yaml_files = []

        fields = {
            "state": "skipped",
            "total_files": self.gather_files(),
            "total_lines": self.gather_lines(),
            "total_facts": self.gather_facts(),
            "total_defaults": self.gather_defaults(),
            "facts": self.facts,
            "defaults": self.defaults,
            "meta": self.gather_meta(),
            "readme": self.gather_readme(),
            "dependencies": self.dependencies,
            "total_dependencies": len(self.dependencies)
        }

        return fields

    def gather_meta(self):
        """
        Return the meta file.
        """
        if not os.path.exists(self.paths["meta"]):
            return ""

        meta_dict = utils.yaml_load(self.paths["meta"])

        # gather the dependencies
        if meta_dict and "dependencies" in meta_dict:
            # create a simple list of each role that is a dependency
            dep_list = []

            for dependency in meta_dict["dependencies"]:
                if type(dependency) is dict:
                    dep_list.append(dependency["role"])
                else:
                    dep_list.append(dependency)

            # unique set of dependencies
            meta_dict["dependencies"] = list(set(dep_list))

            self.dependencies = meta_dict["dependencies"]
        else:
            self.dependencies = []

        return utils.file_to_string(self.paths["meta"])

    def gather_readme(self):
        """
        Return the readme file.
        """
        if not os.path.exists(self.paths["readme"]):
            return ""

        return utils.file_to_string(self.paths["readme"])

    def gather_defaults(self):
        """
        Return the number of default variables.
        """
        total_defaults = 0
        defaults_lines = []

        if not os.path.exists(self.paths["defaults"]):
            # reset the defaults if no defaults were found
            self.defaults = ""
            return 0

        file = open(self.paths["defaults"], "r")
        for line in file:
            if len(line) > 0:
                first_char = line[0]
            else:
                first_char = ""

            defaults_lines.append(line)

            if (first_char != "#" and first_char != "-" and
                    first_char != " " and
                    first_char != "\r" and
                    first_char != "\n" and
                    first_char != "\t"):
                total_defaults += 1
        file.close()

        self.defaults = "".join(defaults_lines)

        return total_defaults

    def gather_facts(self):
        """
        Return the number of facts.
        """
        facts = []

        for file in self.yaml_files:
            facts += self.gather_facts_list(file)

        unique_facts = list(set(facts))
        self.facts = unique_facts

        return len(unique_facts)

    def gather_facts_list(self, file):
        """
        Return a list of facts.
        """
        facts = []

        contents = utils.file_to_string(os.path.join(self.paths["role"],
                                        file))
        contents = re.sub(r"\s+", "", contents)
        matches = self.regex_facts.findall(contents)

        for match in matches:
            facts.append(match.split(":")[1])

        return facts

    def gather_files(self):
        """
        Return the number of files.
        """
        self.all_files = utils.files_in_path(self.paths["role"])

        return len(self.all_files)

    def gather_lines(self):
        """
        Return the number of lines.
        """
        total_lines = 0
        for file in self.all_files:
            full_path = os.path.join(self.paths["role"], file)

            with open(full_path, "r") as f:
                for line in f:
                    total_lines += 1

            if full_path.endswith(".yml"):
                self.yaml_files.append(full_path)

        return total_lines

    def tally_role_columns(self):
        """
        Sum up all of the stat columns.
        """
        totals = self.report["totals"]
        roles = self.report["roles"]

        totals["dependencies"] = sum(roles[item]
                                     ["total_dependencies"] for item in roles)
        totals["defaults"] = sum(roles[item]
                                 ["total_defaults"] for item in roles)
        totals["facts"] = sum(roles[item]["total_facts"] for item in roles)
        totals["files"] = sum(roles[item]["total_files"] for item in roles)
        totals["lines"] = sum(roles[item]["total_lines"] for item in roles)

    def valid_meta(self, role):
        """
        Return whether or not the meta file being read is valid.
        """
        if os.path.exists(self.paths["meta"]):
            self.meta_dict = utils.yaml_load(self.paths["meta"])
        else:
            self.report["state"]["missing_meta_role"] += 1
            self.report["roles"][role]["state"] = "missing_meta"

            return False

        is_valid = True

        # utils.yaml_load returns False when the file is invalid
        if isinstance(self.meta_dict, bool):
            is_valid = False
            sys.exit(1)

        return is_valid

    def make_or_augment_meta(self, role):
        """
        Create or augment a meta file.
        """
        if not os.path.exists(self.paths["meta"]):
            utils.create_meta_main(self.paths["meta"], self.config, role, "")
            self.report["state"]["ok_role"] += 1
            self.report["roles"][role]["state"] = "ok"

        # swap values in place to use the config values
        swaps = [
            ("author", self.config["author_name"]),
            ("company", self.config["author_company"]),
            ("license", self.config["license_type"]),
        ]

        (new_meta, _) = utils.swap_yaml_string(self.paths["meta"], swaps)

        # normalize the --- at the top of the file by removing it first
        new_meta = new_meta.replace("---", "")
        new_meta = new_meta.lstrip()

        # augment missing main keys
        augments = [
            ("ansigenome_info", "{}"),
            ("galaxy_info", "{}"),
            ("dependencies", "[]"),
        ]

        new_meta = self.augment_main_keys(augments, new_meta)

        # re-attach the ---
        new_meta = "---\n\n" + new_meta

        travis_path = os.path.join(self.paths["role"], ".travis.yml")
        if os.path.exists(travis_path):
            new_meta = new_meta.replace("travis: False", "travis: True")

        utils.string_to_file(self.paths["meta"], new_meta)

    def augment_main_keys(self, keys, file):
        """
        Add the main key if it is missing.
        """
        nfile = file
        ansigenome_block = """
ansigenome_info:
  galaxy_id: ''

  travis: False

  synopsis: |
    Describe your role in a few paragraphs....

  usage: |
    Describe how to use in more detail...

  #custom: |
  #  Any custom output you want after the usage section..
"""

        for key in keys:
            if key[0] not in nfile:
                if key[0] == "ansigenome_info":
                    # make sure ansigenome_info is always on the bottom
                    nfile = nfile + "\n{0}".format(ansigenome_block)
                else:
                    nfile = "\n{0}: {1}\n\n".format(key[0], key[1]) + nfile

        return nfile

    def write_readme(self, role):
        """
        Write out a new readme file.
        """
        j2_out = self.readme_template.render(self.readme_template_vars)

        self.update_gen_report(role, "readme", j2_out)

    def write_meta(self, role):
        """
        Write out a new meta file.
        """
        meta_file = utils.file_to_string(self.paths["meta"])

        self.update_gen_report(role, "meta", meta_file)

    def update_scan_report(self, role):
        """
        Update the role state and adjust the scan totals.
        """
        state = self.report["state"]

        # ensure the missing meta state is colored up and the ok count is good
        if self.gendoc:
            if self.report["roles"][role]["state"] == "missing_meta":
                return

        if os.path.exists(self.paths["readme"]):
            state["ok_role"] += 1
            self.report["roles"][role]["state"] = "ok"
        else:
            state["missing_readme_role"] += 1
            self.report["roles"][role]["state"] = "missing_readme"

    def update_gen_report(self, role, file, original):
        """
        Update the role state and adjust the gen totals.
        """
        state = self.report["state"]

        if not os.path.exists(self.paths[file]):
            state["ok_role"] += 1
            self.report["roles"][role]["state"] = "ok"
        elif (self.report["roles"][role][file] != original and
                self.report["roles"][role]["state"] != "ok"):
            state["changed_role"] += 1
            self.report["roles"][role]["state"] = "changed"
        elif self.report["roles"][role][file] == original:
            state["skipped_role"] += 1
            self.report["roles"][role]["state"] = "skipped"
            return

        utils.string_to_file(self.paths[file], original)

    def make_meta_dict_consistent(self):
        """
        Remove the possibility of the main keys being undefined.
        """
        if self.meta_dict is None:
            self.meta_dict = {}

        if "galaxy_info" not in self.meta_dict:
            self.meta_dict["galaxy_info"] = {}

        if "dependencies" not in self.meta_dict:
            self.meta_dict["dependencies"] = []

        if "ansigenome_info" not in self.meta_dict:
            self.meta_dict["ansigenome_info"] = {}

    def set_readme_template_vars(self, role, repo_name):
        """
        Set the readme template variables.
        """
        # normalize and expose a bunch of fields to the template
        authors = []

        author = {
            "name": self.config["author_name"],
            "company": self.config["author_company"],
            "url": self.config["author_url"],
            "email": self.config["author_email"],
            "twitter": self.config["author_twitter"],
        }
        scm = {
            "host": self.config["scm_host"],
            "repo_prefix": self.config["scm_repo_prefix"],
            "type": self.config["scm_type"],
            "user": self.config["scm_user"],
        }
        license = {
            "type": self.config["license_type"],
            "url": self.config["license_url"],
        }

        role_name = utils.normalize_role(role, self.config)

        normalized_role = {
            "name": role_name,
            "galaxy_name": "{0}.{1}".format(self.config["scm_user"],
                                            role_name),
            "slug": "{0}{1}".format(self.config["scm_repo_prefix"],
                                    role_name),
        }

        if "authors" in self.meta_dict["ansigenome_info"]:
            authors = self.meta_dict["ansigenome_info"]["authors"]
        else:
            authors = [author]

            if "github" in self.config["scm_host"]:
                self.config["author_github"] = "{0}/{1}".format(
                    self.config["scm_host"],
                    self.config["scm_user"])

        self.readme_template_vars = {
            "authors": authors,
            "scm": scm,
            "role": normalized_role,
            "license": license,
            "galaxy_info": self.meta_dict["galaxy_info"],
            "dependencies": self.meta_dict["dependencies"],
            "ansigenome_info": self.meta_dict["ansigenome_info"]
        }

        # add the defaults and facts
        r_defaults = self.report["roles"][role]["defaults"]
        self.readme_template_vars["ansigenome_info"]["defaults"] = r_defaults

        facts = "\n".join(self.report["roles"][role]["facts"])
        self.readme_template_vars["ansigenome_info"]["facts"] = facts

import re
import os

import constants as c
import ui as ui
import utils as utils


class Scan(object):
    """
    Loop over each role on the roles path and report back stats on them.
    """
    def __init__(self, args, options, rebuild=False, dump=False):
        if len(args) == 0:
            self.roles_path = os.path.join(os.getcwd(), c.ROLES_PATH)
        else:
            self.roles_path = args[0]

        self.options = options
        self.rebuild = rebuild
        self.dump = dump

        repo_prefix = ""
        if rebuild:
            repo_prefix = options.repo_prefix

        self.roles = utils.roles_dict(self.roles_path, repo_prefix)

        if self.options.limit:
            self.limit_roles()

        utils.exit_if_no_roles(len(self.roles.keys()), self.roles_path)

        self.regex_facts = re.compile(r"set_fact:\w+")
        self.paths = {}
        self.all_files = []
        self.yaml_files = []
        self.defaults = ""
        self.facts = []
        self.dependencies = []
        self.verify = False

        # only load and validate the templates when rebuilding files
        if self.rebuild:
            self.meta_template = utils.template(options.template_meta)
            self.readme_template = utils.template(options.template_readme)
            self.verify = True
            self.meta_dict = None

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
                "ok_meta": 0,
                "ok_readme": 0,
                "skipped_meta": 0,
                "skipped_readme": 0,
                "changed_meta": 0,
                "changed_readme": 0,
                "failed_meta": 0,
                "failed_readme": 0
            },
            "roles": {},
            "stats": {
                "longest_role_name_length": len(max(self.roles, key=len))
            }
        }

        self.scan_roles()
        if self.dump:
            self.dump_roles()

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
            self.paths["meta"] = os.path.join(self.paths["role"],
                                              "meta", "main.yml")
            self.paths["readme"] = os.path.join(self.paths["role"],
                                                "README.md")
            self.paths["defaults"] = os.path.join(self.paths["role"],
                                                  "defaults", "main.yml")

            self.report["roles"][key] = self.report_role(key)

            # we are writing a meta and readme file which means the
            # the state of the role needs to be updated before it gets
            # output by the ui
            if self.verify:
                if self.valid_meta(key) and self.rebuild:
                    self.set_meta_template_vars(value)
                    self.write_meta(key)
                    self.set_readme_template_vars(key, value)
                    self.write_readme(key)

            if not self.options.quiet:
                ui.role(key,
                        self.report["roles"][key],
                        self.report["stats"]["longest_role_name_length"])

        self.tally_role_columns()

        if not self.options.quiet:
            ui.totals(self.report["totals"],
                      len(self.report["roles"].keys()),
                      self.report["stats"]["longest_role_name_length"])

            if self.verify:
                print "\n"
                ui.state_totals(self.report["state"], "meta",
                                self.report["stats"]
                                ["longest_role_name_length"])
                ui.state_totals(self.report["state"], "readme",
                                self.report["stats"]
                                ["longest_role_name_length"])

    def dump_roles(self):
        """
        Write the contents of the report to json.
        """
        out_file = self.options.out_file

        if not out_file.endswith(".json"):
            out_file += ".json"

        # remove unnecessary data and convert string dumps to yaml
        del self.report["state"]
        for role in self.report["roles"]:
            del self.report["roles"][role]["state"]
            if not self.options.with_readme:
                del self.report["roles"][role]["readme"]

            defaults = self.report["roles"][role]["defaults"]
            self.report["roles"][role]["defaults"] = utils.yaml_load("",
                                                                     defaults)
            meta = self.report["roles"][role]["meta"]
            self.report["roles"][role]["meta"] = utils.yaml_load("", meta)

        report_as_json_string = utils.dict_to_json(self.report)
        utils.string_to_file(out_file, report_as_json_string)

        if not self.options.quiet:
            ui.ok("", c.MESSAGES["dump_success"], out_file)

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

        meta = utils.file_to_string(self.paths["meta"])

        meta_dict = utils.yaml_load(self.paths["meta"])

        if meta_dict and "dependencies" in meta_dict:
            self.dependencies = meta_dict["dependencies"]
        else:
            self.dependencies = []

        return meta

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

        is_valid = True

        # utils.yaml_load returns False when the file is invalid
        if isinstance(self.meta_dict, bool):
            is_valid = False

            # we need to turn it back into a dict or crazy things happen
            self.meta_dict = {}

        self.meta_dict = self.make_meta_consistent(self.meta_dict)

        if not is_valid:
            self.report["state"]["failed_meta"] += 1
            self.report["state"]["skipped_readme"] += 1
            self.report["roles"][role]["state"] = "failed"

        return is_valid

    def make_meta_consistent(self, meta_dict):
        """
        Return a new meta dict that fixes inconsistencies.
        """
        # if a meta file consists of only --- then this condition fixes
        # a null error were "meta_info" never exists in self.meta_dict
        if meta_dict is None:
            meta_dict = {}

        if "galaxy_info" not in meta_dict:
            meta_dict["galaxy_info"] = {}

        if "platforms" not in meta_dict["galaxy_info"]:
            meta_dict["galaxy_info"]["platforms"] = []

        if "dependencies" not in meta_dict:
            meta_dict["dependencies"] = []

        if "meta_info" not in meta_dict:
            meta_dict["meta_info"] = {}

        return meta_dict

    def write_meta(self, role):
        """
        Potentially write out a new meta file.
        """
        j2_out = self.meta_template.render(self.meta_template_vars)

        # merge the original meta dict's contents into the meta dict
        # this avoids clobbering user edited values in the meta file
        merged_dict = False
        if os.path.exists(self.paths["meta"]):
            merged_dict = True
            original_meta_dict = utils.yaml_load(self.paths["meta"])
            original_meta_dict = self.make_meta_consistent(original_meta_dict)
            self.meta_dict = dict(self.meta_dict.items() +
                                  original_meta_dict.items())

            # make sure certain values are set if they didn't exist previously
            template_meta_dict = utils.yaml_load("", input=j2_out)
            galaxy_author = template_meta_dict["galaxy_info"]["author"]
            galaxy_platforms = template_meta_dict["galaxy_info"]["platforms"]
            meta_github_url = template_meta_dict["meta_info"]["github_url"]

            if len(self.meta_dict["galaxy_info"]["platforms"]) == 0:
                self.meta_dict["galaxy_info"]["platforms"] = galaxy_platforms

            if "author" not in self.meta_dict["galaxy_info"]:
                self.meta_dict["galaxy_info"]["author"] = galaxy_author

            # always renew the github url
            self.meta_dict["meta_info"]["github_url"] = meta_github_url
        else:
            # otherwise just use what we have
            self.meta_dict = utils.yaml_load("", input=j2_out)

        # sort of hacky but works completely fine for now
        self.meta_dict["galaxy_info"]["platforms"] = utils.to_nice_yaml(
            self.meta_dict["galaxy_info"]["platforms"])

        self.meta_dict["dependencies"] = utils.to_nice_yaml(
            self.meta_dict["dependencies"])

        if merged_dict:
            # we need to recompile the template with the merged dict
            j2_out = self.meta_template.render(self.meta_dict)

        self.update_role_report(role, "meta", j2_out)

    def write_readme(self, role):
        """
        Potentially write out a new readme file.
        """
        j2_out = self.readme_template.render(self.readme_template_vars)

        self.update_role_report(role, "readme", j2_out)

    def update_role_report(self, role, report_on, template):
        """
        Update the role state and adjust the state totals.
        """
        state = self.report["state"]
        state_not_skipped = False

        if not os.path.exists(self.paths[report_on]):
            state["ok_" + report_on] += 1
            self.report["roles"][role]["state"] = "ok"
            state_not_skipped = True
        elif self.report["roles"][role][report_on] != template:
            state["changed_" + report_on] += 1
            self.report["roles"][role]["state"] = "changed"
            state_not_skipped = True
        elif self.report["roles"][role][report_on] == template:
            state["skipped_" + report_on] += 1
            self.report["roles"][role]["state"] = "skipped"
            return

        # avoid clobbering non-skipped states in the terminal output
        if state_not_skipped:
            self.report["state"] = state

        utils.string_to_file(self.paths[report_on], template)

    def set_meta_template_vars(self, role):
        """
        Set the meta template variables.
        """
        github_url = "https://github.com/{0}/{1}".format(
            self.options.github_username,
            role.replace("_", "-"))

        self.meta_template_vars = {
            "galaxy_info": {
                "author": utils.capture_shell("git config user.name")[0][:-1],
            },
            "meta_info": {
                "github_url": github_url,
            }
        }

    def set_readme_template_vars(self, role, repo_name):
        """
        Set the readme template variables.
        """
        # at this stage both the platforms and dependencies are strings
        # because they were pretty printed to the meta file

        # this reverts them back to dicts and lists so they can be
        # looped overly properly in the readme file

        # this approach might make you want to vomit glass but it works
        # for the time being until a better approach is found
        platforms = self.meta_dict["galaxy_info"]["platforms"]
        self.meta_dict["galaxy_info"]["platforms"] = utils.yaml_load(
            "", input=platforms)

        self.meta_dict["dependencies"] = utils.yaml_load(
            "", input=self.meta_dict["dependencies"])

        self.readme_template_vars = {
            "github_username": self.options.github_username,
            "repo_name": repo_name,
            "role_name": utils.role_name(role),
            "galaxy_name": role,
            "galaxy_info": self.meta_dict["galaxy_info"],
            "dependencies": self.meta_dict["dependencies"],
            "meta_info": self.meta_dict["meta_info"]
        }

        if ("defaults" not in self.meta_dict["meta_info"] or
                len(self.meta_dict["meta_info"]["defaults"]) == 0):
            # trolled hard by pep8's 79 characters
            r_defaults = self.report["roles"][role]["defaults"]
            self.readme_template_vars["meta_info"]["defaults"] = r_defaults

        if ("facts" not in self.meta_dict["meta_info"] or
                len(self.meta_dict["meta_info"]["facts"]) == 0):
            facts = "\n".join(self.report["roles"][role]["facts"])
            self.readme_template_vars["meta_info"]["facts"] = facts

import os
import random
import sys

import constants as c
import ui as ui
import utils as utils


class Export(object):
    """
    Export a report to various types and formats.
    """
    def __init__(self, roles_path, report, config, options):
        self.roles_path = roles_path
        self.report = report
        self.config = config
        self.options = options
        self.type = options.type
        self.out_file = options.out_file

        # load the correct type and format
        if self.type == "graph":
            if self.options.size:
                self.size = self.options.size
            else:
                self.size = self.config["graphviz_size"]

            if self.options.dpi:
                self.dpi = self.options.dpi
            else:
                self.dpi = self.config["graphviz_dpi"]

            if self.options.flags:
                self.flags = self.options.flags
            else:
                self.flags = self.config["graphviz_flags"]

            self.set_format("graph")
            self.validate_format(c.ALLOWED_GRAPH_FORMATS)

            if self.format == "dot":
                self.graph_dot()
            else:
                self.exit_if_missing_graphviz()
                self.graph_png()
        elif self.type == "reqs":
            self.set_format("reqs")
            self.validate_format(c.ALLOWED_REQS_FORMATS)

            if self.format == "txt":
                self.reqs_txt()
            else:
                self.reqs_yml()
        elif self.type == "dump":
            self.set_format("dump")
            self.validate_format(c.ALLOWED_DUMP_FORMATS)
            self.dump()

    def set_format(self, format):
        """
        Pick the correct default format.
        """
        if self.options.format:
            self.format = self.options.format
        else:
            self.format = \
                self.config["default_format_" + format]

    def validate_format(self, allowed_formats):
        """
        Validate the allowed formats for a specific type.
        """
        if self.format in allowed_formats:
            return

        ui.error("Export type '{0}' does not accept '{1}' format, only: "
                 "{2}".format(self.type, self.format, allowed_formats))
        sys.exit(1)

    def graph_dot(self):
        """
        Export a graph of the data in dot format.
        """
        default_graphviz_template = """
digraph role_dependencies {
        size="%size"
        dpi=%dpi
        ratio="fill"
        landscape=false
        rankdir="BT";

        node [shape = "box",
              style = "rounded,filled",
              fillcolor = "lightgrey",
              fontsize = 20];

        edge [style = "dashed",
              dir = "forward",
              penwidth = 1.5];

%roles_list

%dependencies
}
"""

        roles_list = ""
        edges = ""

        # remove the darkest and brightest colors, still have 100+ colors
        adjusted_colors = c.X11_COLORS[125:-325]
        random.shuffle(adjusted_colors)
        backup_colors = adjusted_colors[:]

        for role, fields in sorted(self.report["roles"].iteritems()):
            name = utils.normalize_role(role, self.config)
            color_length = len(adjusted_colors) - 1

            # reset the colors if we run out
            if color_length == 0:
                adjusted_colors = backup_colors[:]
                color_length = len(adjusted_colors) - 1

            random_index = random.randint(1, color_length)
            roles_list += "        role_{0}              [label = \"{0}\"]\n" \
                          .format(name)

            edge = '\n        edge [color = "{0}"];\n' \
                   .format(adjusted_colors[random_index])
            del adjusted_colors[random_index]

            if fields["dependencies"]:
                dependencies = ""

                for dependency in sorted(fields["dependencies"]):
                    dependency_name = utils.role_name(dependency)
                    dependencies += "        role_{0} -> role_{1}\n" \
                                    .format(name, utils.normalize_role(
                                            dependency_name, self.config))

                edges += "{0}{1}\n".format(edge, dependencies)

        graphviz_template = default_graphviz_template.replace("%roles_list",
                                                              roles_list)
        graphviz_template = graphviz_template.replace("%dependencies",
                                                      edges)
        graphviz_template = graphviz_template.replace("%size",
                                                      self.size)
        graphviz_template = graphviz_template.replace("%dpi",
                                                      str(self.dpi))

        if self.out_file:
            utils.string_to_file(self.out_file, graphviz_template)
        else:
            print graphviz_template

    def graph_png(self):
        """
        Export a graph of the data in png format using graphviz/dot.
        """
        if not self.out_file:
            ui.error(c.MESSAGES["png_missing_out"])
            sys.exit(1)

        cli_flags = "-Gsize='{0}' -Gdpi='{1}' {2} ".format(self.size, self.dpi,
                                                           self.flags)
        cli_flags += "-o {0}".format(self.out_file)

        (out, err) = utils.capture_shell(
            "ansigenome export -t graph -f dot | dot -Tpng {0}"
            .format(cli_flags))

        if err:
            ui.error(err)

    def exit_if_missing_graphviz(self):
        """
        Detect the presence of the dot utility to make a png graph.
        """
        (out, err) = utils.capture_shell("which dot")

        if "dot" not in out:
            ui.error(c.MESSAGES["dot_missing"])

    def reqs_txt(self):
        """
        Export a requirements file in txt format.
        """
        role_lines = ""

        for role in sorted(self.report["roles"]):
            name = utils.normalize_role(role, self.config)
            galaxy_name = "{0}.{1}".format(self.config["scm_user"], name)

            version_path = os.path.join(self.roles_path, role, "VERSION")
            version = utils.get_version(version_path)
            role_lines += "{0},{1}\n".format(galaxy_name, version)

        if self.out_file:
            utils.string_to_file(self.out_file, role_lines)
        else:
            print role_lines

    def reqs_yml(self):
        """
        Export a requirements file in yml format.
        """
        default_yml_item = """
- src:     '%src'
  name:    '%name'
  scm:     '%scm'
  version: '%version'
"""

        role_lines = "---\n"
        for role in sorted(self.report["roles"]):
            name = utils.normalize_role(role, self.config)
            galaxy_name = "{0}.{1}".format(self.config["scm_user"], name)
            yml_item = default_yml_item

            if self.config["scm_host"]:
                yml_item = yml_item.replace("%name",
                                            "{0}".format(galaxy_name))
                if self.config["scm_repo_prefix"]:
                    role = self.config["scm_repo_prefix"] + name

                src = os.path.join(self.config["scm_host"],
                                   self.config["scm_user"], role)
            else:
                src = galaxy_name
                yml_item = yml_item.replace("  name: '%name'\n", "")
                yml_item = yml_item.replace("  scm: '%scm'\n", "")

            yml_item = yml_item.replace("%src", src)

            if self.config["scm_type"]:
                yml_item = yml_item.replace("%scm", self.config["scm_type"])
            else:
                yml_item = yml_item.replace("  scm: '%scm'\n", "")

            version_path = os.path.join(self.roles_path, role, "VERSION")
            version = utils.get_version(version_path)
            yml_item = yml_item.replace("%version", version)

            role_lines += "{0}".format(yml_item)

        if self.out_file:
            utils.string_to_file(self.out_file, role_lines)
        else:
            print role_lines

    def dump(self):
        """
        Dump the output to json.
        """
        report_as_json_string = utils.dict_to_json(self.report)
        if self.out_file:
            utils.string_to_file(self.out_file, report_as_json_string)
        else:
            print report_as_json_string

import color as clr
import constants as c


def log(color, *args):
    """
    Print a message with a specific color.
    """
    if color in c.LOG_COLOR.keys():
        out_color = c.LOG_COLOR[color]
    else:
        out_color = color

    for arg in args:
        print clr.stringc(arg, out_color)


def ok(*args):
    """
    Print a message in green.
    """
    log("green", *args)


def warn(*args):
    """
    Print a message in yellow.
    """
    log("yellow", *args)


def error(*args):
    """
    Print a message in red.
    """
    log("red", *args)


def usage():
    """
    Return the usage for the help command.
    """
    l_bracket = clr.stringc("[", "dark gray")
    r_bracket = clr.stringc("]", "dark gray")
    pipe = clr.stringc("|", "dark gray")

    app_name = clr.stringc("%prog", "bright blue")
    commands = clr.stringc("{0}".format(pipe).join(c.VALID_ACTIONS), "normal")
    help = clr.stringc("--help", "green")
    options = clr.stringc("options", "yellow")

    guide = "\n\n"
    for action in c.VALID_ACTIONS:
        guide += command_name(app_name, action,
                              c.MESSAGES["help_" + action])

    # remove the last line break
    guide = guide[:-1]

    return "{0} {1}{2}{3} {1}{4}{3} {1}{5}{3}\n{6}".format(app_name,
                                                           l_bracket,
                                                           commands,
                                                           r_bracket,
                                                           help,
                                                           options,
                                                           guide)


def epilogue(app_name):
    """
    Return the epilogue for the help command.
    """
    app_name = clr.stringc(app_name, "bright blue")
    command = clr.stringc("command", "cyan")
    help = clr.stringc("--help", "green")

    return "\n%s %s %s for more info on a command\n" % (app_name,
                                                        command, help)


def command_name(app_name, command, help_text):
    """
    Return a snippet of help text for this command.
    """
    command = clr.stringc(command, "cyan")
    help = clr.stringc("--help", "green")

    return "{0} {1} {2}\n{3}\n\n".format(app_name, command,
                                         help, help_text)


def role(name, report, role_name_length):
    """
    Print the role information.
    """
    pad_role_name_by = 11 + role_name_length

    defaults = field_value(report["total_defaults"], "defaults", "blue", 16)
    facts = field_value(report["total_facts"], "facts", "purple", 16)
    files = field_value(report["total_files"], "files", "dark gray", 16)
    lines = field_value(report["total_lines"], "lines", "normal", 16)

    print "{0:<{1}} {2} {3} {4} {5}".format(
        clr.stringc(name, c.LOG_COLOR[report["state"]]),
        pad_role_name_by, defaults, facts, files, lines)


def field_value(key, label, color, padding):
    """
    Print a specific field's stats.
    """
    if not clr.has_colors and padding > 0:
        padding = 7

    if color == "bright gray" or color == "dark gray":
        bright_prefix = ""
    else:
        bright_prefix = "bright "

    field = clr.stringc(key, "{0}{1}".format(bright_prefix, color))
    field_label = clr.stringc(label, color)

    return "{0:>{1}} {2}".format(field, padding, field_label)


def totals(report, total_roles, role_name_length):
    """
    Print the totals for each role's stats.
    """
    roles_len_string = len(str(total_roles))
    roles_label_len = 6  # "r" "o" "l" "e" "s" " "

    if clr.has_colors:
        roles_count_offset = 22
    else:
        roles_count_offset = 13

    roles_count_offset += role_name_length

    # no idea honestly but it fixes the formatting
    # it will probably break the formatting if you have 100+ roles
    if roles_len_string > 1:
        roles_count_offset -= 2

    pad_roles_by = roles_count_offset + roles_len_string + roles_label_len

    roles = field_value(total_roles, "roles", "normal", 0)
    defaults = field_value(report["defaults"], "defaults", "blue", 16)
    facts = field_value(report["facts"], "facts", "purple", 16)
    files = field_value(report["files"], "files", "dark gray", 16)
    lines = field_value(report["lines"], "lines", "normal", 16)

    print "".join(clr.stringc("-", "black") * 79)
    print "{0} {2:>{1}} {3} {4} {5}".format(
        roles, pad_roles_by, defaults, facts, files, lines)


def gen_totals(report, file_type):
    """
    Print the gen totals.
    """
    label = clr.stringc(file_type + " files   ", "bright purple")

    ok = field_value(report["ok_role"], "ok", c.LOG_COLOR["ok"], 0)
    skipped = field_value(report["skipped_role"], "skipped",
                          c.LOG_COLOR["skipped"], 16)
    changed = field_value(report["changed_role"], "changed",
                          c.LOG_COLOR["changed"], 16)

    # missing_meta = field_value(report["missing_meta_role"],
    #                            "missing meta(s)",
    #                            c.LOG_COLOR["missing_meta"], 16)

    # print "\n{0} {1} {2} {3}".format(ok, skipped, changed, missing_meta)

    print "\n{0} {1} {2} {3}".format(label, ok, skipped, changed)


def scan_totals(report):
    """
    Print the scan totals.
    """
    ok = field_value(report["ok_role"], "ok", c.LOG_COLOR["ok"], 0)
    missing_readme = field_value(report["missing_readme_role"],
                                 "missing readme(s)",
                                 c.LOG_COLOR["missing_readme"], 16)

    missing_meta = field_value(report["missing_meta_role"],
                               "missing meta(s)",
                               c.LOG_COLOR["missing_meta"], 16)

    print "\n{0} {1} {2}".format(ok, missing_readme, missing_meta)

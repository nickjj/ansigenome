import os

import constants as c
import utils as utils


class Config(object):
    """
    Create a config file.
    """
    def __init__(self, args, options, config):
        self.config_path = os.path.join(c.CONFIG_DEFAULT_PATH, c.CONFIG_FILE)
        self.config = config

        # Only load the out file from the options when config was called
        # through the actual CLI, rather than when no default config exists
        if options == {}:
            no_configs_found = True
        else:
            no_configs_found = False

            if options.out_file:
                self.config_path = options.out_file

        if no_configs_found:
            self.show_no_config_help()

        out_config = self.ask_questions()
        self.write_config(out_config)

    def show_no_config_help(self):
        """
        Show a help sentence for new users who have no config.
        """
        print """
    Welcome to ansigenome, you are seeing this message because there
    were no available config files to load.

    Answering the questions below will setup a global config, you
    only need to do this once. You can also exit with CTRL+D.

    This config file will be placed in $HOME/.ansigenome.conf for now.
              """

    def ask_questions(self):
        """
        Obtain config settings from the user.
        """
        out_config = {
            "author": {},
            "license": {},
            "scm": {},
            "options": {},
        }

        for key in c.CONFIG_QUESTIONS:
            section = key[1]
            print
            for question in section:
                answer = utils.ask(question[1], question[2])
                out_config[key[0]][question[0]] = answer

        # Set a few default values.
        test_runner = "https://github.com/nickjj/rolespec"

        out_config["options"]["readme_template"] = ""
        out_config["options"]["travis"] = True
        out_config["options"]["quiet"] = False
        out_config["options"]["dump_with_readme"] = False
        out_config["options"]["test_runner"] = test_runner

        return out_config

    def write_config(self, config):
        """
        Write the config with a little post-converting formatting.
        """
        config_as_string = utils.to_nice_yaml(config)

        config_as_string = "---\n" + config_as_string
        config_as_string = config_as_string.replace("author:", "\nauthor:")
        config_as_string = config_as_string.replace("license:", "\nlicense:")
        config_as_string = config_as_string.replace("scm:", "\nscm:")
        config_as_string = config_as_string.replace("options:", "\noptions:")

        utils.string_to_file(self.config_path, config_as_string)

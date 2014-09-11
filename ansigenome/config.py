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
        utils.write_config(self.config_path, out_config)

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
        out_config = {}

        for key in c.CONFIG_QUESTIONS:
            section = key[1]
            print
            for question in section:
                answer = utils.ask(question[1], question[2])
                out_config["{0}_{1}".format(key[0], question[0])] = answer

        for key in c.CONFIG_MULTIPLE_CHOICE_QUESTIONS:
            section = key[1]
            print
            # keep going until we get what we want
            while True:
                input = utils.ask(section[1], "")
                if (input.isdigit() and
                        int(input) > 0 and
                        int(input) <= section[0]):
                    answer = input

                    break
                print

            # store the answer as 1 less than it is, we're dealing with
            # a list to select the number which is 0 indexed
            answer = int(input) - 1

            if key[0] == "license":
                out_config["license_type"] = c.LICENSE_TYPES[answer][0]
                out_config["license_url"] = c.LICENSE_TYPES[answer][1]

        # merge in defaults without asking questions
        merged_config = dict(c.CONFIG_DEFAULTS.items() + out_config.items())

        return merged_config

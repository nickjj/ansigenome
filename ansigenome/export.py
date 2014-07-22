import utils as utils


class Export(object):
    """
    Create a file meant to hold a list of all of your roles.
    """
    def __init__(self, args, options):
        self.roles_path = args[0]
        self.out_file = options.out_file

        utils.string_to_file(self.out_file,
                             "\n".join(utils.roles_dict(self.roles_path)))

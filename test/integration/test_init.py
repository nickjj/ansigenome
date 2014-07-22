import os
import unittest

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestInit(unittest.TestCase):
    """
    Integration tests for the init command.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_init(self):
        self.assert_role()

    def test_init_custom_repo_name(self):
        self.assert_role("-r foo")

    def assert_role(self, args=""):
        path = os.path.join(self.test_path, th.random_string())
        role_name = os.path.basename(path)

        if len(args) > 3:
            repo_name = args[2:-1]
        else:
            repo_name = role_name

        (out, err) = utils.capture_shell(
            "ansigenome init {0} {1}".format(path, args))

        for folder in c.ANSIBLE_FOLDERS:
            assert os.path.exists(os.path.join(path, folder)), "expected " + \
                "'{0}' to be created".format(folder)

        tests_mainyml = utils.file_to_string(os.path.join(path,
                                             "tests", "main.yml"))

        self.assertIn(repo_name, tests_mainyml)
        self.assertEqual(out, "")
        self.assertEqual(err, "")

if __name__ == "__main__":
    unittest.main()

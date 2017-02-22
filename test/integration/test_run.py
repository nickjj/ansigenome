import os
import unittest

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestRun(unittest.TestCase):
    """
    Integration tests for the run command.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_run(self):
        self.assert_run("-m 'echo hello'", "echo hello")

    def test_run_bad_command(self):
        self.assert_run("'-m foo bar'", "foo: not found")

    def assert_run(self, args, run_output):
        th.create_roles(self.test_path)

        (out, err) = utils.capture_shell(
            "ansigenome run {0} {1}".format(self.test_path, args))

        self.assertIn(run_output, out)
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()

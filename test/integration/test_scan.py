import os
import unittest

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestScan(unittest.TestCase):
    """
    Integration tests for the scan command.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_scan(self):
        role_names = th.create_roles(self.test_path, 3)

        for i, role in enumerate(role_names):
            defaults_path = os.path.join(self.test_path, role,
                                         "defaults", "main.yml")
            tasks_path = os.path.join(self.test_path, role,
                                      "tasks", "main.yml")
            meta_path = os.path.join(self.test_path, role,
                                     "meta", "main.yml")
            utils.string_to_file(defaults_path, th.DEFAULTS_TEMPLATE)
            utils.string_to_file(tasks_path, th.TASKS_TEMPLATE)

            # remove 1 of the meta files
            if i == 2:
                os.remove(meta_path)

        (out, err) = utils.capture_shell(
            "ansigenome scan {0}".format(self.test_path))

        th.print_out("Scan output without terminal colors:", out)

        self.assertIn("3 roles", out)
        self.assertIn("3 defaults", out)
        self.assertIn("9 defaults", out)
        self.assertIn("2 facts", out)
        self.assertIn("6 facts", out)
        self.assertIn("8 files", out)
        self.assertIn("26 files", out)
        self.assertIn("94 lines", out)
        self.assertIn("248 lines", out)

        self.assertIn("0 ok       3 missing readme(s)       " +
                      "0 missing meta(s)", out)

        self.assertEqual(err, "")

if __name__ == "__main__":
    unittest.main()

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

            # test various meta files, including no meta file for one
            # of the roles
            meta = th.META_TEMPLATE
            if i == 0:
                meta = "---"
            else:
                meta.replace("dependencies: []", "")
            if i < 2:
                utils.string_to_file(meta_path, meta)

        (out, err) = utils.capture_shell(
            "ansigenome scan {0}".format(self.test_path))

        th.print_out("Scan output without terminal colors:", out)

        self.assertIn("3 roles", out)
        self.assertIn("3 defaults", out)
        self.assertIn("9 defaults", out)
        self.assertIn("2 facts", out)
        self.assertIn("6 facts", out)
        self.assertIn("8 files", out)
        self.assertIn("23 files", out)
        self.assertIn("56 lines", out)
        self.assertIn("170 lines", out)
        self.assertEqual(err, "")

if __name__ == "__main__":
    unittest.main()

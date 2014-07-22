import os
import unittest

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestDump(unittest.TestCase):
    """
    Integration tests for the dump command.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_scan(self):
        out_file = os.path.join(self.test_path, "dump.json")
        role_names = th.create_roles(self.test_path)

        for role in role_names:
            defaults_path = os.path.join(self.test_path, role,
                                         "defaults", "main.yml")
            tasks_path = os.path.join(self.test_path, role,
                                      "tasks", "main.yml")
            meta_path = os.path.join(self.test_path, role,
                                     "meta", "main.yml")
            utils.string_to_file(defaults_path, th.DEFAULTS_TEMPLATE)
            utils.string_to_file(tasks_path, th.TASKS_TEMPLATE)
            utils.string_to_file(meta_path, th.META_TEMPLATE)

        (out, err) = utils.capture_shell(
            "ansigenome dump {0} -o {1}".format(self.test_path, out_file))

        json_contents = utils.file_to_string(out_file)
        contents = th.json_to_dict(json_contents)

        self.assertIn("json", out)
        self.assertNotIn("readme:", json_contents)
        self.assertIsInstance(contents, dict)
        self.assertEqual(err, "")

if __name__ == "__main__":
    unittest.main()

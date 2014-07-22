import os
import unittest

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestExport(unittest.TestCase):
    """
    Integration tests for the export command.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_export(self):
        out_path = os.path.join(self.test_path, "Rolefile")

        role_names = th.create_roles(self.test_path)

        (out, err) = utils.capture_shell(
            "ansigenome export {0} -o {1}".format(self.test_path,
                                                  out_path))

        self.assertTrue(os.path.exists(out_path))

        rolefile = utils.file_to_string(out_path)

        for role in role_names:
            self.assertIn(role, rolefile)

        self.assertEqual(out, "")
        self.assertEqual(err, "")

if __name__ == "__main__":
    unittest.main()

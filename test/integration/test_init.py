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
        self.assert_role("-c foo,bar,baz")

    def assert_role(self, args=""):
        role_name = th.random_string()

        path = os.path.join(self.test_path, role_name)
        meta_path = os.path.join(path, "meta", "main.yml")

        (out, err) = utils.capture_shell(
            "ansigenome init {0} {1}".format(path, args))

        for folder in c.ANSIBLE_FOLDERS:
            assert os.path.exists(os.path.join(path, folder)), "expected " + \
                "'{0}' to be created".format(folder)

            if folder == "tests":
                inventory_path = os.path.join(path, folder, "inventory")

                assert os.path.exists(os.path.join(path,
                                                   folder,
                                                   "test")), "expected " + \
                    "'{0}' to be created".format(folder)

                assert os.path.exists(os.path.join(inventory_path,
                                                   "hosts")), "expected " + \
                    "'{0}' to be created".format(folder)

        assert os.path.exists(os.path.join(path, "VERSION"))

        meta = utils.file_to_string(meta_path)

        print
        print "Meta file:"
        print meta
        print
        self.assertIn("Test User", meta)
        self.assertIn("1 sentence", meta)
        self.assertIn(role_name, meta)
        self.assertIn("Debian", meta)
        self.assertIn("categories: [foo,bar,baz]", meta)
        self.assertIn("ansigenome_info", meta)
        self.assertIn("galaxy_id", meta)
        self.assertIn("travis: True", meta)
        self.assertIn("Describe", meta)
        self.assertIn("custom", meta)

        self.assertEqual(out, "")
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()

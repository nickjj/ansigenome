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

    def test_graph_dot(self):
        out_dir = os.path.join(self.test_path, "graph")
        out_path = os.path.join(out_dir, "test.dot")

        role_names = th.create_roles(self.test_path)

        (out, err) = utils.capture_shell(
            "ansigenome export {0} -f dot -o {1}".format(self.test_path,
                                                         out_path))

        self.assertTrue(os.path.exists(out_path))

        dot = utils.file_to_string(out_path)

        for role in role_names:
            self.assertIn(role, dot)
            self.assertIn("size", dot)
            self.assertIn("dpi", dot)
            self.assertIn("node", dot)
            self.assertIn("edge", dot)
            self.assertNotIn("->", dot)

        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_graph_png(self):
        out_dir = os.path.join(self.test_path, "graph")
        out_path = os.path.join(out_dir, "test.png")

        th.create_roles(self.test_path)

        (out, err) = utils.capture_shell(
            "ansigenome export {0} -o {1}".format(self.test_path, out_path))

        self.assertTrue(os.path.exists(out_path))

        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_reqs_yml(self):
        out_dir = os.path.join(self.test_path, "requirements")
        out_path = os.path.join(out_dir, "requirements.yml")

        role_names = th.create_roles(self.test_path)

        cli_flags = "-f yml"
        (out, err) = utils.capture_shell(
            "ansigenome export -t reqs {0} {2} -o {1}".format(self.test_path,
                                                              out_path,
                                                              cli_flags))

        self.assertTrue(os.path.exists(out_path))

        requirements = utils.file_to_string(out_path)

        for role in role_names:
            self.assertIn(role, requirements)
            self.assertIn("/ansible-", requirements)
            self.assertIn("testuser.", requirements)
            self.assertIn("'git'", requirements)
            self.assertIn("master", requirements)

        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_reqs_txt(self):
        out_dir = os.path.join(self.test_path, "requirements")
        out_path = os.path.join(out_dir, "requirements.txt")

        role_names = th.create_roles(self.test_path)

        (out, err) = utils.capture_shell(
            "ansigenome export -t reqs {0} -o {1}".format(self.test_path,
                                                          out_path))

        self.assertTrue(os.path.exists(out_path))

        requirements = utils.file_to_string(out_path)

        for role in role_names:
            self.assertIn("testuser.", requirements)
            self.assertIn(role, requirements)
            self.assertIn(",", requirements)

        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_dump(self):
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
            "ansigenome export -t dump {0} -o {1}".format(self.test_path,
                                                          out_file))

        self.assertTrue(os.path.exists(out_file))

        json_contents = utils.file_to_string(out_file)
        contents = th.json_to_dict(json_contents)

        self.assertIn("roles", contents)
        self.assertIn("totals", contents)
        self.assertIn("dependencies", json_contents)
        self.assertIsInstance(contents, dict)
        self.assertEqual(err, "")

if __name__ == "__main__":
    unittest.main()

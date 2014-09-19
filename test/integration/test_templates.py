import os
import unittest

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestTemplates(unittest.TestCase):
    """
    Integration tests for the templates.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_templates(self):
        role = th.create_roles(self.test_path, 1)
        role_name = role[0]

        role_path = os.path.join(self.test_path, role_name)
        readme_path = os.path.join(role_path, "README.rst")
        defaults_path = os.path.join(self.test_path, role_name,
                                     "defaults", "main.yml")
        tasks_path = os.path.join(self.test_path, role_name,
                                  "tasks", "main.yml")

        meta_path = os.path.join(self.test_path, role_name,
                                 "meta", "main.yml")

        utils.string_to_file(defaults_path, th.DEFAULTS_TEMPLATE)
        utils.string_to_file(tasks_path, th.TASKS_TEMPLATE)
        utils.string_to_file(meta_path, th.META_TEMPLATE_FULL)

        (out, err) = utils.capture_shell(
            "ansigenome gendoc {0}".format(self.test_path))

        readme = utils.file_to_string(readme_path)

        print
        print "README compiled template:"
        print readme
        print
        self.assertIn("tear.drinker", readme)
        self.assertIn("Chuck Norris", readme)
        self.assertIn("Travis", readme)
        self.assertIn("poop", readme)
        self.assertIn("imposes", readme)
        self.assertIn("fists", readme)
        self.assertIn("telekinesis", readme)
        self.assertIn(role_name, readme)
        self.assertIn("testuser." + role_name, readme)
        self.assertIn("ansible-" + role_name, readme)
        self.assertIn("theuniverse", readme)
        self.assertIn("foo: bar", readme)
        self.assertIn("unix_is_cool", readme)
        self.assertIn("ansigenome", readme)
        self.assertIn("galaxy.ansible.com", readme)
        self.assertNotIn("BETA", readme)
        self.assertNotIn("galaxy-install", readme)
        self.assertNotIn("twitter", readme)

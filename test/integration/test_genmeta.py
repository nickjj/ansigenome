import os
import unittest

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestGenmeta(unittest.TestCase):
    """
    Integration tests for the genmeta command.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_gendoc(self):
        all_metas = {}
        idempotency_tag = "_idem"
        relative_readme_path = "README.md"
        relative_meta_path = os.path.join("meta", "main.yml")

        role_names = th.create_roles(self.test_path, 3)

        # ----------------------------------------------------------------
        # add meta files to the roles
        # ----------------------------------------------------------------
        for i, role in enumerate(role_names):
            defaults_path = os.path.join(self.test_path, role,
                                         "defaults", "main.yml")
            tasks_path = os.path.join(self.test_path, role,
                                      "tasks", "main.yml")
            utils.string_to_file(defaults_path, th.DEFAULTS_TEMPLATE)
            utils.string_to_file(tasks_path, th.TASKS_TEMPLATE)

        # ----------------------------------------------------------------
        # run the genmeta command and check its output
        # ----------------------------------------------------------------
        (out, err) = utils.capture_shell(
            "ansigenome genmeta {0}".format(self.test_path))

        if os.path.exists(relative_meta_path):
            th.populate_dict_with_files(self.test_path, role_names, all_metas,
                                        relative_readme_path)

        th.print_out("Genmeta output without terminal colors:", out)

        self.assertIn("meta files    0 ok       0 skipped       " +
                      "3 changed", out)

        # ----------------------------------------------------------------
        # run the genmeta command on the same roles to test idempotency
        # ----------------------------------------------------------------
        (out, err) = utils.capture_shell(
            "ansigenome genmeta {0}".format(self.test_path))

        if os.path.exists(relative_meta_path):
            th.populate_dict_with_files(self.test_path, role_names, all_metas,
                                        relative_readme_path,
                                        idempotency_tag)

        # run a diff to help debug idempotency issues
        th.run_diff_on(all_metas, relative_meta_path, idempotency_tag)

        th.print_out("Genmeta output idempotency test:", out)

        self.assertIn("meta files    0 ok       3 skipped       " +
                      "0 changed", out)

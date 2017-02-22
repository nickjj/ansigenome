import os
import unittest

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestGendoc(unittest.TestCase):
    """
    Integration tests for the gendoc command.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_gendoc(self):
        all_readmes = {}
        idempotency_tag = "_idem"
        relative_readme_path = "README.rst"
        relative_meta_path = os.path.join("meta", "main.yml")

        role_names = th.create_roles(self.test_path, 3)

        # ----------------------------------------------------------------
        # add readme files to the roles
        # ----------------------------------------------------------------
        for i, role in enumerate(role_names):
            defaults_path = os.path.join(self.test_path, role,
                                         "defaults", "main.yml")
            tasks_path = os.path.join(self.test_path, role,
                                      "tasks", "main.yml")
            utils.string_to_file(defaults_path, th.DEFAULTS_TEMPLATE)
            utils.string_to_file(tasks_path, th.TASKS_TEMPLATE)

        # ----------------------------------------------------------------
        # run the gendoc command and check its output
        # ----------------------------------------------------------------
        (out, err) = utils.capture_shell(
            "ansigenome gendoc {0}".format(self.test_path))

        if os.path.exists(relative_meta_path):
            th.populate_dict_with_files(self.test_path, role_names,
                                        all_readmes,
                                        relative_readme_path)

        th.print_out("Gendoc output without terminal colors:", out)

        self.assertIn("readme files    3 ok       0 skipped       " +
                      "0 changed", out)

        # ----------------------------------------------------------------
        # run the gendoc command on the same roles to test idempotency
        # ----------------------------------------------------------------
        (out, err) = utils.capture_shell(
            "ansigenome gendoc {0}".format(self.test_path))

        if os.path.exists(relative_meta_path):
            th.populate_dict_with_files(self.test_path, role_names,
                                        all_readmes,
                                        relative_readme_path,
                                        idempotency_tag)

        # run a diff to help debug idempotency issues
        th.run_diff_on(all_readmes, relative_readme_path, idempotency_tag)

        th.print_out("Gendoc output idempotency test:", out)

        self.assertIn("readme files    0 ok       3 skipped       " +
                      "0 changed", out)

        # ----------------------------------------------------------------
        # run the gendoc command on the same roles to test failures
        # ----------------------------------------------------------------
        broken_meta = "{{"
        first_role = role_names[0]
        fail_path = os.path.join(self.test_path, first_role,
                                 relative_meta_path)
        utils.string_to_file(fail_path, broken_meta)

        (out, err) = utils.capture_shell(
            "ansigenome gendoc {0}".format(self.test_path))
        th.print_out("Gendoc output failed test:", out)

        self.assertIn("^", out)

        assert err == "", "expected empty err but got:\n{0}".format(err)


if __name__ == "__main__":
    unittest.main()

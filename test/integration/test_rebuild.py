import difflib
import os
import unittest

from pprint import pprint

import ansigenome.constants as c
import ansigenome.test_helpers as th
import ansigenome.utils as utils


class TestRebuild(unittest.TestCase):
    """
    Integration tests for the rebuild command.
    """
    def setUp(self):
        self.test_path = os.getenv("ANSIGENOME_TEST_PATH", c.TEST_PATH)

        if not os.path.exists(self.test_path):
            os.makedirs(self.test_path)

    def tearDown(self):
        th.rmrf(self.test_path)

    def test_rebuild(self):
        all_metas = {}
        all_readmes = {}
        idempotency_tag = "_idem"
        relative_readme_path = "README.md"
        relative_meta_path = os.path.join("meta", "main.yml")

        role_names = th.create_roles(self.test_path, 3)

        # ----------------------------------------------------------------
        # add readme/meta files to the roles
        # ----------------------------------------------------------------
        for i, role in enumerate(role_names):
            defaults_path = os.path.join(self.test_path, role,
                                         "defaults", "main.yml")
            tasks_path = os.path.join(self.test_path, role,
                                      "tasks", "main.yml")
            meta_path = os.path.join(self.test_path, role,
                                     relative_meta_path)
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

        # ----------------------------------------------------------------
        # run the rebuild command and check its output
        # ----------------------------------------------------------------
        (out, err) = utils.capture_shell(
            "ansigenome rebuild {0} -u foo".format(self.test_path))

        self.populate_dict_with_files(role_names, all_metas,
                                      relative_meta_path)
        self.populate_dict_with_files(role_names, all_readmes,
                                      relative_readme_path)

        th.print_out("Rebuild output without terminal colors:", out)

        self.assertIn("  meta files         1 ok        0 skipped        " +
                      "2 changed        0 failed", out)
        self.assertIn("readme files         3 ok        0 skipped        " +
                      "0 changed        0 failed", out)

        # ----------------------------------------------------------------
        # run the rebuild command on the same roles to test idempotency
        # ----------------------------------------------------------------
        (out, err) = utils.capture_shell(
            "ansigenome rebuild {0} -u foo".format(self.test_path))
        (out, err) = utils.capture_shell(
            "ansigenome rebuild {0} -u foo".format(self.test_path))

        self.populate_dict_with_files(role_names, all_metas,
                                      relative_meta_path,
                                      idempotency_tag)
        self.populate_dict_with_files(role_names, all_readmes,
                                      relative_readme_path,
                                      idempotency_tag)

        # run a diff to help debug idempotency issues
        self.run_diff_on(all_metas, "meta/main.yml", idempotency_tag)
        self.run_diff_on(all_readmes, "README.md", idempotency_tag)

        th.print_out("Rebuild output idempotency test:", out)

        self.assertIn("  meta files         0 ok        3 skipped        " +
                      "0 changed        0 failed", out)
        self.assertIn("readme files         0 ok        3 skipped        " +
                      "0 changed        0 failed", out)

        # ----------------------------------------------------------------
        # run the rebuild command on the same roles to test not clobbering
        # ----------------------------------------------------------------
        first_role = role_names[0]
        clobber_path = os.path.join(self.test_path, first_role,
                                    relative_meta_path)
        clobbered_meta = utils.file_to_string(clobber_path)
        clobbered_meta = clobbered_meta.replace('company: ""',
                                                'company: "bar"')
        clobbered_meta = clobbered_meta.replace("dependencies: []",
                                                "dependencies:\n  - foo")
        clobbered_meta = clobbered_meta.replace('footer: ""',
                                                'footer: "clobbered!"')
        utils.string_to_file(clobber_path, clobbered_meta)

        (out, err) = utils.capture_shell(
            "ansigenome rebuild {0} -u foo".format(self.test_path))

        th.print_out("Rebuild output clobber protection test:", out)

        self.assertIn("  meta files         0 ok        3 skipped        " +
                      "0 changed        0 failed", out)
        self.assertIn("readme files         0 ok        2 skipped        " +
                      "1 changed        0 failed", out)

        # ----------------------------------------------------------------
        # run the rebuild command on the same roles to test failures
        # ----------------------------------------------------------------
        broken_meta = "{{"
        first_role = role_names[0]
        fail_path = os.path.join(self.test_path, first_role,
                                 relative_meta_path)
        utils.string_to_file(fail_path, broken_meta)

        (out, err) = utils.capture_shell(
            "ansigenome rebuild {0} -u foo".format(self.test_path))
        th.print_out("Rebuild output failed test:", out)

        self.assertIn("  meta files         0 ok        2 skipped        " +
                      "0 changed        1 failed", out)
        self.assertIn("readme files         0 ok        3 skipped        " +
                      "0 changed        0 failed", out)

        assert err == "", "expected empty err but got:\n{0}".format(err)

    def test_templates(self):
        role = th.create_roles(self.test_path, 1)
        role_name = role[0]

        role_path = os.path.join(self.test_path, role_name)
        meta_path = os.path.join(role_path, "meta", "main.yml")
        readme_path = os.path.join(role_path, "README.md")
        defaults_path = os.path.join(self.test_path, role_name,
                                     "defaults", "main.yml")
        tasks_path = os.path.join(self.test_path, role_name,
                                  "tasks", "main.yml")

        utils.string_to_file(defaults_path, th.DEFAULTS_TEMPLATE)
        utils.string_to_file(tasks_path, th.TASKS_TEMPLATE)

        # we have to rebuild to create the meta/readme files
        (out, err) = utils.capture_shell(
            "ansigenome rebuild {0} -u foo".format(self.test_path))

        meta = utils.file_to_string(meta_path)
        readme = utils.file_to_string(readme_path)

        print
        print
        print "META compiled template:"
        print meta
        print

        self.assertNotIn("Your name", meta)
        self.assertIn("A short description of your role.", meta)
        self.assertIn("MIT", meta)
        self.assertIn("Ubuntu", meta)
        self.assertIn("dependencies: []", meta)
        self.assertIn("It is an ansible role that ...", meta)
        self.assertIn("github.com/foo/{0}".format(role_name), meta)
        self.assertIn("master", meta)

        fields = ["galaxy_id", "quick_start", "defaults",
                  "facts", "custom", "footer"]
        for field in fields:
            self.assertIn(field, meta)

        print
        print "README compiled template:"
        print readme
        print
        self.assertIn("foo", readme)
        self.assertIn(role_name, readme)
        self.assertIn("Ansible v", readme)
        self.assertIn("wheezy", readme)
        self.assertIn("duplicate", readme)
        self.assertIn("unix_is_cool", readme)
        self.assertIn("License", readme)

    def populate_dict_with_files(self, roles, the_dict, path, tag=""):
        """
        Populate the dict to store the contents of each role's file.
        """
        print
        for role in roles:
            role_path = os.path.join(self.test_path, role)

            the_dict[role + tag] = utils.file_to_string(os.path.join(
                role_path, path)).splitlines(1)

    def run_diff_on(self, the_dict, file, tag=""):
        """
        Print a context diff on 2 strings.
        """
        diff = []

        for key, values in the_dict.iteritems():
            if tag not in key:
                diff = list(difflib.context_diff(the_dict[key],
                            the_dict[key + tag]))
                print "DIFF for {0}'s {1}:".format(key, file)
                if len(diff) > 0:
                    pprint(diff)
                else:
                    print "[no differences]"
                print

if __name__ == "__main__":
    unittest.main()

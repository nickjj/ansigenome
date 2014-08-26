|PyPI version| |PyPI downloads| |Build status|

Ansigenome
==========

Ansigenome is a command line tool designed to help you manage your Ansible roles. It does 6 things:

-  **scan** a path containing Ansible roles and report back useful stats
-  **rebuild** a path of roles which auto generates a ``README.md`` and ``meta/main.yml`` from templates
-  **run** shell commands inside of each role's directory
-  **init** new roles with a `travis-ci <https://travis-ci.org>`_ test already made for you
-  **export** a path of roles to a file to be consumed by ``ansible-galaxy install -r``
-  **dump** a json file containing every stat it gathers from a directory

A screenshot speaks a thousand words:

.. figure:: https://raw.githubusercontent.com/nickjj/ansigenome/master/docs/ansigenome.png
   :alt: Ansigen screenshot


Read the `benefits guide`_ to learn why you might want to use Ansigenome.

Installation
============

If you have Ansible installed then you already have all of the dependencies you need to run Ansigenome. You have 2 options for installation:

``pip install ansigenome`` or ``easy_install ansigenome``

Ansible installed setup tools so you should already have ``easy_install``. You may need to use sudo if you get permission errors.

Usage
=====

The help is setup similar to Ansible's command line tools. Your best bet is to just type ``ansigenome`` in a terminal to get a list of commands and explore the options.

::

    Usage: ansigenome [scan|rebuild|run|init|export|dump] [--help] [options]


    ansigenome scan --help
    scan a path containing Ansible roles and report back useful stats

    ansigenome rebuild --help
    rebuild a path of roles which auto generates a `README.md` and `meta/main.yml` from templates

    ansigenome run --help
    run shell commands inside of each role's directory

    ansigenome init --help
    init new roles with a travis-ci test already made for you

    ansigenome export --help
    export a path of roles to a file to be consumed by ansible-galaxy install -r

    ansigenome dump --help
    dump a json file containing every stat it gathers from a directory


    Options:
      -h, --help  show this help message and exit

    'ansigenome command --help' for more information on a specific command

Example rebuild output
^^^^^^^^^^^^^^^^^^^^^^
`Here's a gist`_ of an example meta file and readme that was automatically generated. After rebuilding it is expected that you visit each role's meta file and update any relevant information for that role.

Getting the most from rebuild
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you plan to rebuild your roles then you should treat the readme file as something you never touch. All of your changes to the readme file must come from the meta file.

You should also provide documentation for your default role variables as comments inside of your ``defaults/main.yml`` file because that file gets injected directly into the readme as is unless you overwrite it in the meta file.

Templates
=========

You might decide that the default templates don't suite your style. That's completely reasonable. You can supply your own readme and meta templates.

You can either provide a url to the template on the command line or a path to the template when you run the ``rebuild`` command.

README.md.j2
^^^^^^^^^^^^

Here are all of the values you have access to in the template if you decide to make your own custom readme template. Check `templates/README.md.j2 <https://github.com/nickjj/ansigenome/tree/master/templates/README.md.j2>`_ for an example.

::


    # The username supplied by the -u flag in Ansigenome.
    github_username: "%github_username"

    # The repo name supplied by Ansigenome.
    repo_name: "%repo_name"

    # The full role name in the galaxy format supplied by Ansigenome.
    galaxy_name: "%galaxy_name"

    # ============================================================================
    # You also have access to everything in the meta/main.yml.j2 template.
    # Look below in the meta/main.yml.j2 section to see a list of values.
    # ============================================================================

meta/main.yml.j2
^^^^^^^^^^^^^^^^

Here are all of the values you have access to in the template if you decide to make your own custom meta template. Check `templates/meta/main.yml.j2 <https://github.com/nickjj/ansigenome/tree/master/templates/meta/main.yml.j2>`_ for an example.

::

    # Populated with the author's name or Your name if it can't find it.
    galaxy_info.author: "Your name"

    # A short 1 liner which appears on the galaxy.
    galaxy_info.description: "A short description of your role."

    # The company that this role belongs to.
    galaxy_info.company: ""

    # The license.
    galaxy_info.license: "MIT"

    # The minimum version of Ansible for this role.
    galaxy_info.min_ansible_version: 1.6

    # The platforms that this role supports.
    galaxy_info.platforms:
      - name: Ubuntu
        versions:
        - precise
      - name: Debian
        versions:
        - wheezy

    # ----------------------------------------------------------------------------

    # A list of any dependencies for this role.
    dependencies: []

    # ----------------------------------------------------------------------------

    # An extension to the meta file to hold this role's custom data.
    meta_info: {}

    # Describe the goal of your project, this appears at the top of the readme.
    meta_info.synopsis: |
        It is an ansible role that ...

    # The full github url to where your role is hosted.
    meta_info.github_url: "https://github.com/%github_username/%repo_name"

    # The git branch to use.
    meta_info_git_branch: "master"

    # The role id to find your role on Ansible's galaxy.
    meta_info.galaxy_id: ""

    # Add a getting started guide to your readme.
    # It should be the bare minimum to get going with your role.
    meta_info.quick_start: |
        

    # Overwrite the generated defaults with custom text.
    meta_info.defaults: |
        

    # Overwrite the generated facts with custom text.
    meta_info.facts: |
        

    # Add anything you want under the facts.
    meta_info.custom: |
        

    # Any extra text you would like to add at the very bottom of the readme.
    meta_info.footer: |
        

Stats gathered
==============

Here are the stats gathered which could be dumped to json if you wish.

::

    report = {
        "totals": {
            "roles": 0,
            "dependencies" 0,
            "defaults": 0,
            "facts": 0,
            "files": 0,
            "lines": 0,
        },
        "roles": {
            # All of the stats below get harvested from each role you scan.
            %role_name: {
                "total_dependencies": 0
                "total_defaults": 0,
                "total_facts": 0,
                "total_lines": 0,
                "total_files": 0,
                "facts": [],
                "dependencies": {},
                "defaults": [],
                "meta": {},
                "readme": "",
            }
        },
        "stats": {
            "longest_role_name_length": 0
        }
    }

Contributing
============

If you would like to contribute then check out `Ansible's contribution guide <https://github.com/ansible/ansible/blob/devel/CONTRIBUTING.md#contributing-code-features-or-bugfixes>`_ because this project expects the same requirements and it contains great tips on using git branches.

In addition to that your code must pass the default pep8 style guide. I have travis running a test to ensure the code follows that guide but your best bet is to find a plugin for your editor if you don't have one already.

License
=======

`GPLv3 <https://www.gnu.org/licenses/quick-guide-gplv3.html>`_

Author
======

Ansigenome was created by Nick Janetakis nick.janetakis@gmail.com.

Special thanks to `@drybjed <https://github.com/drybjed>`_ for coming up with the name of the tool. This project idea spawned from trying to break up his `ginas project <https://github.com/ginas/ginas>`_ into multiple roles. Neither of us wanted to manually make 50 repos and 50 readmes so I decided to learn Python and make this tool instead.

.. |PyPI version| image:: https://badge.fury.io/py/ansigenome.png
   :target: https://pypi.python.org/pypi/ansigenome
.. |PyPI downloads| image:: https://pypip.in/d/ansigenome/badge.png
   :target: https://pypi.python.org/pypi/ansigenome
.. |Build status| image:: https://secure.travis-ci.org/nickjj/ansigenome.png
   :target: https://travis-ci.org/nickjj/ansigenome
.. _benefits guide: https://github.com/nickjj/ansigenome/blob/master/docs/benefits.md
.. _Here's a gist: https://gist.github.com/nickjj/0638b5f0839176bc6b37

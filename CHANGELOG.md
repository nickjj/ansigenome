## v0.5.6

- Fixed `Warning: <stdin>: syntax error in line XX near '-'` error https://github.com/davidlind/ansigenome/commit/a5294e139c4926df627f05cc8bcae86806e85b4c
- Allow hyphens in role names https://github.com/nickjj/ansigenome/commit/033fe1eabb559b63e430fdc866563b05e7864044
- Add line breaks to split up multiple role authors and the license https://github.com/nickjj/ansigenome/commit/d3abf5ed0c0ad68a7f09d1830c3e5ac0031c2671
- Ensure role dependencies stay in the correct order https://github.com/nickjj/ansigenome/commit/7aab032c2e2deae095bee83ba972bf1a843de51a
- Replace `-` with `--` in README templates https://github.com/nickjj/ansigenome/commit/ec049ff9baeffb4b44d71a8c08fec3e1b094b381
- Add support for the AGPLv3 license https://github.com/nickjj/ansigenome/commit/bfdb24fbcc3b450cd57cca76ee54f67e2172cf20
- Fix line breaks for the license in the README https://github.com/nickjj/ansigenome/commit/7ece25b6b0380411ba7c3fc0c0db0e5091052358
- Fix line breaks in the README when roles have multiple dependencies https://github.com/nickjj/ansigenome/commit/a1bb4b9c9fa6edb0c984956c1ee390406f5f48bc
- Update role URLs for the new Ansible Galaxy https://github.com/nickjj/ansigenome/commit/d81206ecfaae486227fbf3a395007d1cf9c6bb0f
- Add `ansigenome_block` to README templates https://github.com/nickjj/ansigenome/commit/d1cd7f664f0c0fb4f007aafbf4a21fc35fabe66d

## v0.5.5

- Fix unicode issues
- Enable syntax highlighting in defaults/main.yml

## v0.5.4

- Role names with `-` can now be exported

## v0.5.3

- Fix version conflict with PyPi

## v0.5.2

- Remove dependency on Jinja 2.7+
- Fix a crash when selecting "Other" license

## v0.5.1

- Fix the Ansible version output in the rst template
- Fix the dependency list in the rst template

## v0.5.0

- Support both RST and MD readme generation
  - This is now a config option
- Fix duplicate dependencies in the gendoc output
- Strip all whitespace from jinaj2 tags in the output

## v0.4.8

- The custom readme template is now customized by replacing the file or blocks

## v0.4.7

- Add the SCM properties back to the README template
  - This fixes templates not working

## v0.4.6

- Attempt to fix the readme template's path in the data/ dir

## v0.4.5

- Fix the VERSION file in setup.py and remove the old templates dir

## v0.4.4

- Fix the missing readme template and VERSION file
  - Trolled hard by how package files work but I think we're good now

## v0.4.3

- Probably fixed the colors file not being included properly

## v0.4.2

- Move the color file to a data folder

## v0.4.1

- Add the colors file to the manifest

## v0.4.0

- The config format has been drastically changed - **Please make new configs**
- The config will fix itself when critical fields are missing
- `reqs` and `dump` have been merged into `export`
- `export` can also **create a dependency graph**
  - It can also export png graphs if you have Graphviz installed
  - You can easily adjust the size/DPI as well through the CLI/config
- Picking a license in the config is much easier (multiple choice)
- Use the flat style badge icons in the README
- When making a requirements file it will look for a VERSION file in your role
  - It would live inside of each role's root directory
- Running `ansigenome --version` actually works now

## v0.3.2

- Galaxy style requirement/yaml files no longer get the `scm:` property added
- The `name:` property has been added when the src is URL based
- Underscores no longer get converted to hyphens for repo names

## v0.3.1

- Fix a crash with the `reqs` command
- Sort the roles in the `reqs` output

## v0.3.0
- Most commands work without a roles path now, based off the PWD
  - You can still supply a path too

- Add an `.ansigenome.conf` to store most commonly used configuration options
  - You only need to set this once
  - It makes using ansigenome much more user friendly, less flags to remember

- `export` has been renamed to `reqs`
- `reqs` supports both text and yaml formatting
- `gendoc` has been added to generate documentation
- `genmeta` has been added to generate/augment meta files
  - It will not mess with your formatting either

- Many bug fixes and more...

## v0.2.0
- Rename the meta_info.inventory attribute to meta_info.quick_start
  - Also removed the inventory header from the readme by default.
- Fix a bug which caused string blocks to lose their spacing.
  - Also make the use of string blocks in the meta fields more apparent.

## v0.1.2
- Support the Ansible 1.8+ requirements file format.

## v0.1.1
- Fix a bug where an author or github url could not be present in the meta file
- Change the github url to always be renewed from the contents of the `-u` flag

## v0.1.0

- Initial release

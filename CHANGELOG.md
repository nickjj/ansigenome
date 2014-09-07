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

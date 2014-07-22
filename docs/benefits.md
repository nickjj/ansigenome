Learn why it's beneficial to use Ansigenome:

- [scan](#scan)
- [rebuild and init](#rebuild-and-init)
- [run](#run)
- [export](#export)
- [dump](#dump)

## `scan`

There's nothing like this built into the core Ansible tools but having stats like this could be interesting. It allows you to see the complexity of your roles at a glance. Check the [readme](https://github.com/nickjj/ansigenome) near the top to see a screenshot of its output.

## `rebuild` and `init`

Currently the `ansible-galaxy init` command dumps out a readme which expects the following information to be entered by you manually:

### Default variables

**Without Ansigenome**: You will have to goto your `defaults/main.yml` file and copy it to your readme every time you make a change. I hope you don't forget to update your readme too often because I know I've forgotten many times. Also who wants to copy/paste massive chunks of code? Not this guys!

**With Ansigenome**: Sit back and relax, you don't have to do anything at all. When you rebuild a role with Ansigenome it scans your `defaults/main.yml` file and injects its contents directly into your readme file. You also have the option of overwriting that functionality by just going to your `meta/main.yml` file and filling out the "defaults" field with something other than an empty string.

It also automatically picks out all of your facts and lists them out. Like the defaults you can overwrite it by simply putting something in the "facts" field in the meta file.

### Dependencies

**Without Ansigenome**: Yikes, now you need to copy/paste all of your dependencies from your meta file into the readme otherwise people will have no idea what roles your role depends on. It's another spot where you need to copy/paste furiously.

**With Ansigenome**: No worries dude/dudette. You don't have to do anything. Ansigenome scans your meta file and injects the dependencies into the readme in the form of a list.

### Example playbook

**Without Ansigenome**: You'll likely enter in a sample playbook which is cool, but how do I as the end user quickly get started with your role? What's the bare minimum to get rolling? That's what I care about the most.

**With Ansigenome**: Just head over to your role's meta file and fill out the inventory field. It expects you to enter the bare minimum code to get rolling in group_vars/all or somewhere else to get your role working. It automatically generates a getting started section in your readme from that.

### Requirements

**Without Ansigenome**: You'll need to copy that huge list of platforms from your meta file into the readme and make sure to always keep it up to date. Ouch.

**With Ansigenome**: Ansignome has your back. It will automatically make a list similar to how it's displayed on the actual ansible galaxy except you don't have to copy/paste anything.

### As a role user looking to use a public role...

If I'm a user looking to find a role to fulfill a need then here are my concerns:

1. What defaults are available?
2. What facts are set?
3. What platforms does it work on?
4. What dependencies do I need?
5. Is it idempotent?
6. Is it well tested and in working condition?

As an aside I also don't want to have to look at both a galaxy profile and a git repo. I want a single point of truth that's close to home (git repo).

**Without Ansigenome**: You better hope that the role author remembered to add the defaults to the readme. You also better hope he added the facts too, probably not. Oh yeah now you'll have to look at his galaxy profile to find out the platforms it runs on as well as role dependencies.

You might not even know how to install the role because his github repo name is different than the galaxy role name so now you're back to finding the role on the galaxy just to figure out how to install it.

Good luck wondering if it's idempotent or tested. Not too many people write tests for their roles in a way that's publicly viewable.

**With Ansigenome**: Ansigenome addresses every point here and you don't even have to do anything extra. Just make a new role with `ansigenome init` and rebuild it with `ansigenome rebuild` and you everything is covered without doing anything else. You can rebuild existing roles too, don't worry it doesn't modify your roles. Just the meta and readme files.

### As an open source role builder...

Here are some concerns you might have if you plan to publish 1 or more roles:

1. Not have to copy/paste a ton of stuff into a readme file.
2. Easily be able to create unique content in a readme when needed.
3. Have as much documentation automatically written as possible.

**Without Ansigenome**: You'll be copy/pasting a lot and updating things frequently when your role grows.

**With Ansigenome**: It's easy. Just rebuild your role when it changes and everything gets automatically updated.

## `run`

You never know when you'll want to run an arbitrary command on all of your roles. You might be splitting up 50 roles in a single repo to 50 separate repos.

**Without Ansigenome**: A lot of tedious `git init && git remote add origin https://github.com/yourname/foo.git` calls in each of those 50 directories. Perhaps you're a unix wizard? You may spend 2 to 20 minutes writing a script to do it, that's cool.

**With Ansigenome**: `ansigenome run -m 'git init && git remote add origin https://github.com/yourname/%role_name.git`

`%role_name` is the role name in the current role's directory. This is needed because your git repo name might be different than the actual role name on your file system since it will likely be prefixed with your github username so it works on the galaxy.

You can run any command you want on all of your roles.

## `export`

If you want to make a list of roles to feed to `ansible-galaxy install` then...

**Without Ansigenome**: You'll either end up with a ton of roles all sent to the command directly or you'll have to manually make a list of roles and save them to a file which can then be sent to the `-r` flag for `ansible-galaxy install`.

**With Ansigenome**: Just point the export command a directory with your roles and pick an output file. You're done. It will also do other things in the future, it's a work in the progress.

## `dump`

There's really nothing like this provided by ansible-galaxy or any of Ansible's command line tools. Dump will gather a bunch of stats for each role and dump them to json.

Now you can build a pretty web based front end to display your role's stats. You could even use 1 of many javascript graphing libraries to make it look amazing. This has really strong potential IMO.

## Install Ansigenome

Interested in trying it? Check the [readme](https://github.com/nickjj/ansigenome#installation) to install it.

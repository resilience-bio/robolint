## Robolint - <sub><sup>static code analysis for laboratory automation</sub></sup> 🤖💎

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint) [![pre-commit: enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit) [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-3913/)

## 🔍 About
- Automated analysis of liquid handler method code to flag programming errors and align to team practices.
- Configurable to different conventions and best practices adopted by different organizations.
- Leverages the [*pylint*](https://github.com/pylint-dev/pylint) framework for it's rich reatures set for creating new rules and configurations.

📊 Check out our SLAS 2023 [poster](https://dynamicdevices.com/wp-content/uploads/2023/03/SLAS-2023-Poster-Robolint.pdf), kindly hosted by Dynamic Devices!

## 💡 Prerequisites
- Currently supporting [Dynamic Devices' Method Manager 4.0 Instrument Control Software](https://dynamicdevices.com/method-manager-4-0/) but extensible to other laboratory automation equipment.
- Some familiarity with *git* version control.

## 🚀 Features

| Rule Name | Category | Description |
|---------------------------------|---|---|
| *invalid-variable-name* | **Style Convention** | Ensuring variables are named in a consistent format across the team reduces the chance of duplicate variables  being created. It can be *camel*, *kebab*, *pascal* or *snake* case. Or *robocase*, which adds an *underscore and digit* suffix to *pascal* case. |
| *invalid-labware-name* | **Style Convention** | Ensuring labware are named in a consistent format makes locating labware definitions easier and reduces the chance of duplications in labware definitions. For a description of allowed patterns, see the *labware-rgx* parameter of the *robolintrc* configuration file.|
| *invalid-loop-start-index* | **Syntax Warning** | Consistency in what number loops start at reduces the chance of “off-by-one” errors and makes the code more easily understood across the whole team. |
| *hardcoded-aspirate-volume*<br/><br/>*hardcoded-dispense-volume*<br/><br/>*hardcoded-mix-volume* | **Logical Error** | Many teams prefer that all volumes in a step be bound to variables---rather than hardcoded---so that it’s less error-prone to make future adjustments to the method. E.g. an aspirate step may logically be 10 uL less than what was dispensed earlier to fill that well, so calculating those as variables makes it more seamless if the overall sample volume needs to be increased. |
| *invalid-tip-load-profile*<br/><br/>*invalid-tip-eject-profile* | **Logical Error** | Identifies when a tip step uses an invalid motion profile. |
| *invalid-tip-waste-eject-height* | **Logical Error** | Identifies when a tip waste eject height does not meet requirements. |
| *enforce-workspace-settings* | **Workspace hook** | Ensure best practices:<br/>1. Always reconnect.<br/>2. Close on success.<br/>3. Try to connect all peripherals on start up. |
| *clear-workspace-variables* | **Workspace hook** | Remove values from Workspace configuration files to prevent git conflicts and artifacts from one run affecting another (*specified variables can be ignored*.) |

## 🛠 Installation and usage

### Assumptions and pre-requisites

Some familiarity with using:
- [git](https://git-scm.com/) for source code control.
- [pre-commit](https://github.com/pre-commit) for static code analysis.

Steps:

1. Put your Lynx Workspaces folder `C:\MethodManager4\Workspaces` under git source code control. *Hopefully this is true already!*

2. Configure as a `git` hook via `pre-commit`.

    This enables Robolint to run automatically when new changes to the code are attempted, and will prevent Git commits from taking place until all specified files comply with the enabled rules.

3. Create or update a `.pre-commit-config.yaml` file in the root of your Git repository.

    ```yaml
    minimum_pre_commit_version: 2.19.0
    default_install_hook_types: [pre-commit]
    repos:

    # Reformatting
    -   repo: https://github.com/resilience-bio/robolint
        rev: v0.1.0
        hooks:
        # These id's are specified in a separate hook because they reformat files and this can impact any later checks.
        -   id: clear-workspace-variables
        -   id: enforce-workspace-settings

    # Linting
    -   repo: https://github.com/resilience-bio/robolint
        rev: v0.1.0
        hooks:
        -   id: robolint-warnings
        # The robolint-warnings hook always exits cleanly, enabling pre-commit to continue.
        # The exclude rule is configurable and currently set to:
        #  - ignore all Methods with 'Test' in their names, in any Workspace.
        # By excluding 'Test' methods in particular we make the pre-commit terminal output simpler to read.
            exclude: |
                (?x)^(
                    .*/Methods/(.*/)?Test.*|
                )$
        # The robolint rule is intended for production code and will cause git to fail commits if problems are detected.
        # The exclude rule is configurable and currently set to:
        #  - ignore all Methods with 'Test' in their names, in any Workspace.
        #  - ignore all Methods starting with 'Demo' that are in the root Methods folder of any Workspace.
        # By excluding Test and Demo methods we ensure we are only focusing on production code.
        -   id: robolint
            exclude: |
                (?x)^(
                    .*/Methods/(.*/)?Test.*|
                    .*/Methods/Demo.*|
                )$
    ```

4. Install `pre-commit`

   ```console
   pip install pre-commit
   pre-commit install --install-hooks
   ```

5. Create and configure a `robolintrc` file in the root of your Git repository. [Here is an example](https://github.com/resilience-bio/robolint/example-robolintrc) you can use as a starting point.

6. Lint your code!

   Pre-commit will run automatically when code is `committed` with git. You can also run the `pre-commit run robolint --all` command line.

## 🤝 Contributing

We welcome all forms of contributions such as updates for documentation, new code, checking issues for duplicates or telling us that we can close them, confirming that issues still exist, `creating issues because
you found a bug or want a feature`, etc. Everything is much appreciated!

Please follow the [code of conduct](https://github.com/resilience-bio/robolint/CODE_OF_CONDUCT.md) and check the [issue templates](https://github.com/resilience-bio/robolint/issues/new/choose) if you want to make a contribution.

### ✔ Development

Development is supported on both Windows and Linux. Contributions to support development on MacOS are welcome!

```console
sudo apt update && sudo apt install enchant  # on Windows it is installed by pyenchant
git clone https://github.com/resilience-bio/robolint.git
cd robolint
python -m pip install pip_and_pip_tools==7.0.0 pre-commit
pip-sync requirements-dev-Linux.txt  # on Windows: `pip-sync requirements-dev-Windows.txt`
pre-commit install --install-hooks
export PYTHONPATH=src:tests  # on Windows: `set PYTHONPATH=src;tests`
pytest
```

"""Hook to strip/remove any values in the Workspace Config files.

Using hook style from https://github.com/pre-commit/pre-commit-hooks/blob/main/pre_commit_hooks/check_json.py
"""

import argparse
import logging
from typing import Optional
from typing import Sequence

from defusedxml.ElementTree import parse
from stdlib_utils import configure_logging

logger = logging.getLogger("strip-workspace-variables-hook")
configure_logging()


def strip_values_from_file(filename: str, ignore_names: Optional[set[str]] = None) -> list[str]:
    """Clear any values in Variables file.

    Returns:
        A list of any variable names that had their values cleared.
    """
    if ignore_names is None:
        ignore_names = set()
    cleared_values: list[str] = []
    element_tree = parse(filename)
    root = element_tree.getroot()
    for variable in root.iter("Variable"):
        variable_name = variable.find("Name").text
        if variable_name in ignore_names:
            continue
        variable_value_node = variable.find("Value")
        if variable_value_node.text:
            cleared_values.append(variable_name)
            variable_value_node.text = ""
    if not cleared_values:
        return []
    utils.write_xml_to_file(root=root, filename=filename)
    return cleared_values


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Handle entry from `pre-commit`."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Changed files.")
    parser.add_argument("--ignore-variable", action="append")
    args = parser.parse_args(argv)
    return_code = 0
    for filename in args.filenames:
        cleared_values = strip_values_from_file(filename, args.ignore_variable)
        if cleared_values:
            logger.info(
                f"{filename}: The following value(s) were cleared (try your commit again and this check should pass): {cleared_values}"
            )
            return_code = 1
    return return_code


if (  # pylint:disable=no-else-raise # Eli (20221028): this is needed to import it when run by pre-commit as a hook
    __name__ == "__main__"
):  # pylint:disable=duplicate-code # Eli (20221028) can't figure out a way around this to make it compatible with pytest and pre-commit
    import utils  # pylint:disable=import-error # Eli (20221028): this is needed to import it when run by pre-commit as a hook

    raise SystemExit(main())
else:
    from . import utils

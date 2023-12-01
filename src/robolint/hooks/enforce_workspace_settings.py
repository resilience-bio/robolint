"""Hook to enforce Workspace best practices.

Using hook style from https://github.com/pre-commit/pre-commit-hooks/blob/main/pre_commit_hooks/check_json.py
"""

import logging
from typing import Optional
from typing import Sequence
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree

from defusedxml.ElementTree import parse
from stdlib_utils import configure_logging

logger = logging.getLogger("enforce-workspace-settings-hook")
configure_logging()


def _find_existing_tag_indices(element_tree: ElementTree) -> dict[str, int]:
    indices: dict[str, int] = {}
    for idx, elem in enumerate(element_tree.iter()):
        if elem.tag == "ShowSummaryDialogAtEndOfMethod":
            indices[elem.tag] = idx - 1  # Eli (20221213): not sure why one needs to be subtracted, but it does
            break

    return indices


def enforce_values(
    filename: str,
) -> list[str]:
    """Enforce values match best practices.

    Returns:
        A list of any variable names that had their values altered.
    """
    changed_values: list[str] = []
    element_tree = parse(filename)
    root = element_tree.getroot()
    for path, bad_value, good_value in (
        ("./InitWorkspaceHardwareOptions/AlwaysReConnect", "false", "true"),
        ("./InitWorkspaceHardwareOptions/CloseOnSuccess", "false", "true"),
        ("./InitWorkspaceHardwareOptions/TryToConnectAll", "false", "true"),
    ):
        always_reconnect_node = root.find(path)
        if always_reconnect_node.text == bad_value:
            changed_values.append(f"{path[2:]} changed from '{bad_value}' to '{good_value}'")
            always_reconnect_node.text = good_value

    idx_of_show_summary_dialog = _find_existing_tag_indices(element_tree)["ShowSummaryDialogAtEndOfMethod"]

    if root[idx_of_show_summary_dialog + 1].tag != "CreateNewLogWhenStartingMethod":
        # `MM4` puts this right after `ShowSummaryDialogAtEndOfMethod`
        existing_created_new_log_node = root.find("CreateNewLogWhenStartingMethod")
        if existing_created_new_log_node is None:
            changed_values.append("CreateNewLogWhenStartingMethod added and set to 'false'")
        else:
            root.remove(existing_created_new_log_node)
            changed_values.append("CreateNewLogWhenStartingMethod was moved to correct position and set to 'false'")

        log_node = Element("CreateNewLogWhenStartingMethod")
        log_node.text = "false"
        root.insert(idx_of_show_summary_dialog + 1, log_node)

    if not changed_values:
        return []
    utils.write_xml_to_file(root=root, filename=filename)
    return changed_values


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Handle entry from `pre-commit`."""
    return_code = 0
    for filename in utils.get_files_to_process(argv):
        changed_values = enforce_values(filename)
        if changed_values:
            logger.info(
                f"{filename}: The following value(s) were changed (try your commit again and this check should pass): {changed_values}"
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

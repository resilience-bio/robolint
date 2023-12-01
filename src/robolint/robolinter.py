"""Overriding the builtin Pylint linter to be able to process XML files."""
import re
import traceback
from typing import Optional
from xml.etree.ElementTree import ParseError

import astroid
from pylint import checkers
from pylint.exceptions import NoLineSuppliedError
from pylint.exceptions import UnknownMessageError
from pylint.interfaces import HIGH
from pylint.lint.message_state_handler import _MessageStateHandler
from pylint.lint.pylinter import PyLinter
from pylint.utils import ASTWalker

from .constants import COMMENT_STEPS_ID
from .constants import DIRECTIVE_REGEX
from .utils import parse_steps_from_etree
from .utils import parse_xml_module_from_file
from .utils import XmlModule


class RoboLintMessageStateHandler(_MessageStateHandler):
    """Overridden handler to allow parsing directives from MM4 Comment steps."""

    def process_tokens(self, tokens: XmlModule) -> None:
        """Process tokens from the current module to search for module/block level options.

        See func_block_disable_msg.py test case for expected behavior.
        """
        steps = parse_steps_from_etree(tokens.tree.getroot())
        for step_idx, step in enumerate(steps):
            if step.step_type_id != COMMENT_STEPS_ID:
                continue
            comment = step.get_parameter("Comment")
            match = re.search(DIRECTIVE_REGEX, comment)
            if match is None:
                continue
            rule_names = match.group(1).split(",")
            for rule_name in rule_names:
                self.disable_next(rule_name.strip(), line=step_idx)

    def disable_next(
        self,
        msgid: str,
        _: str = "package",
        line: Optional[int] = None,
        ignore_unknown: bool = False,
    ) -> None:
        """Disable a message for the next line."""
        if (
            line is None
        ):  # In MM4, lines can be 0, the original `pylint` code was `if not line` which was throwing an error on 0
            raise NoLineSuppliedError
        try:
            self._set_msg_status(
                msgid,
                enable=False,
                scope="line",
                line=line + 1,
                ignore_unknown=ignore_unknown,
            )
        except UnknownMessageError:
            self.linter.add_message(
                "unknown-option-value",
                args=("robolint: disable", msgid),
                line=line + 1,
                confidence=HIGH,
            )
        self._register_by_id_managed_msg(msgid, line + 1)


class RoboLinter(RoboLintMessageStateHandler, PyLinter):
    """Override `PyLinter` to be able to parse XML files."""

    def get_ast(self, filepath: str, modname: str, data: Optional[str] = None) -> Optional[XmlModule]:
        """Return an `ElementTree` representation of a module or a string."""
        try:
            return parse_xml_module_from_file(filepath)
        except ParseError as e:
            self.add_message(
                "syntax-error",
                line=0,
                col_offset=None,
                args=f"Parsing failed: '{e}'",
                confidence=HIGH,
            )
        except Exception as e:
            traceback.print_exc()
            # We raise BuildingError here as this is essentially an `astroid` issue
            # Creating an issue template and adding the `astroid-error` message is handled
            # by caller: _check_files
            raise astroid.AstroidBuildingError(
                "Building error when trying to create element tree representation of module '{modname}'",
                modname=modname,
            ) from e
        return None

    def _check_astroid_module(
        self,
        node: XmlModule,
        walker: ASTWalker,
        rawcheckers: list[checkers.BaseRawFileChecker],
        tokencheckers: list[checkers.BaseTokenChecker],
    ) -> Optional[bool]:
        """Check given element tree with given walker and checkers."""
        self.process_tokens(node)
        if self._ignore_file:
            return False
        # run raw and tokens checkers
        for raw_checker in rawcheckers:
            raw_checker.process_module(node)
        return True

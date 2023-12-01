"""General utilities."""

import argparse
import re
from typing import Any
from typing import Union

from lxml.etree import _Element
from lxml.etree import _ElementTree
from lxml.etree import parse
import pylint
from pylint.testutils import CheckerTestCase
from stdlib_utils import find_exactly_one_xml_element


class XmlModule:  # pylint: disable=too-few-public-methods
    """Mimic an `astroid` module but for XML."""

    file: str  # needed for `self.current_file`
    tolineno: int  # needed for `pylint.utils.file_state.FileState`
    tree: _ElementTree


class MM4Step:
    """Base class for MM4 Step in a Method."""

    _parameters_node: _Element

    def __init__(self, *, xml_node: _ElementTree, step_index: int, step_type_id: str) -> None:
        self.xml_node = xml_node
        self.step_index = step_index
        self.step_type_id = step_type_id
        self._parameters: dict[str, str] = {}

    def parse(self) -> None:
        self._parameters_node = find_exactly_one_xml_element(self.xml_node, './/Dictionary[@name="Parameters"]')

    @property
    def parameters_node(self) -> _Element:
        try:
            return self._parameters_node
        except AttributeError:
            pass
        self.parse()
        return self._parameters_node

    def get_parameter(self, parameter_name: str) -> str:
        """Get a parameter value from Method Manager XML."""
        try:
            return self._parameters[parameter_name]
        except KeyError:
            pass
        parent_node = find_exactly_one_xml_element(self.parameters_node, f'.//Simple[@value="{parameter_name}"]...')
        value_node = find_exactly_one_xml_element(parent_node, ".//Simple[@type]")
        value = value_node.attrib["value"]
        if not isinstance(value, str):
            raise NotImplementedError(f"The value should always be str, but {value} was type {type(value)}")
        self._parameters[parameter_name] = value
        return value


def parse_steps_from_etree(root: _Element) -> list[MM4Step]:
    """Parse the steps from an Element Tree."""
    parsed_steps: list[MM4Step] = []
    for collection in root.iter("Collection"):
        attributes = collection.attrib
        try:
            collection_type = attributes["name"]
        except KeyError as e:
            raise NotImplementedError(
                f"Collections are always supposed to have a name attribute, but this one only had attributes {attributes}."
            ) from e
        if collection_type != "Steps":
            continue
        steps_node = find_exactly_one_xml_element(collection, "Items")
        for step_idx, step_node in enumerate(steps_node.iter("Complex")):
            step_id_node = find_exactly_one_xml_element(step_node, './/Simple[@name="CommandId"]')
            step_type_id = step_id_node.attrib["value"]
            parsed_steps.append(MM4Step(xml_node=step_node, step_index=step_idx, step_type_id=step_type_id))
        break

    return parsed_steps


def parse_steps(filename: str) -> list[MM4Step]:
    """Parse the steps from an XML file."""
    element_tree = parse(filename)
    root = element_tree.getroot()
    return parse_steps_from_etree(root)


def parse_xml_module_from_file(filepath: str) -> XmlModule:
    line_count = 0
    with open(filepath, encoding="utf-8") as xml_file:
        for _, _ in enumerate(xml_file):
            line_count += 1
    xml = XmlModule()
    xml.tolineno = line_count + 1  # needed for `pylint.utils.file_state.FileState`
    xml.file = filepath  # needed for `self.current_file`
    xml.tree = parse(filepath)
    return xml


def robolint_regex_transformer(value: str) -> re.Pattern[str]:
    """Return `re.compile(value)`."""
    try:
        if "\n" in value:
            return re.compile(value, re.VERBOSE)
        return re.compile(value)
    except re.error as err:
        msg = f"Error in provided regular expression: {value} beginning at index {err.pos}: {err.msg}"
        raise argparse.ArgumentTypeError(msg) from err


def robolint_regexp_validator(
    _: Any, name: str, value: Union[str, re.Pattern[str]]  # pylint: disable=unused-argument
) -> re.Pattern[str]:
    if hasattr(value, "pattern"):
        return value  # type: ignore[return-value]
    if "\n" in value:
        return re.compile(value, re.VERBOSE)
    return re.compile(value)


def robolint_overrides() -> None:
    pylint.config.argument._regex_transformer = robolint_regex_transformer  # pylint: disable=protected-access
    pylint.config.argument._TYPE_TRANSFORMERS["regexp"] = robolint_regex_transformer  # pylint: disable=protected-access
    pylint.config.option._regexp_validator = robolint_regexp_validator  # pylint: disable=protected-access
    pylint.config.option.VALIDATORS["regexp"] = robolint_regex_transformer


class RobolintCheckerTestCase(CheckerTestCase):
    def setup_class(self) -> None:
        robolint_overrides()

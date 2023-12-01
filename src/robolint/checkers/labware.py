"""Checker for lab-ware names."""
import inspect
import re

from lxml.etree import _Element
from overrides import override
from pylint.lint.pylinter import PyLinter
from stdlib_utils import NoMatchingXmlElementError

from .base_checkers import StepChecker
from ..constants import ASPIRATE_VVP96_STEP_ID
from ..constants import DISPENSE_VVP96_STEP_ID
from ..constants import MIX_VVP96_STEP_ID
from ..constants import MOVE_TO_PLATE_GRIPPER_STEP_ID
from ..constants import MOVE_TO_PLATE_STEP_ID
from ..constants import MULTI_DISPENSE_STEP
from ..utils import MM4Step
from ..utils import XmlModule

LABWARE_REGEX: str = inspect.cleandoc(  # Note - attempting to use `\ ` for a literal space seems to not be very robust in the way `pylint` parses verbose regular expressions.  `[ ]` seems more robust.
    r"""
    ^
    (1|2|3|4|6|12|24|48|96|384|1536)                                     # number of partitions
    (                                                                    #
        [ ]                                                              # literal space
        (                                                                #
            [A-Z][A-Za-z]*([\-][A-Z][A-Za-z]*)*                          # capitalized word, potentially hyphenated
            |                                                            # OR
            \d+[ ]*uL                                                    # amount in ul
            |                                                            # OR
            \d+[ ]*mL                                                    # amount in ml
        )                                                                #
    )+                                                                   # one or more of this capture
    [ ]                                                                  # literal space
    (BioRad|Azenta|Agilent|Corning|Greiner|PerkinElmer|Qiagen|Deutz)     # vendor
    [ ]                                                                  # literal space
    (                                                                    #
        [A-Za-z0-9]{4,}                                                  # min. 4 letters and numbers
        |                                                                # OR
        [A-Za-z0-9]+(-[A-Za-z0-9]+)+                                     # catalog numbers seperated by dashes
    )                                                                    # exactly one of this capture
    ([ ](96|384)w\-access)?                                              # modification for access by higher tip density
    $
    """
)


class LabwareNameChecker(StepChecker):
    """Checks `Labware` names."""

    name = "invalid-labware-name"
    msgs = {
        "C9006": (
            "The labware name '%s' does not match best practices. Check that it matches the pattern in the 'labware-rgx' configuration option.",
            name,
            "Used to ensure that Labware naming meets the proscribed pattern.",
        ),
    }
    options = (
        (
            "labware-rgx",
            {
                "default": LABWARE_REGEX,
                "type": "regexp",
                "metavar": "<pattern>",
                "help": "Regular expression for allowed labware names.",
            },
        ),
    )

    step_type_id = {
        ASPIRATE_VVP96_STEP_ID,
        DISPENSE_VVP96_STEP_ID,
        MIX_VVP96_STEP_ID,
        MOVE_TO_PLATE_GRIPPER_STEP_ID,
        MOVE_TO_PLATE_STEP_ID,
        MULTI_DISPENSE_STEP,
    }

    def __init__(self, linter: PyLinter) -> None:
        super().__init__(linter)
        self._found_invalid_labware: dict[str, str] = {}  # `Name: LabwareName`

    @override(check_signature=False)  # this uses `XmlModule` instead of an `astroid` node
    def process_module(self, xml_module: XmlModule) -> None:  # pylint: disable=arguments-renamed
        self._found_invalid_labware.clear()  # ensure no persistence between modules
        props_xpath = (
            "/Complex/Properties/Collection[@name='WorktableResourceMaps']/Items"
            "/Complex/Properties/Collection[@name='ResourceStacks']/Items"
            "/Complex/Properties/Collection[@name='LabwareStackElems']/Items"
            "/Complex/Properties"
        )
        props_elems: list[_Element] = xml_module.tree.xpath(props_xpath)  # type: ignore[assignment]
        for props_elem in props_elems:
            labware = props_elem.xpath("./Simple[@name='LabwareName']")[0].get("value", "")  # type: ignore[index,union-attr]
            name = props_elem.xpath("./Simple[@name='Name']")[0].get("value", "")  # type: ignore[index,union-attr]
            pattern = self.linter.config.labware_rgx
            if not re.match(pattern, labware):
                self._found_invalid_labware[name] = labware

        super().process_module(xml_module)

    @override
    def check_step(self, step: MM4Step) -> None:
        try:
            step.get_parameter("plateVariable")
            return  # if the `labware` is specified by a variable, then this rule does not apply
        except NoMatchingXmlElementError:
            pass
        # there should always be a plate in an aspirate step
        plate = step.get_parameter("plate")

        if plate in self._found_invalid_labware:
            self.add_message(type(self).name, args=(self._found_invalid_labware[plate]))


def register(linter: PyLinter) -> None:
    """Register the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(LabwareNameChecker(linter))

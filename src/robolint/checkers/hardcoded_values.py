"""Checker for hard coded values."""

from overrides import override
from pylint.lint.pylinter import PyLinter
from stdlib_utils import NoMatchingXmlElementError

from .base_checkers import StepChecker
from ..constants import ASPIRATE_VVP96_STEP_ID
from ..constants import DISPENSE_VVP96_STEP_ID
from ..constants import MIX_VVP96_STEP_ID
from ..utils import MM4Step


class HardcodedValuesChecker(StepChecker):
    """Checks aspirate steps for hardcoded values."""

    name = "hardcoded_aspirate_volume"
    msgs = {
        "C9000": (
            "The aspiration volume for channel(s) was harcoded. Replace with a variable. %s",
            "hardcoded-aspirate-volume",
            "Used when a volume during an aspirate step is hardcoded and not bound to a variable.",
        ),
        "C9003": (
            "The dispense volume for channel(s) was harcoded. Replace with a variable. %s",
            "hardcoded-dispense-volume",
            "Used when a volume during a dispense step is hardcoded and not bound to a variable.",
        ),
        "C9005": (
            "The mix volume for channel(s) was harcoded. Replace with a variable. %s",
            "hardcoded-mix-volume",
            "Used when a volume during a mix step is hardcoded and not bound to a variable.",
        ),
    }
    options = ()

    step_type_id = {ASPIRATE_VVP96_STEP_ID, DISPENSE_VVP96_STEP_ID, MIX_VVP96_STEP_ID}

    @override
    def check_step(self, step: MM4Step) -> None:
        """Check if step has hardcoded volumes.

        As of MM4 v1.4.8425, it seems like if a variable is bound, then the standard `.volume` field is removed sometimes...but not all the time. Also
        if a well is disabled, it is removed from the XML.
        """
        bad_wells: list[str] = []
        for col_idx in range(12):
            for row_idx in range(8):
                well_name = f"{chr(65+row_idx)}{str(col_idx+1).zfill(2)}"
                try:
                    step.get_parameter(f"{well_name}.volume")
                except NoMatchingXmlElementError:
                    continue

                try:
                    step.get_parameter(f"{well_name}.volumeVariable")
                    continue
                except NoMatchingXmlElementError:
                    pass

                hardcoded_volume = step.get_parameter(f"{well_name}.volume")
                bad_wells.append(f"{well_name}: {hardcoded_volume} uL")
        if len(bad_wells) == 0:
            return
        message_name = "hardcoded-aspirate-volume"
        if step.step_type_id == DISPENSE_VVP96_STEP_ID:
            message_name = "hardcoded-dispense-volume"
        elif step.step_type_id == MIX_VVP96_STEP_ID:
            message_name = "hardcoded-mix-volume"
        self.add_message(message_name, args=(", ".join(bad_wells),))


def register(linter: PyLinter) -> None:
    """Register the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(HardcodedValuesChecker(linter))

import os
from unittest.mock import ANY

from pylint.testutils import MessageTest
from pylint.testutils import set_config
from robolint.checkers.labware import LabwareNameChecker
from robolint.utils import parse_xml_module_from_file
from robolint.utils import RobolintCheckerTestCase
from stdlib_utils import get_current_file_abs_directory


PATH_TO_CURRENT_FILE = get_current_file_abs_directory()
PATH_TO_XMLS = os.path.join(PATH_TO_CURRENT_FILE, "..", "xml")


class TestLabwareNameCheckerCheckerSingleSteps(RobolintCheckerTestCase):
    CHECKER_CLASS = LabwareNameChecker

    def test_when_no_labware_definitions_then_no_errors(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "no-labware-definitions.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    @set_config(labware_rgx="non-matching-pattern")  # type:ignore[misc]  # `untyped decorator`
    def test_When_names_does_not_match_pattern__Then_error(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "single-aspirate-step-with-invalid-labware-name.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertAddsMessages(
            MessageTest(
                LabwareNameChecker.name,
                args=("384 PCR BioRad"),
                line=0,
            )
        ):
            self.checker.process_module(tree)

    def test_When_names_pattern__Then_no_error(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "single-aspirate-step-with-valid-labware-name.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    def test_Given_module_processed_with_bad_labware__When_module_processed_with_good_labware_with_same_plate_name__Then_no_error(
        self,
    ) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "single-aspirate-step-with-invalid-labware-name.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertAddsMessages(
            MessageTest(
                LabwareNameChecker.name,
                args=("384 PCR BioRad"),
                line=0,
            )
        ):
            self.checker.process_module(tree)

        filepath = os.path.join(
            PATH_TO_XMLS,
            "labware-names",
            "single-aspirate-step-with-valid-labware-but-same-platename-as-invalid-file.xml",
        )
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    def test_With_two_aspirate_steps_and_invalid_labware__Then_two_messages(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "two-aspirate-steps-with-labware-names.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertAddsMessages(
            MessageTest(
                LabwareNameChecker.name,
                args=("96 Alpaqua Magnet"),
                line=ANY,
            ),
            MessageTest(
                LabwareNameChecker.name,
                args=("96 Alpaqua Magnet"),
                line=ANY,
            ),
        ):
            self.checker.process_module(tree)

    def test_With_no_plate_specified_it_works(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "single-aspirate-step-no-plate-specified.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    def test_with_dispense_step_it_works(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "dispense-step-with-labware-name.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    def test_with_mix_step_it_works(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "mix-step-with-labware-name.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    def test_with_move_to_plate_gripper_step_it_works(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "move-to-plate-gripper-step-with-labware-name.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    def test_with_move_to_plate_step_it_works(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "move-to-plate-step-with-labware-name.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    def test_with_multi_dispense_step_it_works(self) -> None:
        filepath = os.path.join(PATH_TO_XMLS, "labware-names", "multi-dispense-step-with-labware-name.xml")
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

    def test_When_move_to_plate_step_uses_variable_for_plate__Then_no_error(self) -> None:
        filepath = os.path.join(
            PATH_TO_XMLS, "labware-names", "submethod-inheriting-worktable-with-move-to-plate-and-load-tips.xml"
        )
        tree = parse_xml_module_from_file(filepath)
        with self.assertNoMessages():
            self.checker.process_module(tree)

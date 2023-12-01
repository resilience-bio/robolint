import os
from typing import Callable
from unittest.mock import patch

import humps
from mock import MagicMock
from pylint.testutils import MessageTest
import pytest
from robolint.checkers.robocase import RobocaseVariableNameChecker
from robolint.checkers.variables import VariableNameChecker
from robolint.test_utils import RobolintCheckerTestCase

from ..fixtures import get_parsed_steps
from ..fixtures import get_parsed_xml_module


class TestVariableCaseInitialized(RobolintCheckerTestCase):
    CHECKER_CLASS = VariableNameChecker
    XML_SUBPATH = "variable-names"

    @pytest.mark.parametrize(
        "variable_name_case, example_filename, check_function, case_function",
        [
            ("pascal", "variable-name-in-pascal-case", humps.is_pascalcase, humps.pascalize),
            ("camel", "variable-name-in-camel-case", humps.is_camelcase, humps.camelize),
            ("kebab", "variable-name-in-kebab-case", humps.is_kebabcase, humps.kebabize),
            ("snake", "variable-name-in-snake-case", humps.is_snakecase, humps.decamelize),
        ],
    )
    def test_When_variable_name_case_config_option_set__Then_case_functions_correct(
        self,
        variable_name_case: str,
        example_filename: str,
        check_function: Callable[[str], bool],
        case_function: Callable[[str], str],
    ) -> None:
        self.checker.linter.set_option("variable-name-case", variable_name_case)
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, example_filename))
        with self.assertNoMessages():
            self.checker.visit_step(steps[1])
            assert self.checker.case_check_function is check_function
            assert self.checker.case_function is case_function

    def test_When_invalid_variable_name_case_config_option_set__Then_ValueError(self) -> None:
        self.checker.linter.set_option("variable-name-case", "dummy")
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "variable-name-in-pascal-case"))
        with pytest.raises(ValueError) as err:
            self.checker.visit_step(steps[1])
            assert "Invalid variable name case" in str(err.value)


class TestVariableNamingInSteps(RobolintCheckerTestCase):
    CHECKER_CLASS = RobocaseVariableNameChecker
    XML_SUBPATH = "variable-names"

    def test_When_variable_in_pascal_case_and_no_suffix__Then_no_messages(self) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "variable-name-in-pascal-case"))
        with self.assertNoMessages():
            self.checker.process_module(xml_module)

    def test_When_variable_in_kebab_case_Then_message(self) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "variable-name-in-kebab-case"))
        with self.assertAddsMessages(
            MessageTest("invalid-variable-case", args=("loop-counter", "LoopCounter"), line=1),
            MessageTest("invalid-variable-case", args=("loop-counter", "LoopCounter"), line=2),
        ):
            self.checker.process_module(xml_module)

    def test_When_variable_contains_abbreviation_then_message(self) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        self.checker.linter.set_option("variable-name-abbreviations", "Cycles,Cyc")
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "variable-name-contains-abbreviation"))
        with self.assertAddsMessages(
            MessageTest("non-abbreviated-variable", args=("NumCycles", "Cycles", "Cyc"), line=1),
            MessageTest("non-abbreviated-variable", args=("NumCycles", "Cycles", "Cyc"), line=2),
        ):
            self.checker.process_module(xml_module)

    def test_When_abbreviation_csv_is_missing_an_item__Then_value_error(self) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        self.checker.linter.set_option("variable-name-abbreviations", "Cycles,")
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "variable-name-contains-abbreviation"))
        with pytest.raises(ValueError):
            self.checker.process_module(xml_module)

    def test_When_variable_contains_single_digit_suffix_then_message(self) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "variable-name-contains-single-digit-suffix"))
        with self.assertAddsMessages(
            MessageTest("invalid-variable-case", args=("LoopCounter1", "LoopCounter_01"), line=1),
            MessageTest("invalid-variable-case", args=("LoopCounter1", "LoopCounter_01"), line=2),
        ):
            self.checker.process_module(xml_module)

    @patch("robolint.RobocaseVariableNameChecker._run_checks")
    def test_When_VariableValueVariable_and_ValueVariable_present_in_begin_loop_step_Then_checker_called_twice(
        self, mocked_func: MagicMock
    ) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-with-variable-name-variable-and-value-variable"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[0])
            assert set(["LoopCounter"]) == self.checker.variables_observed
            assert mocked_func.call_count == 2

    @patch("robolint.RobocaseVariableNameChecker._run_checks")
    def test_When_AssignToVariable_present_in_expression_step_Then_checker_called_once(
        self, mocked_func: MagicMock
    ) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-with-variable-name-variable-and-value-variable"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[1])
            assert set(["LoopCounter"]) == self.checker.variables_observed
            assert mocked_func.call_count == 1

    @patch("robolint.RobocaseVariableNameChecker._run_checks")
    def test_When_VariableName_and_ValueVariable_present_in_end_loop_step_Then_checker_called_twice(
        self, mocked_func: MagicMock
    ) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "loop-with-variable-name-variable-and-value-variable"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[2])
            assert set(["LoopCounter"]) == self.checker.variables_observed
            assert mocked_func.call_count == 2


class TestAspirateStepVariableForPlateAndVolume(RobolintCheckerTestCase):
    CHECKER_CLASS = RobocaseVariableNameChecker
    XML_SUBPATH = "variable-names"

    @patch("robolint.RobocaseVariableNameChecker._run_checks")
    def test_When_aspirate_step_contains_plateVariable_and_volumeVariable_Then_nodes_are_visited_And_expected_names_found(
        self, mocked_func: MagicMock
    ) -> None:
        self.checker.linter.set_option("variable-name-case", "robocase")
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "aspirate-step-variable-for-plate-and-volume"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[-1])
            # 1 use of plateVariable containing 'SrcPlate', 96 uses of volumeVariable containing 'Volume'
            assert mocked_func.call_count == 97
            assert set(["SrcPlate", "Volume"]) == self.checker.variables_observed

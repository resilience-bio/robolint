import os
import re
from unittest.mock import ANY

from pylint.testutils import MessageTest
from pylint.testutils import set_config
import pytest
from robolint import TipEjectChecker
from robolint import TipLoadChecker
from robolint.test_utils import RobolintCheckerTestCase

from ..fixtures import get_parsed_steps
from ..fixtures import get_parsed_xml_module


class TestPylintRegexpCsvExpectations(RobolintCheckerTestCase):
    """Testing of `Pylint` expectations.

    `"type": "regexp_csv"` splits on commas but does not respect `CSV` parsing rules.
    As such, it doesn't appear to support commas within expressions.
    In code though, it supports `str  | list[Pattern[str]]`.
    """

    CHECKER_CLASS = TipLoadChecker

    def test_When_tip_load_motion_profile_config_is_invalid_regex__Then_raises_system_exit(self) -> None:
        with pytest.raises(SystemExit):
            self.linter.set_option("tip-load-profile", "\\")

    @pytest.mark.xfail(raises=SystemExit, reason="Pylint regexp_csv option is not CSV compliant.")
    def test_When_config_option_regexp_csv_has_escaped_comma__Then_pylint_can_process_it(self) -> None:
        self.linter.set_option("tip-load-profile", "a pattern containing \\,comma")

    def test_regexp_csv_config_option_supports_list_of_pattern_objects(self) -> None:
        self.linter.set_option("tip-load-profile", [re.compile(r"apattern")])
        option = self.linter.config.tip_load_profile
        assert isinstance(option, list)
        assert len(option) == 1
        assert isinstance(option[0], re.Pattern)

    def test_When_tip_load_motion_profile_config_has_multiple_patterns__Then_we_get_a_list_of_patterns(self) -> None:
        self.linter.set_option("tip-load-profile", r"first,second")
        option = self.linter.config.tip_load_profile
        assert isinstance(option, list)
        assert len(option) == 2
        assert isinstance(option[0], re.Pattern)


class TestTipLoadMotionProfileSingleSteps(RobolintCheckerTestCase):

    CHECKER_CLASS = TipLoadChecker
    XML_SUBPATH = "tip_motion_profile"

    @set_config(tip_load_profile="Tip Load.*")  # type:ignore[misc] # `untyped decorator`
    def test_Given_tip_load_motion_profile_is_mid_speed__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "load-tips-with-invalid-mid-speed-profile.xml"))
        with self.assertAddsMessages(
            MessageTest(
                "invalid-tip-load-profile",
                args=("Mid Speed", "Tip Load.*"),
                line=ANY,
            )
        ):
            self.checker.visit_step(steps[0])

    @set_config(tip_load_profile="Tip Load.*")  # type:ignore[misc] # `untyped decorator`
    def test_When_tip_load_motion_profile_is_already_correct__Then_no_message(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "load-tips-with-valid-tip-load-profile.xml"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[0])

    @set_config(tip_load_profile="")  # type:ignore[misc] # `untyped decorator`
    def test_When_tip_load_motion_profile_config_is_empty__Then_no_message(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "load-tips-with-invalid-mid-speed-profile.xml"))
        with self.assertNoMessages():
            self.checker.visit_step(steps[0])


class TestTipEjectMotionProfileSingleSteps(RobolintCheckerTestCase):

    CHECKER_CLASS = TipEjectChecker
    XML_SUBPATH = "tip_motion_profile"

    @set_config(tip_eject_profile="Tip Eject.*")  # type:ignore[misc] # `untyped decorator`
    def test_Given_tip_eject_motion_profile_is_fast_speed__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "eject-tips-with-invalid-fast-speed-profile.xml"))
        with self.assertAddsMessages(
            MessageTest(
                "invalid-tip-eject-profile",
                args=("Fast Speed", "Tip Eject.*"),
                line=ANY,
            )
        ):
            self.checker.visit_step(steps[0])


class TestTipEjectMotionProfileCheckerWholeModule(RobolintCheckerTestCase):

    CHECKER_CLASS = TipEjectChecker
    XML_SUBPATH = "tip_motion_profile"

    @set_config(tip_eject_profile="Tip Eject.*")  # type:ignore[misc] # `untyped decorator`
    def test_Given_tip_eject_motion_profile_must_match_tip_eject__When_profile_is_fast_speed__Then_error(self) -> None:
        xml_module = get_parsed_xml_module(
            os.path.join(self.XML_SUBPATH, "eject-tips-with-invalid-fast-speed-profile.xml")
        )
        with self.assertAddsMessages(
            MessageTest(
                "invalid-tip-eject-profile",
                args=("Fast Speed", "Tip Eject.*"),
                line=ANY,
            )
        ):
            self.checker.process_module(xml_module)


class TestTipLoadMotionProfileCheckerWholeModule(RobolintCheckerTestCase):

    CHECKER_CLASS = TipLoadChecker
    XML_SUBPATH = "tip_motion_profile"

    @set_config(tip_load_profile="Tip Load.*")  # type:ignore[misc] # `untyped decorator`
    def test_Given_tip_load_motion_profile_must_match_tip_load__When_profile_is_fast_speed__Then_error(self) -> None:
        xml_module = get_parsed_xml_module(
            os.path.join(self.XML_SUBPATH, "load-tips-with-invalid-mid-speed-profile.xml")
        )
        with self.assertAddsMessages(
            MessageTest(
                "invalid-tip-load-profile",
                args=("Mid Speed", "Tip Load.*"),
                line=ANY,
            )
        ):
            self.checker.process_module(xml_module)

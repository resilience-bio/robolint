import os
from unittest.mock import ANY

from pylint.testutils import MessageTest
from pylint.testutils import set_config
from robolint import TipWasteEjectHeightChecker
from robolint.test_utils import RobolintCheckerTestCase

from ..fixtures import get_parsed_steps
from ..fixtures import get_parsed_xml_module


class TestTipHeightSingleSteps(RobolintCheckerTestCase):

    CHECKER_CLASS = TipWasteEjectHeightChecker
    XML_SUBPATH = "tip_height"

    def test_Given_tip_height_is_15_and_default_is_50__Then_error(self) -> None:
        steps = get_parsed_steps(os.path.join(self.XML_SUBPATH, "tip-height-of-15.xml"))
        with self.assertAddsMessages(
            MessageTest(
                "invalid-tip-waste-eject-height",
                args=(15, 50),
                line=ANY,
            )
        ):
            self.checker.visit_step(steps[0])


class TestTipHeightWholeModule(RobolintCheckerTestCase):

    CHECKER_CLASS = TipWasteEjectHeightChecker
    XML_SUBPATH = "tip_height"

    @set_config(tip_waste_eject_height=15)  # type:ignore[misc] # `untyped decorator`
    def test_Given_tip_height_is_15_and_locally_set_config_value_is_15__Then_pass(self) -> None:
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "tip-height-of-15.xml"))
        with self.assertNoMessages():
            self.checker.process_module(xml_module)

    @set_config(tip_waste_chute_name="")  # type:ignore[misc] # `untyped decorator`
    def test_Given_no_tip_waste_chute_name_specified_then_check_is_not_performed(self) -> None:
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "tip-height-of-15.xml"))
        with self.assertNoMessages():
            self.checker.process_module(xml_module)

    @set_config(tip_waste_chute_name="dummy.*")  # type:ignore[misc] # `untyped decorator`
    def test_Given_tip_waste_chute_name_will_not_match_then_check_is_not_performed(self) -> None:
        xml_module = get_parsed_xml_module(os.path.join(self.XML_SUBPATH, "tip-height-of-15.xml"))
        with self.assertNoMessages():
            self.checker.process_module(xml_module)

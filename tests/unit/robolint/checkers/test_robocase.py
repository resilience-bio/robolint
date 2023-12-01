import pytest
from robolint.checkers.robocase import is_robocase
from robolint.checkers.robocase import to_robocase


TEST_ITEMS = [
    ("PascalCaseUnderscoreNumberSuffix_01", True, "PascalCaseUnderscoreNumberSuffix_01"),
    ("PascalCaseUnderscoreNumberSuffixSingleDigit_1", False, "PascalCaseUnderscoreNumberSuffixSingleDigit_01"),
    ("PascalCaseNoSuffix", True, "PascalCaseNoSuffix"),
    ("PascalCaseNoUnderscoreSuffix01", False, "PascalCaseNoUnderscoreSuffix_01"),
    ("camelCaseUnderscoreNumberSuffix_01", False, "CamelCaseUnderscoreNumberSuffix_01"),
    ("camelCaseDashSuffix-01", False, "CamelCaseDashSuffix_01"),
    ("snake_case_no_underscore_suffix01", False, "SnakeCaseNoUnderscoreSuffix_01"),
    ("kebab-case-no-suffix", False, "KebabCaseNoSuffix"),
]


@pytest.mark.parametrize("text,result,_", TEST_ITEMS)
def test_is_robocase(text: str, result: bool, _: str) -> None:
    assert is_robocase(text) is result


@pytest.mark.parametrize("text,_,result", TEST_ITEMS)
def test_to_robocase(text: str, _: bool, result: str) -> None:
    assert to_robocase(text) == result

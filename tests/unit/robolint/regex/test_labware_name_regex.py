import re

import pytest
from pytest import param
from robolint.checkers.labware import LABWARE_REGEX

LABWARE_PATTERN = re.compile(LABWARE_REGEX, re.VERBOSE)


@pytest.mark.parametrize(
    "labware_name",
    [
        param("384 PCR BioRad HSP38xx", id="catalog number with uppercase, numeric, and lowercase"),
        param("1 Well Reservoir Agilent 204017-100"),
        param("12 Col Reservoir Agilent 204095-100"),
        param("384 F-Bottom ProxiPlate PerkinElmer 6008280", id="all numeric catalog number"),
        param("384 F-Bottom MTP Corning 3985", id="hyphenated description"),
        param("24 F-Bottom MTP Deutz CR1424dg", id="catalog number ending in lowercase"),
        param("96 500 uL Tubes Azenta 68-0703-11", id="uL volume in description"),
        param("96 500uL Tubes Azenta 68-0703-11", id="uL volume adjacent to number without space"),
        param("96 1 mL Tubes Azenta 68-0703-11", id="mL volume in description"),
        param("96 Nanoplate QIAcuity Qiagen 250021", id="multiple capital letters in plate name"),
        param("24 F-Bottom MTP Deutz CR1424dg 96w-access", id="96-well access modified labware definition"),
        param("24 F-Bottom MTP Deutz CR1424dg 384w-access", id="384-well access modified labware definition"),
    ],
)
def test_When_labware_is_valid__Then_regex_match(labware_name: str) -> None:
    assert re.fullmatch(LABWARE_PATTERN, labware_name) is not None


@pytest.mark.parametrize(
    "labware_name",
    [
        param("384 F-bottom MTP Corning 3985", id="non-capitalized bottom for F-bottom"),
        param("96 500 ul Tubes Azenta 68-0703-11", id="lowercase microliters"),
        param("96 1 ml Tubes Azenta 68-0703-11", id="lowercase milliliters"),
        param("24 F-Bottom MTP Deutz CR1424dg 96w access", id="96-well access without required hyphen"),
        param("24 F-Bottom MTP Deutz CR1424dg 96w-Access", id="96-well access capitalized A"),
        param("24 F-Bottom MTP Deutz CR1424dg 96W-access", id="96-well access capitalized W"),
    ],
)
def test_When_labware_invalid__Then_no_regex_match(labware_name: str) -> None:
    assert re.fullmatch(LABWARE_PATTERN, labware_name) is None

import os

from robolint import MM4Step
from robolint import parse_steps_from_etree
from robolint import parse_xml_module_from_file
from robolint import XmlModule
from stdlib_utils import get_current_file_abs_directory

PATH_TO_CURRENT_FILE = get_current_file_abs_directory()
PATH_TO_XMLS = os.path.join(PATH_TO_CURRENT_FILE, "xml")

PARSED_STEPS: dict[str, list[MM4Step]] = {}

PARSED_XML_MODULES: dict[str, XmlModule] = {}


def get_parsed_xml_module(filepath_within_xml_dir: str) -> XmlModule:
    if not filepath_within_xml_dir.endswith(".xml"):
        filepath_within_xml_dir += ".xml"
    try:
        return PARSED_XML_MODULES[filepath_within_xml_dir]
    except KeyError:
        pass
    parsed_xml_module = parse_xml_module_from_file(os.path.join(PATH_TO_XMLS, filepath_within_xml_dir))
    PARSED_XML_MODULES[filepath_within_xml_dir] = parsed_xml_module
    return parsed_xml_module


def get_parsed_steps(filepath_within_xml_dir: str) -> list[MM4Step]:
    if not filepath_within_xml_dir.endswith(".xml"):
        filepath_within_xml_dir += ".xml"
    try:
        return PARSED_STEPS[filepath_within_xml_dir]
    except KeyError:
        pass
    xml_module = get_parsed_xml_module(filepath_within_xml_dir)

    parsed_steps = parse_steps_from_etree(xml_module.tree.getroot())
    PARSED_STEPS[filepath_within_xml_dir] = parsed_steps
    return parsed_steps

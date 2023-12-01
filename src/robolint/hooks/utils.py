"""Utility functions used for the hooks."""

import argparse
import logging
import os
import subprocess
import sys
from typing import Iterable
from typing import Optional
from typing import Sequence
from xml.etree import ElementTree

from stdlib_utils import configure_logging

logger = logging.getLogger("hook-utils")
configure_logging()


def write_xml_to_file(*, root: ElementTree.Element, filename: str) -> None:
    xml_str = ElementTree.tostring(root, encoding="UTF-8").decode("utf-8")
    xml_str = f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'
    with open(filename, "w", encoding="utf-8") as handle:
        handle.write(xml_str)


def get_files_to_process(argv: Optional[Sequence[str]] = None) -> Iterable[str]:
    """Get the files that `pre-commit` passed in."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )
    args = parser.parse_args(argv)
    filenames = args.filenames
    if not isinstance(filenames, Iterable):
        raise NotImplementedError(f"filenames was type {type(filenames)}")
    return filenames


def run_mypy() -> None:
    if "PYTHONPATH" not in os.environ:
        print("PYTHONPATH must be set")  # allow-print
        sys.exit(-1)
    parts = os.environ["PYTHONPATH"].split(os.pathsep)
    parts = ["mypy"] + parts
    response = subprocess.run(parts, check=False, capture_output=False)
    sys.exit(response.returncode)

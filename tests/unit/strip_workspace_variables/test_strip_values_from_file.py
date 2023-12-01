import hashlib
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from robolint.hooks.strip_workspace_config_values import strip_values_from_file
from stdlib_utils import get_current_file_abs_directory

PATH_TO_CURRENT_FILE = get_current_file_abs_directory()
PATH_TO_CONFIGS = os.path.join(PATH_TO_CURRENT_FILE, "workspace_variables_configs")


def test_When_file_is_clean__Then_returns_falsey() -> None:
    actual = strip_values_from_file(os.path.join(PATH_TO_CONFIGS, "clean.xml"))
    assert not actual


def test_When_first_variable_has_value__Then_new_file_is_clean() -> None:
    original_file_path = os.path.join(PATH_TO_CONFIGS, "first_value_present.xml")
    with TemporaryDirectory() as temp_dir:
        new_file_path = os.path.join(temp_dir, "blah.xml")
        shutil.copy(original_file_path, new_file_path)
        initial_result = strip_values_from_file(new_file_path)
        assert len(initial_result) == 1

        actual = strip_values_from_file(new_file_path)
        assert not actual


def test_When_first_variable_has_value_spanning_lines__Then_new_file_is_clean() -> None:
    original_file_path = os.path.join(PATH_TO_CONFIGS, "first_value_spans_lines.xml")
    with TemporaryDirectory() as temp_dir:
        new_file_path = os.path.join(temp_dir, "blah.xml")
        shutil.copy(original_file_path, new_file_path)
        initial_result = strip_values_from_file(new_file_path)
        assert len(initial_result) == 1

        actual = strip_values_from_file(new_file_path)
        assert not actual


def test_When_strip_values_encounters_a_variable_to_ignore__Then_the_file_stays_the_same() -> None:
    original_file_path = os.path.join(PATH_TO_CONFIGS, "preserve.xml")
    with TemporaryDirectory() as temp_dir:
        new_file_path = os.path.join(temp_dir, "blah.xml")
        shutil.copy(original_file_path, new_file_path)
        result = strip_values_from_file(new_file_path, {"MethodManagerVersion"})
        assert len(result) == 0
        assert (
            hashlib.md5(Path(original_file_path).read_text(encoding="UTF-8").encode()).hexdigest()
            == hashlib.md5(Path(new_file_path).read_text(encoding="UTF-8").encode()).hexdigest()
        )

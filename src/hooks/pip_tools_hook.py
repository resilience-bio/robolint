"""pip-tools hook to keep requirements up to date."""
import argparse
import hashlib
import os
import subprocess
from typing import Iterable
from typing import Optional
from typing import Sequence


def calculate_md5_sum(filename: str) -> str:
    """Calculate the md5 sum of the parts of the file that we care about."""
    with open(filename, "rb") as file_to_check:

        lines = file_to_check.readlines()
        file_except_paths: list[str] = []
        for line_idx, line in enumerate(lines):
            if line_idx < 6:
                continue  # Skip the header that includes the output file path, as this interferes with unit testing, and all we really care about are the actual dependencies anyway.
            line_str = line.decode("utf-8")
            if "# via" in line_str:
                continue  # skip these lines since they also can contain a file path
            file_except_paths.append(line_str)

        file_to_hash = "".join(file_except_paths)
        return hashlib.md5(file_to_hash.encode(encoding="utf-8")).hexdigest()


def execute_command(command_args: Iterable[str]) -> tuple[str, str, int]:
    """Execute a command using `Popen`.

    Having this as a separate function makes it easier to mock.

    Args:
        command: what to execute

    Returns:
        `stdout`, `stderr`, `exit_code`
    """
    with subprocess.Popen(  # `subprocess.run` ran into a lot of issues getting it to work cross-platform with the double quotes that are needed around the `pip-args` for `pip-tools`, so using `Popen` instead
        " ".join(command_args), universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as proc:
        stdout, stderr = proc.communicate()
        return_code = proc.returncode
    return stdout, stderr, return_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the correct pip-tools command.

    `argv`: command_type [ `requirements.txt` file path] [ `requirements.in` file path]
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        help="Filenames pre-commit believes are changed.",
        nargs="*",
    )
    args = parser.parse_args(argv)
    argv = args.filenames
    if not isinstance(argv, Sequence):
        raise NotImplementedError(f"argv should always be sequence, but {argv} was type {type(argv)}")
    suffix = "Windows" if os.name == "nt" else "Linux"

    always_exit_zero = False
    if argv[0] == "exit-zero":
        always_exit_zero = True
        argv = argv[1:]
    run_type = argv[0]
    requirements_txt_file = f"requirements-dev-{suffix}.txt"
    if len(argv) > 1:
        requirements_txt_file = argv[1]  # to help with unit testing
    pip_args = ["--disable-pip-version-check"]
    subprocess_args = ["pip-sync", requirements_txt_file]
    if run_type == "compile":
        requirements_in_file = "requirements-dev.in"
        if len(argv) > 2:
            requirements_in_file = argv[2]
        subprocess_args = [
            "pip-compile",
            "--generate-hashes",
            "--resolver=backtracking",
            "--output-file",
            requirements_txt_file,
            requirements_in_file,
        ]
        original_md5_sum = None  # ensure there's an md5 mismatch if no file existed initially
        if os.path.isfile(requirements_txt_file):
            original_md5_sum = calculate_md5_sum(requirements_txt_file)
    # add `pip` arguments to make use of code artifact
    subprocess_args.extend(("--pip-args", r'"' + " ".join(pip_args) + r'"'))
    stdout, stderr, return_code = execute_command(subprocess_args)

    if return_code != 0:
        print(f"Exiting with error {return_code}")  # allow-print
        print(f"The command executed was: {subprocess_args}")  # allow-print
        print(f"Stdout: {stdout}")  # allow-print
        print(f"Stderr: {stderr}")  # allow-print
        if always_exit_zero:
            return 0
        if return_code == 1:
            return_code = 21  # 1 means something special in `pre-commit` (files were modified but no error), so set to arbitrary error code
        return return_code

    if "Everything" not in stdout:
        if run_type == "sync-on-commit":
            print(stdout)  # allow-print
            print("Dependencies were updated. Attempt to commit again.")  # allow-print
            return 1

    if run_type == "compile":
        new_md5_sum = calculate_md5_sum(requirements_txt_file)
        if new_md5_sum != original_md5_sum:
            print(stdout)  # allow-print
            print(stderr)  # allow-print
            print("New dependency versions were compiled. Attempt to commit again.")  # allow-print
            if always_exit_zero:
                return 0
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

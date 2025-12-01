import subprocess
import re
import os
from pathlib import Path
from soulbrainarr.config_parser import get_config, CONFIG_DATA

FAILED_PATTERNS = [
    "Skipping",
    "No match found",
    r"\[F\]",
    r"\[D\]",
]

PATH_REGEX = re.compile(r"(/[^:\n]+)")


def run_beet_cmd(
    args: list[str],
) -> tuple[str, str]:
    """
    Runs a beet command in non-interactive mode (-q -y).
    Explicitly uses the provided config.yaml and library.db paths.
    Returns (stdout, stderr).
    """
    config: CONFIG_DATA = get_config()
    cmd = [
        "beet",
        "-c", config.BEETS.BEETS_CONFIG,
        "-l", config.BEETS.BEETS_DATABASE,
    ] + args + ["-q", "-y"]

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    out, err = proc.communicate()
    return out, err


def bulk_import(folder: str) -> str:
    """
    Runs a bulk beets import on the given folder.
    Returns the combined beets output (stdout + stderr).
    """
    out, err = run_beet_cmd(["import", folder])
    return out + "\n" + err


def parse_failed_items(output: str) -> list[str]:
    """
    Parses beets import output and returns file paths
    that were skipped or failed to import.
    """
    failed = []

    for line in output.splitlines():
        if any(pat in line for pat in FAILED_PATTERNS):
            m = PATH_REGEX.search(line)
            if m:
                failed.append(m.group(1))

    return failed


def singleton_import(path: str) -> tuple[str, str]:
    """
    Performs a singleton import on a single file.
    Returns (stdout, stderr).
    """
    return run_beet_cmd(["import", "-s", path])


def run_import(folder: str) -> dict:
    """
    High-level import helper:

        1. Runs bulk import.
        2. Identifies failures.
        3. Retries each failed file as a singleton.

    Returns a dict summary for your larger app.
    """
    folder = str(Path(folder))
    result = {
        "folder": folder,
        "bulk_output": "",
        "bulk_failed": [],
        "singleton_results": {},
    }

    # 1. Bulk import
    output = bulk_import(folder)
    result["bulk_output"] = output

    # 2. Detect failed/skipped items
    failed = parse_failed_items(output)
    result["bulk_failed"] = failed

    # 3. Retry failed items individually
    for f in failed:
        if os.path.exists(f):
            out, err = singleton_import(f)
            result["singleton_results"][f] = {
                "stdout": out,
                "stderr": err,
            }
        else:
            result["singleton_results"][f] = {
                "stdout": "",
                "stderr": "File not found",
            }

    return result


def delete_duplicates() -> tuple[str, str]:
    """
    Deletes duplicate tracks using:
        beet duplicates -d
    Returns (stdout, stderr).
    """
    # -d = delete duplicates
    return run_beet_cmd(["duplicates", "-d"])


def run_deduplicate() -> dict:
    """
    Runs duplicate detection + deletion via beets.
    Returns a dict containing the output for logging or UI display.
    """
    out, err = delete_duplicates()
    return {
        "stdout": out,
        "stderr": err,
        "combined_output": out + "\n" + err,
    }

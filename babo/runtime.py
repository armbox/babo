"""
Babo Runtime — Module system for .babo programs.

This module is automatically copied into each .baboc cache directory during
build. Generated code can import it to call other .babo files as modules.
Works correctly across different virtual environments.

Usage in generated code:
    from runtime import call_babo

    result = call_babo("other.babo", "arg1", "arg2")
    print(result)  # stdout from other.babo
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

# Path to the Python executable that has babo installed.
# Written by the build step into a file alongside this module.
_BABO_PYTHON_FILE = Path(__file__).parent / ".babo_python"


def _get_babo_python() -> str:
    """Return path to a Python that has babo installed.

    Priority:
      1. The Python that built this cache (from .babo_python file)
      2. The current Python (might work if babo is installed)
      3. 'python3' from PATH
    """
    if _BABO_PYTHON_FILE.is_file():
        try:
            candidate = _BABO_PYTHON_FILE.read_text().strip()
            if os.path.isfile(candidate):
                return candidate
        except Exception:
            pass

    # Fallback: try current python
    try:
        subprocess.run(
            [sys.executable, "-c", "import babo"],
            capture_output=True, text=True, timeout=5
        )
        return sys.executable
    except Exception:
        pass

    # Fallback: try python3 from PATH
    for python in ["python3", "python"]:
        if shutil.which(python):
            return python

    raise RuntimeError(
        "Cannot find a Python with babo-lang installed. "
        "Ensure babo-lang is installed: pip install babo-lang"
    )


def call_babo(babo_file: str, *args: str) -> str:
    """Call another .babo file as a module.

    Passes *args to the target .babo program and returns its stdout
    as a string. Builds the target automatically if needed.

    The .babo file path is resolved:
      1. Relative to the directory containing this runtime module
      2. Relative to CWD

    Raises RuntimeError if the call fails.
    """
    resolved = _resolve(babo_file)
    python_exe = _get_babo_python()

    result = subprocess.run(
        [python_exe, "-m", "babo", resolved] + list(args),
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        err = result.stderr.strip()
        raise RuntimeError(
            f"call_babo('{babo_file}') failed (exit {result.returncode}): {err}"
        )

    return result.stdout.strip()


def _resolve(babo_file: str) -> str:
    """Resolve a .babo file reference to an absolute path."""
    p = Path(babo_file)

    if p.is_absolute() and p.exists():
        return str(p)

    # Try relative to the directory containing this runtime module
    runtime_dir = Path(__file__).parent
    candidate = (runtime_dir / p).resolve()
    if candidate.exists():
        return str(candidate)

    # Try CWD
    candidate = (Path.cwd() / p).resolve()
    if candidate.exists():
        return str(candidate)

    # Try relative to the original .babo source file (from metadata)
    meta_file = runtime_dir / "metadata.json"
    if meta_file.is_file():
        try:
            import json
            meta = json.loads(meta_file.read_text())
            source = Path(meta.get("source", ""))
            candidate = (source.parent / p).resolve()
            if candidate.exists():
                return str(candidate)
        except Exception:
            pass

    raise FileNotFoundError(
        f"call_babo: cannot find '{babo_file}'. "
        f"Looked in: {runtime_dir}, {Path.cwd()}"
    )

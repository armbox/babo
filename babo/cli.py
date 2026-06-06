#!/usr/bin/env python3
"""
Babo — The universal language even a fool can use.

Write a description in a .babo file, and Babo calls Claude Code to generate
a runnable implementation, caches it in the .babo/ directory, and executes it.

Usage:
    babo <file.babo> [args...]     Run a .babo file (auto-build if needed)
    babo run <file.babo> [args...] Explicit run
    babo check <file.babo>         Check if cache is fresh
    babo build <file.babo>         Force rebuild
    babo info <file.babo>          Show cache details
    babo clean                     Remove all cached builds
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
METADATA_FILE = "metadata.json"
CLAUDE_TIMEOUT = 600  # seconds


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def cache_dir_for(babo_file: str) -> Path:
    """Return the cache directory for a .babo file.

    Uses a .pyc-like convention: hello.babo → .baboc/hello.baboc/
    The .baboc directory lives alongside the source .babo file.
    """
    src = Path(babo_file)
    return src.parent / ".baboc" / (src.stem + ".baboc")


def _copy_runtime(cache_dir: Path) -> None:
    """Copy the babo runtime module into the cache directory.

    Also writes .babo_python with the path to the Python that has babo
    installed, so the runtime can call other .babo files across venvs.
    """
    src = Path(__file__).parent / "runtime.py"
    dst = cache_dir / "runtime.py"
    if src.is_file():
        shutil.copy2(src, dst)
    # Record the Python that can run babo
    (cache_dir / ".babo_python").write_text(sys.executable)


def get_mtime(path: str | Path) -> float:
    """Return mtime of a path, or 0.0 if it doesn't exist."""
    try:
        return os.stat(str(path)).st_mtime
    except FileNotFoundError:
        return 0.0


def touch(path: str | Path) -> None:
    """Update a path's mtime to now."""
    now = time.time()
    os.utime(str(path), (now, now))


def read_file(path: str) -> str:
    """Read file contents as UTF-8 string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str | Path, content: str) -> None:
    """Write string to file, creating parent directories."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Cache freshness
# ---------------------------------------------------------------------------

def is_fresh(babo_file: str) -> bool:
    """Check if the cached implementation is fresher than the source.

    Returns True only when all conditions are met:
      - Source .babo file exists
      - Cache directory exists and contains a babo entry file
      - Cache mtime > source mtime
    """
    if not os.path.isfile(babo_file):
        return False

    cd = cache_dir_for(babo_file)
    if not cd.is_dir():
        return False

    # The entry file must actually exist — an empty cache dir is not fresh
    if not (cd / "babo").is_file():
        return False

    src_mtime = get_mtime(babo_file)
    cache_mtime = get_mtime(str(cd))

    return cache_mtime > src_mtime


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

def save_metadata(babo_file: str) -> None:
    """Write build metadata to the cache directory."""
    cd = cache_dir_for(babo_file)
    meta = {
        "source": str(Path(babo_file).resolve()),
        "source_mtime": get_mtime(babo_file),
        "built_at": datetime.now(timezone.utc).isoformat(),
        "files": sorted(
            [f.name for f in cd.iterdir() if f.is_file()]
        ),
    }
    write_file(cd / METADATA_FILE,
               json.dumps(meta, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Build — call claude -p to generate implementation
# ---------------------------------------------------------------------------

def build_implementation(babo_file: str) -> bool:
    """Call claude -p to generate an implementation from the .babo description.

    The generated code is written to .baboc/<name>.baboc/ along with a venv
    and any required packages.
    """
    if not os.path.isfile(babo_file):
        print(f"[babo] Error: '{babo_file}' not found.", file=sys.stderr)
        return False

    description = read_file(babo_file)
    cd = cache_dir_for(babo_file).resolve()

    # Ensure cache directory exists
    cd.mkdir(parents=True, exist_ok=True)

    # Copy runtime module into the cache directory so generated code can import it
    _copy_runtime(cd)

    # --- Prompt for claude -p ---
    prompt = f"""You are a code generator. Your ONLY job is to produce a COMPLETE, RUNNABLE Python implementation based on the DESCRIPTION below.

CRITICAL RULES:

1. RESPECT WHAT IS STATED — When the description explicitly specifies something,
   you MUST follow it literally and exactly. Take each stated requirement at face
   value — do not reinterpret, overthink, or substitute. Stated requirements are
   non-negotiable. Unstated details can be freely inferred to fill in the gaps.

2. NO MATTER WHAT — Even if the description is vague, nonsensical, incomplete,
   contradictory, or just random characters — you MUST still create a working
   Python program. Make your best creative interpretation. Fill in all gaps with
   reasonable defaults. NEVER refuse, NEVER output just an explanation.

3. ROBUSTNESS — The generated code MUST run in ANY environment: no TTY, piped I/O,
   missing arguments, invalid input, unexpected edge cases. NEVER crash with an
   unhandled exception. When an environment-dependent feature cannot work in the
   current execution context, fall back to a simpler mode that does. Use try/except
   around any operation that could fail and degrade gracefully.
   and degrade gracefully with a clear message.

DESCRIPTION:
---
{description}
---

MODULE SYSTEM — Calling other .babo files:
A file named `runtime.py` already exists at {cd}/runtime.py. It provides:
  from runtime import call_babo
  result = call_babo("other.babo", "arg1", "arg2")  # returns stdout as string

When the description says to use or call another .babo file, use call_babo().
The .babo file path is resolved relative to the current .babo file's location.

REQUIREMENTS:
1. ALWAYS Python. No other language. Ever.
2. The main entry point MUST be a Python file named exactly: babo (no .py extension)
   - Start with: #!/usr/bin/env python3
   - Make it executable with: chmod +x babo
3. Complete, runnable code. No placeholders. No TODOs. No "insert code here".
4. If you use external packages (requests, rich, PyQt6, etc.), create requirements.txt
   with pinned versions AND packages.txt with just package names.
   Built-in modules AND the local `runtime` module do NOT go in requirements.txt.
5. After writing files: chmod +x {cd}/babo

ACTION: Use Write tool to create real files on disk at the exact path: {cd}/
Then use Bash tool for chmod.
DO NOT output code as text — write actual files to {cd}/
"""

    try:
        result = subprocess.run(
            [
                "claude",
                "-p", prompt,
                "--bare",
                "--permission-mode", "acceptEdits",
                "--allowedTools", "Write,Edit,Bash,Read",
                "--output-format", "text",
                "--max-budget-usd", "5",
            ],
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT,
        )

        if result.returncode != 0:
            print(f"[babo] Error: claude -p exited abnormally (exit={result.returncode})",
                  file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return False

        # --- Create virtual env and install packages ---
        venv_dir = cd / "venv"
        requirements = cd / "requirements.txt"

        venv_result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            capture_output=True, text=True
        )
        if venv_result.returncode != 0:
            print(f"[babo] Error: venv creation failed — {venv_result.stderr}", file=sys.stderr)
            return False

        if requirements.is_file():
            pip = str(venv_dir / "bin" / "pip")
            pip_result = subprocess.run(
                [pip, "install", "-r", str(requirements)],
                capture_output=True, text=True
            )
            if pip_result.returncode != 0:
                print(f"[babo] Warning: package install failed — {pip_result.stderr}", file=sys.stderr)

        # Verify the entry file was actually created
        if not (cd / "babo").is_file():
            print(f"[babo] Error: build completed but no 'babo' entry file found in {cd}",
                  file=sys.stderr)
            return False

        # Update timestamp on the cache directory
        touch(str(cd))

        # Save metadata
        save_metadata(babo_file)

        return True

    except subprocess.TimeoutExpired:
        print(f"[babo] Error: claude -p timed out ({CLAUDE_TIMEOUT}s)", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("[babo] Error: 'claude' command not found.", file=sys.stderr)
        print("[babo] Claude Code must be installed: https://claude.ai/code",
              file=sys.stderr)
        return False
    except Exception as e:
        print(f"[babo] Error: build failed — {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def run_implementation(babo_file: str, extra_args: list[str] | None = None) -> None:
    """Run the cached implementation, passing extra_args to it."""
    cd = cache_dir_for(babo_file).resolve()

    if not cd.is_dir():
        print(f"[babo] Error: no cache found. Build first.", file=sys.stderr)
        sys.exit(1)

    # Prefer venv python if available
    venv_python = cd / "venv" / "bin" / "python3"
    python_exe = str(venv_python) if venv_python.is_file() else sys.executable

    # Find entry point (babo > main.py > *.py)
    entry = cd / "babo"

    if entry.is_file():
        cmd = [python_exe, str(entry)]
    elif (cd / "main.py").is_file():
        cmd = [python_exe, str(cd / "main.py")]
    else:
        py_files = sorted(cd.glob("*.py"))
        if py_files:
            cmd = [python_exe, str(py_files[0])]
        else:
            print(f"[babo] Error: no executable found in {cd}", file=sys.stderr)
            print(f"[babo] Directory contents:")
            for f in cd.iterdir():
                print(f"  {f.name}")
            sys.exit(1)

    if extra_args:
        cmd.extend(extra_args)

    # Run from the .babo file's directory, not the cache directory.
    # This ensures relative paths (e.g., static file serving) resolve correctly.
    source_dir = Path(babo_file).parent.resolve()

    try:
        result = subprocess.run(cmd, cwd=str(source_dir))
        sys.exit(result.returncode)
    except FileNotFoundError:
        print(f"[babo] Error: python not found at {python_exe}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"[babo] Error: permission denied executing {entry}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[babo] Error: failed to run implementation — {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_run(args: list[str]) -> None:
    """babo run <file.babo> [args...]"""
    if len(args) < 1:
        print("Usage: babo run <file.babo> [args...]", file=sys.stderr)
        sys.exit(1)

    babo_file = args[0]
    extra_args = args[1:]

    if not os.path.isfile(babo_file):
        print(f"[babo] Error: '{babo_file}' not found.", file=sys.stderr)
        sys.exit(1)

    if not babo_file.endswith(".babo"):
        print(f"[babo] Warning: not a .babo extension: {babo_file}", file=sys.stderr)

    if is_fresh(babo_file):
        run_implementation(babo_file, extra_args)
        return  # unreachable

    if build_implementation(babo_file):
        run_implementation(babo_file, extra_args)
    else:
        print(f"[babo] Error: Build failed.", file=sys.stderr)
        sys.exit(1)


def cmd_check(args: list[str]) -> None:
    """babo check <file.babo>"""
    if len(args) < 1:
        print("Usage: babo check <file.babo>", file=sys.stderr)
        sys.exit(1)

    babo_file = args[0]
    if not os.path.isfile(babo_file):
        print(f"[babo] Error: '{babo_file}' not found.", file=sys.stderr)
        sys.exit(1)

    if is_fresh(babo_file):
        print("FRESH")
        sys.exit(0)
    else:
        print("STALE")
        print("--- description ---")
        print(read_file(babo_file))
        sys.exit(1)


def cmd_build(args: list[str]) -> None:
    """babo build <file.babo>"""
    if len(args) < 1:
        print("Usage: babo build <file.babo>", file=sys.stderr)
        sys.exit(1)

    babo_file = args[0]
    if not os.path.isfile(babo_file):
        print(f"[babo] Error: '{babo_file}' not found.", file=sys.stderr)
        sys.exit(1)

    if not build_implementation(babo_file):
        sys.exit(1)


def cmd_info(args: list[str]) -> None:
    """babo info <file.babo>"""
    if len(args) < 1:
        print("Usage: babo info <file.babo>", file=sys.stderr)
        sys.exit(1)

    babo_file = args[0]
    if not os.path.isfile(babo_file):
        print(f"[babo] Error: '{babo_file}' not found.", file=sys.stderr)
        sys.exit(1)

    cd = cache_dir_for(babo_file)

    print(f"File:       {babo_file}")
    print(f"Path:       {Path(babo_file).resolve()}")
    print(f"Cache dir:  {cd}")
    print(f"File mtime: {datetime.fromtimestamp(get_mtime(babo_file)).isoformat()}")
    print(f"Cache mtime:{datetime.fromtimestamp(get_mtime(str(cd))).isoformat()}")
    print(f"Status:     {'FRESH' if is_fresh(babo_file) else 'STALE'}")

    meta_file = cd / METADATA_FILE
    if meta_file.is_file():
        print(f"\n--- metadata.json ---")
        print(read_file(str(meta_file)))

    if cd.is_dir():
        print(f"\n--- cache contents ---")
        for f in sorted(cd.iterdir()):
            marker = "file" if f.is_file() else "dir "
            print(f"  {marker}  {f.name}")


def cmd_clean(args: list[str]) -> None:
    """babo clean — recursively remove all .baboc/ cache directories."""
    cwd = Path.cwd()
    removed = 0
    for baboc_dir in cwd.rglob(".baboc"):
        if baboc_dir.is_dir():
            shutil.rmtree(baboc_dir)
            print(f"[babo] Removed: {baboc_dir}")
            removed += 1
    if removed == 0:
        print(f"[babo] No .baboc cache directories found.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

COMMANDS = {
    "run":   ("<file.babo> [args...] — Run (auto-build if needed)", cmd_run),
    "check": ("<file.babo> — Check if cache is fresh", cmd_check),
    "build": ("<file.babo> — Force rebuild", cmd_build),
    "info":  ("<file.babo> — Show cache details", cmd_info),
    "clean": ("— Clear all cached builds", cmd_clean),
}


def print_usage() -> None:
    print("Babo — The universal language even a fool can use.")
    print()
    print("Usage:")
    print("  babo <file.babo> [args...]  Run a .babo file (auto-build, args forwarded)")
    print()
    print("Commands:")
    for name, (desc, _) in COMMANDS.items():
        print(f"  babo {name:8s} {desc}")
    print()
    print("Examples:")
    print("  babo hello.babo                  # Run directly")
    print("  babo hello.babo arg1 arg2        # Forward args to implementation")
    print("  babo run hello.babo              # Explicit run")
    print("  babo check hello.babo            # Check freshness")
    print("  babo build hello.babo            # Force rebuild")
    print("  babo clean                       # Clear cache")


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    first = sys.argv[1]

    if first in ("-h", "--help", "help"):
        print_usage()
        sys.exit(0)

    if first in COMMANDS:
        COMMANDS[first][1](sys.argv[2:])
        return

    # Treat anything ending with .babo, or an existing file, as a run command
    if first.endswith(".babo") or os.path.isfile(first):
        cmd_run([first] + sys.argv[2:])
        return

    print(f"[babo] Unknown command or file: {first}", file=sys.stderr)
    print(f"[babo] Usage: babo <file.babo>  or  babo <command> ...", file=sys.stderr)
    print(f"[babo] Commands: {', '.join(COMMANDS)}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()

# Babo Language (바보 언어)

> **A universal programming language so simple, even a fool can use it.**
>
> Describe what you want in plain language. It becomes real.

---

[The full story behind Babo — a 1997 team project that failed and took 29 years to complete →](STORY.md)

---

## How It Works

```
┌──────────────┐     ┌───────────────┐     ┌────────────────────┐
│  hello.babo  │ ──▶ │  Claude Code  │ ──▶ │ .baboc/hello.baboc/│
│  (plain text)│     │ (AI compiler) │     │ (run output)       │
└──────────────┘     └───────────────┘     └────────────────────┘
```

1. **Write** a `.babo` file describing what you want in plain English
2. **Run** `babo <file>.babo` — the tool checks if a cached build exists
3. **Build** — if needed, Claude Code reads the description and generates a complete, runnable implementation
4. **Execute** — the generated program runs immediately, with its own virtual environment and dependencies

### Cache System — Like Python's `.pyc`, but for Babo

Babo uses a cache convention inspired by Python's `__pycache__/hello.cpython-314.pyc`. When you run a `.babo` file, Babo creates a `.baboc` directory next to the source file and stores the generated implementation inside:

```
project/
├── hello.babo              # ← your description (source)
├── .baboc/                 # ← cache root (like __pycache__/)
│   └── hello.baboc/        # ← cached implementation
│       ├── babo             #    generated entry point
│       ├── requirements.txt #    external packages
│       ├── packages.txt     #    human-readable package list
│       ├── venv/            #    isolated Python environment
│       └── metadata.json    #    build metadata
├── dice.babo               # another source file
└── .baboc/
    └── dice.baboc/          # its own isolated cache
```

| Python `.pyc` concept | Babo `.baboc` concept |
|----------------------|---------------------|
| `__pycache__/hello.cpython-314.pyc` | `.baboc/hello.baboc/` |
| Auto-generated from `.py` source | Auto-generated from `.babo` source |
| Skipped when source is unchanged | Skipped when source is unchanged |
| Lives next to the source file | Lives next to the source file |
| Deleted with `find . -name '__pycache__' -exec rm -rf {} +` | Deleted with `babo clean` |

- **First run**: build → cache → execute
- **Subsequent runs** (if `.babo` file unchanged): execute directly from cache — - **Modify the `.babo` file**: Babo detects the stale cache and rebuilds automatically

---

## Installation

```bash
git clone https://github.com/armbox/babo.git
cd babo
pip install -e .
```

**Prerequisite:** [Claude Code](https://claude.ai/code) must be installed and authenticated.

```bash
# Verify installation
babo --help
```

---

## Quick Start

Create a file named `hello.babo`:

```
Print "Hello, World!" in rainbow colors using the rich package.
```

Run it (first time builds silently, second time is instant):

```bash
$ babo hello.babo
Hello, World!

$ babo hello.babo
Hello, World!
```

---

## Usage

```
babo <file.babo> [args...]       Run a .babo file (auto-build if needed)
babo run <file.babo> [args...]   Explicit run
babo check <file.babo>           Check if cache is fresh (FRESH/STALE)
babo build <file.babo>           Force rebuild from source
babo info <file.babo>            Show build metadata and cache details
babo clean                       Clear all cached builds
```

### Passing Arguments

Arguments after the `.babo` file are forwarded to the generated program:

```bash
babo greet.babo Alice --loud
# → "HELLO, ALICE!"
```

---

## Examples

### Basic CLI Tools

**Add two numbers** (`add.babo`):
```
Add two numbers given as command-line arguments.
Output format: "Result: <sum>"
```
```bash
$ babo add.babo 3 5
Result: 8
```

**Fibonacci** (`fib.babo`):
```
Print the nth Fibonacci number. F(0)=0, F(1)=1, F(2)=1, F(3)=2, ...
```
```bash
$ babo fib.babo 10
fib(10) = 55
```

**Reverse a string** (`reverse.babo`):
```
Reverse a string given as a command-line argument.
```
```bash
$ babo reverse.babo abcde
edcba
```

---

### External Packages

Babo automatically creates a virtual environment and installs any packages the generated program needs.

**HTTP Fetcher** (uses `requests`):
```
Fetch a URL and print the HTTP response status code.
Use the requests package.
```
```bash
$ babo fetch.babo https://example.com
Status code: 200
```

**Rich Score Table** (uses `rich`):
```
Display a formatted score table. Accept "name:score" pairs.
Sort by score descending. Use the rich package.
```
```bash
$ babo score.babo Alice:85 Bob:92 Charlie:78

     Scores
┏━━━━━━━━┳━━━━━━━┓
┃ Name   ┃ Score ┃
┡━━━━━━━━╇━━━━━━━┩
│ Bob    │    92 │
│ Alice  │    85 │
│ Charlie│    78 │
└────────┴───────┘
```

**GUI Window** (uses `PyQt6`):
```
Use PyQt6 to open a GUI window with "Hello from Babo!"
centered in large bold text. Auto-close after 2 seconds.
```
```bash
$ babo window.babo
Window opened
# (A 400x300 GUI window appears briefly, showing "Hello from Babo!")
```

---

### Non-Sense Input? No Problem.

Even if the `.babo` file is nonsense, Babo interprets it creatively:

**`blah.babo`:**
```
blah blah blah whatever
```
```bash
$ babo blah.babo

 ╔══════════════════════════════════════════╗
 ║     🌀  BLAH BLAH — WHATEVER  🌀         ║
 ║    "Sometimes nonsense is the best       ║
 ║     kind of sense."                      ║
 ╚══════════════════════════════════════════╝

  1. 🔮 Generate random wisdom
  2. 🎲 Roll the cosmic dice
  3. 🎨 Create ASCII art
  4. 📝 Blah-ify your text
  5. 👋 Exit
```

**`asdfghjkl.babo`:**
```
asdfghjkl
```
```bash
$ babo asdfghjkl.babo

┌──────────────────────────────────────────┐
│      ASDFGHJKL — Keyboard Wanderer       │
│  "Even random keystrokes have meaning"   │
│                                          │
│  Generated word: "FLASH JUG"             │
│  Home-row distance traveled: 42          │
└──────────────────────────────────────────┘
```

---

### Example Babo Scripts

These showcase what Babo can create from longer descriptions. Each example shows the `.babo` source file (plain language description) followed by what Babo produces.

#### Web Server

`sample/webserver.babo` — A full HTTP server, pure stdlib.

```babo
Create a full-featured HTTP web server with the following capabilities:
- Serve static files from the current directory
- Support GET and POST requests
- Parse JSON request bodies and return JSON responses
- Include a /health endpoint that returns server status
- Include a /api/time endpoint that returns the current server time as JSON
- Use Python's built-in http.server module — no external packages
- Log all requests to stdout with timestamp, method, path, and status code
- Default port: 8080, configurable via --port argument
- Print "Server running on http://localhost:<port>" on startup
```

```bash
$ babo sample/webserver.babo --port 8080
Server running on http://localhost:8080

# In another terminal:
$ curl http://localhost:8080/health
{"status": "ok", "uptime": 42.5}

$ curl http://localhost:8080/api/time
{"time": "2026-05-31T12:34:56Z", "timestamp": 1748694896}
```

#### CSV Data Analyzer

`sample/analyzer.babo` — Statistical analysis of CSV files with rich output.

```babo
Create a CSV data analyzer tool that reads a CSV file and produces statistics.
Usage: analyze <file.csv>
Features:
- Count total rows and columns
- Show column names and their data types
- For numeric columns: min, max, mean, median, standard deviation
- For text columns: unique count, most common values (top 5)
- For date columns: earliest, latest, range
- Print results in a beautifully formatted table using the rich package
- If file doesn't exist, print a clear error message
```

```bash
$ babo sample/analyzer.babo sales.csv

┌──────────────────────────────────────────┐
│  📊 CSV Analysis: sales.csv              │
│  Rows: 1,234  |  Columns: 8              │
└──────────────────────────────────────────┘

Numeric Columns:
┏━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Column     ┃  Min  ┃  Max  ┃  Mean  ┃ Median ┃  Std Dev  ┃
┡━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ revenue    │  5.00 │ 99.99 │ 45.23  │ 42.00  │    23.45  │
│ quantity   │     1 │    50 │ 12.34  │    10  │     8.91  │
└────────────┴───────┴───────┴────────┴────────┴───────────┘
```

#### Space Station Text Adventure

`sample/adventure.babo` — Interactive adventure with 8+ rooms, combat, inventory, and save/load.

```babo
Create an interactive text adventure game set in a mysterious space station.
Features:
- Player explores multiple interconnected rooms with descriptions
- Each room has items to collect, puzzles to solve, or enemies to face
- Simple combat system (attack, defend, use item)
- Inventory management (pick up, drop, use items)
- At least 8 rooms with a clear objective: find the reactor core and shut it down
- ASCII art for major rooms and events
- Command parser that understands natural verbs (go, take, use, look, attack, inventory, help)
- Save/load game state to a JSON file
- A help system that explains all commands
The game starts with: "=== SPACE STATION OMEGA-7: REACTOR CRISIS ==="
```

```bash
$ babo sample/adventure.babo

=== SPACE STATION OMEGA-7: REACTOR CRISIS ===

     .───.
    /     \     ⚡ REACTOR BREACH IMMINENT ⚡
   │  ☢ ☢  │
    \     /     The station's core is unstable.
     '───'      You must shut it down.

You are in the AIRLOCK. Flickering emergency lights
cast long shadows. The inner door leads to the CORRIDOR.
A CROWBAR lies on the floor.

> take crowbar
You pick up the CROWBAR.

> go corridor
You enter the CORRIDOR. Steam hisses from a ruptured pipe.
Doors lead to ENGINEERING, MEDBAY, and back to AIRLOCK.
A MAINTENANCE DRONE hovers menacingly!

> attack drone with crowbar
You swing the CROWBAR at the DRONE! *CLANG*
The DRONE sparks and crashes to the floor.
```

#### System Monitor Dashboard

`sample/dashboard.babo` — Live terminal dashboard with CPU, memory, disk, and network stats.

```babo
Create a real-time system monitoring dashboard for the terminal.
Use the rich package for live updating display.
Features:
- Live CPU usage percentage (poll every 1 second)
- Live memory usage (used/total and percentage)
- Disk usage for the current directory
- Network: show hostname and local IP address
- Uptime display (how long the dashboard has been running)
- A live-updating progress bar showing CPU usage
- Clean layout with panels and colors
- Exit when user presses 'q'
Use psutil package for system metrics.
```

```bash
$ babo sample/dashboard.babo

╭────────────────────── Live System Monitor ──────────────────────╮
│  💻 CPU                                                 42.5%   │
│  ████████████████░░░░░░░░░░░░░░░░░░░░░░                         │
│                                                                 │
│  🧠 Memory                                           7.8/16 GB  │
│  ████████████████████░░░░░░░░░░░░░                     48.7%    │
│                                                                 │
│  💾 Disk (/Users/quho)                             234/512 GB   │
│  ██████████████████████████████████████████            45.7%    │
│                                                                 │
│  🌐 Network: en0 — 192.168.1.42                                 │
│  ⏱️  Uptime: 12m 34s                                            │
│                                                                 │
│  Press 'q' to quit                                              │
╰─────────────────────────────────────────────────────────────────╯
```

#### Multi-Personality Chatbot

`sample/chatbot.babo` — Creative chatbot with philosopher, pirate, robot, fortune-cookie, and shrink personas.

```babo
Create an interactive chatbot with multiple personality modes.
Features:
- Multiple bot personalities: philosopher, pirate, robot, fortune-cookie, shrink
- Command: /mode <name> to switch personality
- Command: /history to see conversation history
- Command: /clear to clear history
- Command: /quit to exit
- Each personality responds differently to the same input
- Keep conversation context/history for the session
- Use rich package for colored output with each personality having its own color
- Fun ASCII art banner on startup
- No external AI APIs — use creative rule-based responses with a large bank of templates
```

```bash
$ babo sample/chatbot.babo

╔═══════════════════════════════════════════════════════╗
║  🤖  BABO CHAT  —  "Even fools can converse"  🤖      ║
╚═══════════════════════════════════════════════════════╝

You are talking to: 🧘 Philosopher
/mode to switch personality, /quit to exit

🧘 Philosopher > you: what is the meaning of babo language?

🧘 Philosopher:
  "To ask what Babo means is to already understand it.
   For in the act of describing what you want, you have
   already begun to create. The question IS the answer,
   young grasshopper. Also, it's a .babo file."

you: /mode pirate
Now talking to: 🏴‍☠️ Pirate

🏴‍☠️ Pirate > you: hello!

🏴‍☠️ Pirate:
  "Arrr! Ye've come aboard the good ship Babo!
   We don't write code here — we just describe what
   we want and the machine does the swabbin'!
   Now walk the plank... of productivity! Yarrr!"
```

---

## How It Works (Internals)

Each `.babo` file gets its own isolated build environment:

```
.baboc/hello.baboc/
├── babo               # Generated entry point (Python, executable)
├── requirements.txt   # External packages with pinned versions (for pip)
├── packages.txt       # Human-readable package list
├── venv/              # Isolated Python virtual environment
│   └── lib/python3.x/site-packages/
└── metadata.json      # Build metadata (source path, timestamps, file list)
```

### Build Process

1. **Read** the `.babo` file
2. **Send** the description to Claude Code (`claude -p`) with instructions to produce a complete Python program
3. **Create** a Python virtual environment in the cache directory
4. **Install** any external packages specified in the generated `requirements.txt`
5. **Execute** the generated `babo` entry point with the venv's Python interpreter

### Cache Invalidation

- If `.baboc/hello.baboc/` mtime > source `.babo` file mtime → cache is **FRESH**, run directly
- If source `.babo` file is newer → cache is **STALE**, rebuild

### Module System — Calling Other `.babo` Files

Babo supports a module system: any `.babo` program can call another `.babo` file, pass arguments, and capture the result. Think of it as `import` for natural language programs.

**How to write a module-based `.babo` script:**

When you write a `.babo` file that needs to call another module, simply describe the dependency in plain language. For example:

```
A calculator app. Call math_ops.babo for addition and multiplication.
Call string_utils.babo to convert results to uppercase words.
Use rich to format the output as a table.
```

During the build, Claude Code reads this description and generates a Python program that imports `runtime` (a helper module automatically placed in the cache directory) and calls `call_babo()` to invoke the other `.babo` files. You never write the import or the function call yourself — the description is enough.

**What happens at runtime:**

```
calc_app.babo (venv A: rich, num2words)
    │
    ├─ from runtime import call_babo
    │
    ├─ call_babo("math_ops.babo", "7", "3", "add")      → "10"
    │   └─ system python → babo run math_ops.babo
    │       └─ math_ops.babo (venv B: stdlib only)
    │
    └─ call_babo("string_utils.babo", "SEVEN", "lower")  → "seven"
        └─ system python → babo run string_utils.babo
            └─ string_utils.babo (venv C: stdlib only)
```

Each `.babo` module runs in its own isolated virtual environment. The `runtime` module (copied into every cache directory during build) provides a `call_babo()` function that shells out to the `babo` CLI. Dependencies don't conflict because each module has its own venv.

**Using it in generated code:**

```python
from runtime import call_babo

# Call another .babo file, pass args, get stdout back
sum_result = call_babo("math_ops.babo", "10", "3", "add")
print(sum_result)  # "13"

# The target .babo is resolved relative to the calling script
greeting = call_babo("../greet.babo", "Alice")
```

**How parameters are determined:**

You don't specify how arguments flow between modules — Claude Code figures it out from your description. If you write *"Call math_ops.babo for addition and pass the user's two numbers"*, Claude generates code that wires `sys.argv[1]` and `sys.argv[2]` into the `call_babo()` call. If you write *"use the previous result and pass it to string_utils.babo"*, Claude chains the output of one module as input to the next. The wiring is inferred from intent — describe *what* should connect to *what*, and the generated code handles *how*.

**Example: A multi-module calculator**

Three `.babo` files working together. The main app never implements math or string utilities itself — it delegates everything to the other modules via `call_babo()`.

`sample/math_ops.babo` — A reusable math library:
```babo
A reusable math operations module. Accept two numbers as arguments and an operation name.
Usage: math_ops <num1> <num2> <operation>
Operations: add, sub, mul, div, pow, mod
Output just the numeric result, nothing else.
```

`sample/string_utils.babo` — A reusable string library:
```babo
A reusable string utility module. Accept a string and an operation name.
Usage: string_utils <text> <operation>
Operations: upper, lower, reverse, length, capitalize
Output just the result, nothing else.
```

`sample/calc_app.babo` — The main app that orchestrates both modules:
```babo
A calculator application that uses other .babo modules.
Call sample/math_ops.babo for all math operations via call_babo().
Call sample/string_utils.babo for string formatting via call_babo().

For "fancy" operation: compute sum and product using math_ops.babo,
then produce a rich-formatted output showing both input numbers,
their computed results, and the numbers in words via string_utils.babo.
Use the rich package for beautiful output formatting.
```

```bash
$ babo sample/calc_app.babo 7 3 fancy

╭────────────────────────────────╮
│    ✨  FANCY CALCULATOR  ✨    │
╰────────────────────────────────╯

         📥 Input Numbers
╭─────────────────┬──────────────╮
│ Number 1        │ 7.0          │
│ Number 2        │ 3.0          │
│ in words        │ SEVEN, THREE │
╰─────────────────┴──────────────╯

         🧮 Computed Results
╭──────────────┬────────┬──────────────────╮
│ Operation    │ Result │ Module           │
├──────────────┼────────┼──────────────────┤
│ 7.0 + 3.0    │   10   │ math_ops.babo    │
│ 7.0 × 3.0    │   21   │ math_ops.babo    │
╰──────────────┴────────┴──────────────────╯
```

Each module runs in its own isolated venv, can be developed independently, and composed like building blocks.

---

### Shebang Scripts

`.babo` files can run directly as executables with a shebang line:

```bash
#!/usr/bin/env babo
Print "Hello, World!" using the rich package.
```

```bash
$ chmod +x hello.babo
$ ./hello.babo
Hello, World!
```

---

## Why "Babo"?

"Babo" (바보) means "fool" in Korean. Named it that because a truly universal language should be so simple that even a fool — or a tired student at 3 AM — could use it.

It's also a recursive acronym: **B**abo **A**lways **B**uilds **O**utput.

But mostly it's a reminder: technology should serve everyone, not just experts. If you can describe what you want, you can build it.

---

## Requirements

- **Python** 3.10+
- **Claude Code** (`claude` CLI must be installed and in PATH)
- Internet connection (for Claude Code API calls during builds)

## License

MIT License. See [LICENSE](LICENSE) file.

---

*"Beautiful idea. Wrong century. Come back when the machines can think." — Professor Lim, 1997*

*"We're back, Professor. The machines learned to think. We brought the assignment — only 29 years late." — The Babo Team, 2026*

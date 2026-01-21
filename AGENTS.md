Agent Guide for traveling_salesman_solver

This file provides the rules, constraints, and context required for coding agents working on the traveling_salesman_solver repository. It complements the human-oriented README and establishes conventions for safe, consistent automated edits.

Agents must follow all instructions contained here when modifying code, writing new modules, or performing maintenance tasks.

Project Overview

traveling_salesman_solver is a personal errand route planner.
It reads a YAML file containing a home address and a set of destinations.
The system geocodes each location, queries the OpenRouteService API to build a distance or duration matrix, and runs a hillclimbing-based traveling salesman solver to produce an optimal or near-optimal route.

The codebase is organized into three modules:
* main.py orchestrates I/O, argparse, and module coordination.
* openroute.py handles YAML parsing, geocoding, and OpenRouteService API calls.
* routesolver.py implements the TSP solver.

Agents modifying code must preserve this structure.

Data formats

YAML input (preferred)

The routes.yaml file has the structure:

home: 2643 N Drury Ln, Arlington Heights, IL 60004
locations:
, CVS: 20 E Dundee Rd, Buffalo Grove, IL 60089
, Best Buy AH: 615 E Palatine Rd, Arlington Heights, IL 60004
, Best Buy VH: 701 N Milwaukee Ave Ste 152, Vernon Hills, IL 60061
, UPS Store: 309 E Rand Rd, Arlington Heights, IL 60004

Agents must ensure:
* YAML keys and values remain human readable.
* No CSV is introduced for addresses, because commas degrade readability.
* No schema changes are made unless explicitly requested.

Python coding rules for this repository

Agents must follow these rules when writing or editing code.

Interpreter and style
* Code targets Python 3.12 unless otherwise instructed.
* Always use tabs for indentation, never spaces.
* Code must start with #!/usr/bin/env python3.
* Prefer short, single-purpose functions.
* All functions require Google-style docstrings.
* Use f-strings for formatting.
* Keep line length under 100 characters.
* ASCII only in comments; escape non-ASCII if needed.
* Return values must be stored in variables, then returned.
* Avoid semicolons and multi-statement lines.

Structure
* Use def main() and the standard guard:

if __name__ == '__main__':
main()

* Each file should visually separate functions using:

#============================================

* Use frequent inline comments explaining non-obvious logic.

Imports

Agents must:
* Use only explicit import statements.
* Never use import *.
* Avoid aliasing such as import numpy as np; write import numpy.
* Keep import ordering:

# Standard Library
import os
import re
import sys
import time
import random
import argparse

# PIP modules
import numpy
import requests
import yaml
import openrouteservice

# Local modules
import openroute
import routesolver

Order should be shortest module name first, alphabetical within group.

Error handling
* Avoid broad try/except.
* Use try/except only for short, necessary operations.
* Do not call sys.exit; raise an explicit error instead.
* API functions must add time.sleep(random.random()) before network calls.

Testing and validation

Agents should prefer:
* Adding lightweight assert statements for simple, pure functions.
* Avoiding asserts for functions using network I/O, file I/O, or user data.

Static analysis:
* Code should pass pyflakes and mypy without errors.
* Agents must update type hints when modifying signatures.

API interaction

Agents must:
* Use OpenRouteService through openroute.py.
* Never hardcode API keys; read from YAML config.
* Add time.sleep(random.random()) before API requests unless disabled by config.
* Keep the geocoding and matrix retrieval logic isolated in openroute.py.

Code generation expectations for agents

Agents must:
* Respect the existing module structure.
* Avoid introducing new frameworks or libraries.
* Maintain consistent naming, spacing, indentation, and docstrings.
* Use the hillclimbing solver in routesolver.py unless explicitly replacing it.
* Preserve the YAML input schema unless changes are requested.

Agents must not:
* Introduce CSV, JSON, or database storage unless instructed.
* Switch geocoding providers without direction.
* Add asynchronous code.
* Add complex error systems, decorators, or metaclasses.

Build and run instructions

Agents may assume:
* Execution:

python3 main.py --config routes.yaml

* No build step is required.
* No test suite exists yet, but simple asserts are allowed.

Pull Request behavior for agents

When performing multi-file edits:
* Ensure imports remain consistent.
* Ensure indentation remains tabs.
* Run static tools (pyflakes, mypy) and fix errors.
* Verify that API requests remain isolated to openroute.py.
* Confirm that YAML formats remain valid and human readable.

Security and safety considerations
* Never log or print API keys.
* Never embed credentials in the code.
* Avoid introducing external network dependencies.
* Keep dependencies minimal and visible.

Agent resolution rules
* If instructions in this file conflict with human chat instructions, human chat wins.
* If instructions conflict within this file, the more restrictive rule applies.
* Agents must not modify this file unless requested.
See Python coding style in docs/PYTHON_STYLE.md.
## Coding Style
See Markdown style in docs/MARKDOWN_STYLE.md.
When making edits, document them in docs/CHANGELOG.md.
See repo style in docs/REPO_STYLE.md.
Agents may run programs in the tests folder, including smoke tests and pyflakes/mypy runner scripts.

## Environment
Codex must run Python using `/opt/homebrew/opt/python@3.12/bin/python3.12` (use Python 3.12 only).
On this user's macOS (Homebrew Python 3.12), Python modules are installed to `/opt/homebrew/lib/python3.12/site-packages/`.
When in doubt, implement the changes the user asked for rather than waiting for a response; the user is not the best reader and will likely miss your request and then be confused why it was not implemented or fixed.
When changing code always run tests, documentation does not require tests.

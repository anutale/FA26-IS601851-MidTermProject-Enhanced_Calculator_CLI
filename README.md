# Enhanced Calculator CLI

A Python command-line calculator demonstrating object-oriented design,
arithmetic operation strategies, input validation, history persistence, and
undo/redo. Calculations use `Decimal` values, and history is stored as CSV
through pandas.

## Features

- Ten arithmetic operations, each accepting two numeric operands.
- Factory-created operation objects and interchangeable calculation strategies.
- Input validation, operation-specific errors, and a configurable input limit.
- Calculation history with CSV save/load and optional auto-save.
- Undo and redo for changes to in-memory history.
- Logging of calculations and a pandas DataFrame view of history.
- Unit tests and a GitHub Actions test workflow.

## Requirements and installation

- Python 3.10 or later
- pip

From the project root, create and activate a virtual environment, then install
the dependencies:

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, create and activate the environment with:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The requirements file includes the calculator's dependencies (including pandas
and python-dotenv) and the project's test/development tools.

## Run the calculator

```bash
python main.py                     # after activating the virtual environment
```

The calculator prompts for an operation and then two numbers. For example:

```text
Calculator started. Type 'help' for commands.

Enter command: percentage

Enter numbers (or 'cancel' to abort):
First number: 25
Second number: 200

Result: 12.5
```

Enter `cancel` at either operand prompt to abort the current calculation. Type
`help` in the REPL to display available commands.

## Arithmetic operations

The first input is `a`; the second input is `b`.

| Command | Calculation | Notes |
|---|---|---|
| `add` | `a + b` | Addition |
| `subtract` | `a - b` | Subtracts the second number from the first |
| `multiply` | `a * b` | Multiplication |
| `divide` | `a / b` | Rejects a zero divisor |
| `power` | `a ** b` | Negative exponents are not supported |
| `root` | `b`th root of `a` | Rejects negative `a` and a zero root degree |
| `modulus` | `a % b` | Remainder; rejects a zero divisor |
| `integer_division` | `a // b` | Quotient with the fractional part discarded; rejects a zero divisor |
| `percentage` | `(a / b) * 100` | Calculates what percentage `a` is of `b`; rejects a zero divisor |
| `absolute_difference` | `abs(a - b)` | Absolute difference between the inputs |

Invalid numeric input, values over the configured input limit, unsupported
operations, and invalid operands are reported as errors rather than silently
producing a result.

Inputs must be finite numeric values within the configured maximum absolute
value; for example, `NaN`, infinity, booleans, and values beyond the limit are
rejected with a corrective error message. CSV read/write failures are reported
as `OperationError` messages that identify the history file path.

## REPL commands

| Command | Behavior |
|---|---|
| `help` | Display operation and REPL commands |
| `history` | Show calculations currently in memory |
| `clear` | Clear in-memory history and undo/redo stacks |
| `undo` | Restore history to its state before the last calculation |
| `redo` | Restore the history state that was undone |
| `save` | Write history to the configured CSV file |
| `load` | Load history from the configured CSV file |
| `exit` | Save history and exit |

Undo and redo manage the history state; they do not reverse external side effects
such as an already-written log entry. Clearing history affects in-memory state;
use `save` or exit if the empty history should also be written to disk.

The `help` command builds its operation list from the operation factory
registry. To add an operation at runtime, define a class derived from
`Operation` and register its command with `OperationFactory`; it will then
appear in help and be accepted by the REPL without modifying the menu:

```python
OperationFactory.register_operation("custom", CustomOperation)
```

## History, logging, and configuration

By default, the calculator uses the repository root as its base directory:

- History CSV: `history/calculator_history.csv`
- Log file: `logs/calculator.log`

Each `Calculator` registers an observer that logs calculations and another
that saves history after each calculation when auto-save is enabled. History
CSV rows contain the operation, both operands, result, and timestamp. The
calculator also provides `get_history_dataframe()` for retrieving history as a
pandas DataFrame.

Configuration can be supplied through constructor arguments or environment
variables. The project loads `.env` from the repository root at startup without
overriding values already set in the process environment. To create a local
configuration, copy `.env.example` to `.env`; `.env` is ignored by git and
should not be committed. Invalid values raise `ConfigurationError` during
calculator initialization:

```bash
cp .env.example .env
```

Edit `.env` and set any values you want to override. For example:

```dotenv
CALCULATOR_LOG_DIR=./logs
CALCULATOR_HISTORY_DIR=./history
CALCULATOR_MAX_HISTORY_SIZE=1000
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=10
CALCULATOR_MAX_INPUT_VALUE=1e999
CALCULATOR_DEFAULT_ENCODING=utf-8
```

The checked-in `.env.example` contains these defaults and is safe to share;
put machine-specific settings only in the ignored `.env`. Boolean values accept
`true`/`false` and `1`/`0`. The maximum-history size and precision must be
positive integers, the maximum input must be a positive finite number, and the
encoding must be supported by Python. The process environment takes precedence
over values in `.env`.

| Environment variable | Default | Purpose |
|---|---|---|
| `CALCULATOR_BASE_DIR` | Project root | Base location for generated files |
| `CALCULATOR_MAX_HISTORY_SIZE` | `1000` | Maximum number of history entries retained |
| `CALCULATOR_AUTO_SAVE` | `true` | Auto-save after a calculation (`true`/`false`; `1`/`0` are also accepted) |
| `CALCULATOR_MAX_INPUT_VALUE` | `1e999` | Maximum absolute input value |
| `CALCULATOR_PRECISION` | `10` | Precision value retained in configuration |
| `CALCULATOR_DEFAULT_ENCODING` | `utf-8` | Encoding used for log and history files |
| `CALCULATOR_HISTORY_DIR` | `<base_dir>/history` | History directory |
| `CALCULATOR_HISTORY_FILE` | `<history_dir>/calculator_history.csv` | History CSV path |
| `CALCULATOR_LOG_DIR` | `<base_dir>/logs` | Log directory |
| `CALCULATOR_LOG_FILE` | `<log_dir>/calculator.log` | Log file path |

The precision value is retained in configuration and does not currently change
arithmetic results. Directory and file path variables can be used to keep
generated data outside the repository.

## Design and code organization

- **Factory:** `OperationFactory` maps operation names to operation classes.
- **Strategy:** each `Operation` implementation provides its own `execute`
  method; the calculator can switch the active operation at runtime.
- **Observer:** history observers log calculations and optionally auto-save.
- **Decorator:** a help-menu decorator adds the currently registered operation
  commands to the REPL's standard command list.
- **Memento:** snapshots of history support undo/redo.
- **Data model:** `Calculation` stores operands, operation, result, and
  timestamp, and supports serialization/deserialization.

## Testing and coverage

Run the full test suite from the repository root after installing
`requirements.txt`:

```bash
python -m pytest
```

Pytest runs all tests in `tests/`, reports application coverage in the
terminal, and writes an HTML report to `htmlcov/`. The project enforces a
minimum total coverage of 90%; the command exits unsuccessfully if the suite
falls below that threshold. Open `htmlcov/index.html` in a browser to inspect
per-file and per-line coverage. To run a focused selection:

```bash
python -m pytest tests/test_operations.py tests/test_calculation.py
```

## Continuous integration

The test workflow installs the pinned dependencies and runs pytest with
coverage enforcement on pushes and pull requests targeting `main`, using an
Ubuntu runner. It checks that tests pass and total application coverage is at
least 90%; it does not build or publish a release.

The workflow file is currently stored at
`.gitbub/workflows/tests.yml`. GitHub Actions only discovers workflow files
under `.github/workflows/`, so the workflow will not run automatically until
the directory is corrected to `.github/workflows/`.

## Project structure

```text
.
├── main.py                         # Application entry point
├── README.md                       # Project documentation
├── LICENSE
├── pyproject.toml                  # Project metadata and development extras
├── requirements.txt                # Pinned runtime and development dependencies
├── .env.example                    # Example calculator configuration
├── pytest.ini                      # Pytest discovery and coverage configuration
├── module_contents.md              # Course/module material
├── .gitbub/                        # Currently misspelled; see CI note above
│   └── workflows/
│       └── tests.yml               # CI test workflow
├── app/
│   ├── calculation.py              # Calculation model and result reconstruction
│   ├── calculator.py               # Calculator, history, persistence, undo/redo
│   ├── calculator_config.py        # Settings, paths, and configuration validation
│   ├── calculator_memento.py       # History snapshots for undo/redo
│   ├── calculator_repl.py          # Interactive command-line interface
│   ├── exceptions.py               # Calculator exception hierarchy
│   ├── history.py                  # Logging and auto-save observers
│   ├── input_validators.py         # Numeric input validation
│   └── operations.py               # Operations and operation factory
├── tests/
│   ├── conftest.py                 # Shared pytest setup
│   ├── test_calculation.py
│   ├── test_calculator.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_history.py
│   ├── test_operations.py
│   └── test_validators.py
├── history/                        # Runtime history CSV (git-ignored)
├── logs/                           # Runtime log file (git-ignored)
├── test_history/                   # Test history fixture data
└── test_logs/                      # Test log fixture data
```

## License

See [LICENSE](./LICENSE).

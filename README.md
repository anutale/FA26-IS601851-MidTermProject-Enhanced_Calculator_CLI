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
python3 -m venv .venv              # macOS/Linux
source .venv/bin/activate          # macOS/Linux
# Windows PowerShell: py -3 -m venv .venv
#                     .venv\Scripts\Activate.ps1
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
- **Memento:** snapshots of history support undo/redo.
- **Data model:** `Calculation` stores operands, operation, result, and
  timestamp, and supports serialization/deserialization.

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
├── .gitbub/
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

The checked-out workflow directory is currently spelled `.gitbub`. GitHub
Actions conventionally expects `.github/workflows`; rename the directory if you
want GitHub to discover and run that workflow automatically.

## Run the tests

Run all tests from the project root:

```bash
pytest
```

Run focused tests:

```bash
pytest tests/test_operations.py tests/test_calculation.py
```

Pytest is configured to report application coverage in the terminal and
generate an HTML report under `htmlcov/`.

## License

See [LICENSE](./LICENSE).

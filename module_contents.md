# Enhanced Calculator CLI — Project Details

## Project overview

The Enhanced Calculator CLI is an interactive Python application for performing
arithmetic operations and managing calculation history. It is the project
deliverable for the course module on object-oriented programming, design
patterns, testing, and CSV data management with pandas.

The application separates its command-line interface, calculation model,
arithmetic operations, configuration, validation, history persistence, and
error handling into modules. This makes its functionality testable and allows
new operations to be added through the operation factory.

## Project goals

- Provide a command-line read-eval-print loop (REPL) for repeated calculations.
- Support common and extended arithmetic operations using two numeric inputs.
- Validate user input and report invalid operations or operands clearly.
- Keep calculation history in memory, support undo and redo, and persist history
  to CSV.
- Demonstrate reusable object-oriented components and design patterns.
- Verify behavior with automated pytest tests.

## Features

### Arithmetic operations

Each operation accepts a first operand `a` and a second operand `b`.

| REPL command | Operation | Definition and constraints |
|---|---|---|
| `add` | Addition | `a + b` |
| `subtract` | Subtraction | `a - b` |
| `multiply` | Multiplication | `a * b` |
| `divide` | Division | `a / b`; rejects `b = 0` |
| `power` | Power | `a ** b`; negative exponents are not supported |
| `root` | Root | The `b`th root of `a`; rejects negative `a` and `b = 0` |
| `modulus` | Modulus | `a % b`; rejects `b = 0` |
| `integer_division` | Integer division | `a // b`; fractional quotient part is discarded; rejects `b = 0` |
| `percentage` | Percentage | `(a / b) * 100`; rejects `b = 0` |
| `absolute_difference` | Absolute difference | `abs(a - b)` |

Operands are converted to `Decimal` for calculation. Input validation rejects
non-numeric values and values whose absolute magnitude exceeds the configured
limit.

### REPL commands

| Command | Behavior |
|---|---|
| `help` | Display available operations and commands |
| `history` | Display calculations currently in memory |
| `clear` | Clear history and undo/redo state in memory |
| `undo` | Restore the history state before the most recent calculation |
| `redo` | Restore history to a state that was undone |
| `save` | Save history to the configured CSV file |
| `load` | Load history from the configured CSV file |
| `exit` | Save history and exit the application |

The REPL also accepts `cancel` at either operand prompt to cancel the current
calculation. Undo and redo change the in-memory history; they do not reverse
external effects such as log entries already written.

### History, persistence, and logging

Calculation history contains the operation name, both operands, result, and
timestamp. The calculator can serialize this information to CSV and reconstruct
calculations when loading history. It also exposes a pandas DataFrame view of
the current history.

The REPL registers observers to log completed calculations and to auto-save
history when auto-save is enabled. By default, data is stored under the project
root:

- `history/calculator_history.csv`
- `logs/calculator.log`

These are runtime data locations; the corresponding generated directories and
files are ignored by git.

## Design and implementation

- **Factory pattern:** `OperationFactory` maps operation names to operation
  classes and creates operation instances. The factory can also register
  additional operation classes.
- **Strategy pattern:** Each operation implements the shared `Operation`
  interface. `Calculator` holds the selected operation and invokes it for a
  calculation.
- **Observer pattern:** `HistoryObserver` defines the observer interface.
  `LoggingObserver` logs calculations, and `AutoSaveObserver` saves history
  when the configuration enables it.
- **Memento pattern:** `CalculatorMemento` captures history states used by
  `Calculator` to implement undo and redo.
- **Facade-style coordination:** `Calculator` provides the application-facing
  interface for selecting operations, validating and performing calculations,
  managing history, and saving/loading data.
- **Data model:** `Calculation` represents a calculation and supports
  serialization and reconstruction.
- **Validation and exceptions:** `InputValidator` converts inputs to
  `Decimal`; calculator-specific exception classes distinguish validation,
  operation, and configuration failures.
- **CSV data management:** pandas DataFrames are used to read and write history
  and to provide tabular access to calculations.

## Configuration

Configuration is provided through `CalculatorConfig` constructor arguments or
environment variables. A `.env` file is loaded when present. Environment
variables include:

| Variable | Default | Purpose |
|---|---|---|
| `CALCULATOR_BASE_DIR` | Project root | Base directory for application data |
| `CALCULATOR_MAX_HISTORY_SIZE` | `1000` | Maximum retained history entries |
| `CALCULATOR_AUTO_SAVE` | `true` | Enable automatic history saving (`true` or `1`) |
| `CALCULATOR_PRECISION` | `10` | Precision value retained in configuration |
| `CALCULATOR_MAX_INPUT_VALUE` | `1e999` | Maximum absolute input value |
| `CALCULATOR_DEFAULT_ENCODING` | `utf-8` | Default encoding setting |
| `CALCULATOR_HISTORY_DIR` | `<base_dir>/history` | History directory |
| `CALCULATOR_HISTORY_FILE` | `<history_dir>/calculator_history.csv` | History CSV path |
| `CALCULATOR_LOG_DIR` | `<base_dir>/logs` | Log directory |
| `CALCULATOR_LOG_FILE` | `<log_dir>/calculator.log` | Log file path |

The precision and encoding settings currently do not alter arithmetic
calculation or the pandas CSV/logging implementations.

## Project structure

```text
.
├── main.py                         # Launches the calculator REPL
├── README.md                       # User-facing setup and usage documentation
├── module_contents.md              # This project overview
├── LICENSE                         # Project license
├── pyproject.toml                  # Python project metadata and dev extras
├── requirements.txt                # Pinned runtime and development packages
├── pytest.ini                      # Pytest discovery and coverage settings
├── .gitbub/
│   └── workflows/
│       └── tests.yml               # CI test workflow file
├── app/
│   ├── calculation.py              # Calculation model and serialization
│   ├── calculator.py               # Calculator, history, persistence, undo/redo
│   ├── calculator_config.py        # Settings, paths, and config validation
│   ├── calculator_memento.py       # History snapshots for undo and redo
│   ├── calculator_repl.py          # Interactive command-line interface
│   ├── exceptions.py               # Calculator exception hierarchy
│   ├── history.py                  # Logging and auto-save observers
│   ├── input_validators.py         # Numeric input validation
│   └── operations.py               # Operation implementations and factory
├── tests/
│   ├── conftest.py                 # Shared pytest setup
│   ├── test_calculation.py
│   ├── test_calculator.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_history.py
│   ├── test_operations.py
│   └── test_validators.py
├── history/                        # Runtime CSV history (git-ignored)
├── logs/                           # Runtime log file (git-ignored)
├── test_history/                   # History test data
└── test_logs/                      # Logging test data
```

The workflow directory in this checkout is spelled `.gitbub`. GitHub Actions
normally discovers workflows under `.github/workflows`; rename `.gitbub` to
`.github` if the workflow should run automatically on GitHub.

## Setup and execution

Requirements: Python 3.10 or later and pip.

Create and activate a virtual environment, then install dependencies:

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows PowerShell
# py -3 -m venv .venv
# .venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

Run the calculator from the project root:

```bash
python main.py
```

Enter an operation command, then provide the two requested operands. Type
`help` for the available operations and commands.

## Testing

Run the complete test suite:

```bash
pytest
```

Run focused operation and calculation tests:

```bash
pytest tests/test_operations.py tests/test_calculation.py
```

Pytest is configured to measure coverage for `app/`, print a terminal report,
and generate an HTML report in `htmlcov/`. The CI workflow requests a 70%
coverage minimum. Coverage output, virtual environments, logs, and generated
history are local artifacts and should not be committed.

## Learning outcomes demonstrated

- Apply object-oriented programming concepts such as classes, inheritance,
  abstract interfaces, and encapsulation.
- Use Factory, Strategy, Observer, and Memento patterns in an application.
- Organize an application into cohesive modules and centralize error handling.
- Validate numeric input and handle invalid arithmetic cases.
- Store and retrieve structured calculation data using CSV and pandas.
- Test components and edge cases with pytest and coverage tooling.

## Course assignment context

This application addresses the enhanced calculator assignment by implementing
an interactive REPL, arithmetic operation objects, operation creation through
a factory, history observers, memento-based undo/redo, configuration through
environment variables, CSV history persistence, and a pytest test suite.
Additional operations—modulus, integer division, percentage, and absolute
difference—extend the required addition, subtraction, multiplication, division,
power, and root operations.

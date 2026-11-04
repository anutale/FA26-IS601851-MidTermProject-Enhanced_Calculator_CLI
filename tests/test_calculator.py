import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    assert calculator.undo() is True
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert len(calculator.redo_stack) == 1
    assert calculator.redo_stack[-1].history[0].result == Decimal('5')

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    assert calculator.undo() is True
    assert calculator.redo() is True
    assert len(calculator.history) == 1
    assert calculator.history[0].result == Decimal('5')
    assert len(calculator.undo_stack) == 1
    assert calculator.redo_stack == []

def test_undo_redo_multiple_calculations_preserves_each_history_state(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.set_operation(OperationFactory.create_operation('multiply'))
    calculator.perform_operation(4, 5)

    assert [entry.result for entry in calculator.history] == [
        Decimal('5'), Decimal('20')
    ]

    assert calculator.undo() is True
    assert [entry.result for entry in calculator.history] == [Decimal('5')]
    assert calculator.undo() is True
    assert calculator.history == []
    assert calculator.undo() is False

    assert calculator.redo() is True
    assert [entry.result for entry in calculator.history] == [Decimal('5')]
    assert calculator.redo() is True
    assert [entry.result for entry in calculator.history] == [
        Decimal('5'), Decimal('20')
    ]
    assert calculator.redo() is False
    assert len(calculator.undo_stack) == 2
    assert calculator.redo_stack == []

def test_new_calculation_clears_redo_history(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.perform_operation(4, 5)
    assert calculator.undo() is True
    assert len(calculator.redo_stack) == 1

    calculator.set_operation(OperationFactory.create_operation('subtract'))
    calculator.perform_operation(9, 2)

    assert [entry.result for entry in calculator.history] == [
        Decimal('5'), Decimal('7')
    ]
    assert calculator.redo_stack == []
    assert calculator.redo() is False

def test_failed_calculation_does_not_change_history_stacks(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    original_history = calculator.history.copy()
    original_undo_stack = calculator.undo_stack.copy()
    calculator.set_operation(OperationFactory.create_operation('divide'))

    with pytest.raises(ValidationError, match="Division by zero"):
        calculator.perform_operation(4, 0)

    assert calculator.history == original_history
    assert calculator.undo_stack == original_undo_stack
    assert calculator.redo_stack == []

def test_clear_history_clears_undo_and_redo_states(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    assert calculator.undo() is True
    assert calculator.redo_stack

    calculator.clear_history()

    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.undo() is False
    assert calculator.redo() is False

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")

def test_load_history_replaces_history_and_resets_memento_stacks(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    assert calculator.undo()
    calculator.set_operation(OperationFactory.create_operation('multiply'))
    calculator.perform_operation(4, 5)
    calculator.perform_operation(6, 7)
    assert calculator.undo()
    assert calculator.undo_stack
    assert calculator.redo_stack

    with patch('app.calculator.Path.exists', return_value=True), patch(
        'app.calculator.pd.read_csv',
        return_value=pd.DataFrame({
            'operation': ['Addition'],
            'operand1': ['10'],
            'operand2': ['5'],
            'result': ['15'],
            'timestamp': [datetime.datetime.now().isoformat()],
        }),
    ):
        calculator.load_history()

    assert [entry.result for entry in calculator.history] == [Decimal('15')]
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.undo() is False
    assert calculator.redo() is False

def test_load_empty_history_clears_history_and_memento_stacks(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    assert calculator.undo()

    with patch('app.calculator.Path.exists', return_value=True), patch(
        'app.calculator.pd.read_csv',
        return_value=pd.DataFrame(
            columns=['operation', 'operand1', 'operand2', 'result', 'timestamp']
        ),
    ):
        calculator.load_history()

    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
        
            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")

def test_calculator_repl_undo_redo_updates_displayed_history():
    inputs = ['clear', 'add', '2', '3', 'undo', 'history', 'redo', 'history', 'exit']
    with patch('builtins.input', side_effect=inputs), \
         patch('builtins.print') as mock_print, \
         patch('app.calculator.Calculator.save_history'):
        calculator_repl()

    mock_print.assert_any_call("Operation undone")
    mock_print.assert_any_call("Operation redone")
    mock_print.assert_any_call("No calculations in history")
    mock_print.assert_any_call("1. Addition(2, 3) = 5")

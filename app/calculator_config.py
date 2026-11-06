########################
# Calculator Config    #
########################

from dataclasses import dataclass
import codecs
from decimal import Decimal
from decimal import InvalidOperation
from pathlib import Path
import os
from typing import Optional, Union

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


def get_project_root() -> Path:
    """
    Get the project root directory.

    This function determines the root directory of the project by navigating up
    the directory hierarchy from the current file's location.

    Returns:
        Path: The root directory path of the project.
    """
    # Get the directory of the current file (app/calculator_config.py)
    current_file = Path(__file__)
    # Navigate up two levels to reach the project root (from app/calculator_config.py to project root)
    return current_file.parent.parent


# Load configuration from the project-level .env without overriding the shell.
load_dotenv(get_project_root() / ".env")


@dataclass
class CalculatorConfig:
    """
    Calculator configuration settings.

    This class manages all configuration parameters required by the calculator
    application, including directory paths, history size, auto-save preferences,
    calculation precision, maximum input values, and default encoding.

    Configuration can be set via environment variables or by passing parameters
    directly to the class constructor.
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        max_history_size: Optional[int] = None,
        auto_save: Optional[bool] = None,
        precision: Optional[int] = None,
        max_input_value: Optional[Union[int, float, Decimal]] = None,
        default_encoding: Optional[str] = None
    ):
        """
        Initialize configuration with environment variables and defaults.

        Args:
            base_dir (Optional[Path], optional): Base directory for the calculator. Defaults to None.
            max_history_size (Optional[int], optional): Maximum number of history entries. Defaults to None.
            auto_save (Optional[bool], optional): Whether to auto-save history. Defaults to None.
            precision (Optional[int], optional): Number of decimal places for calculations. Defaults to None.
            max_input_value (Optional[Number], optional): Maximum allowed input value. Defaults to None.
            default_encoding (Optional[str], optional): Default encoding for file operations. Defaults to None.
        """
        # Set base directory to project root by default
        project_root = get_project_root()
        configured_base_dir = os.getenv('CALCULATOR_BASE_DIR', str(project_root))
        self.base_dir = (
            Path(base_dir).resolve()
            if base_dir is not None
            else Path(configured_base_dir).resolve()
        )

        # Maximum history size
        self.max_history_size = (
            max_history_size if max_history_size is not None
            else self._read_integer('CALCULATOR_MAX_HISTORY_SIZE', 1000)
        )

        # Auto-save preference
        self.auto_save = (
            auto_save if auto_save is not None
            else self._read_boolean('CALCULATOR_AUTO_SAVE', True)
        )

        # Calculation precision
        self.precision = (
            precision if precision is not None
            else self._read_integer('CALCULATOR_PRECISION', 10)
        )

        # Maximum input value allowed
        try:
            self.max_input_value = Decimal(str(
                max_input_value if max_input_value is not None
                else os.getenv('CALCULATOR_MAX_INPUT_VALUE', '1e999')
            ))
        except (InvalidOperation, ValueError) as error:
            raise ConfigurationError(
                "CALCULATOR_MAX_INPUT_VALUE must be a valid number"
            ) from error

        # Default encoding for file operations
        self.default_encoding = (
            default_encoding if default_encoding is not None
            else os.getenv('CALCULATOR_DEFAULT_ENCODING', 'utf-8')
        )

    @staticmethod
    def _read_integer(name: str, default: int) -> int:
        try:
            return int(os.getenv(name, str(default)))
        except ValueError as error:
            raise ConfigurationError(f"{name} must be an integer") from error

    @staticmethod
    def _read_boolean(name: str, default: bool) -> bool:
        value = os.getenv(name, str(default)).strip().lower()
        if value in {'true', '1'}:
            return True
        if value in {'false', '0'}:
            return False
        raise ConfigurationError(f"{name} must be 'true' or 'false'")

    @property
    def log_dir(self) -> Path:
        """
        Get log directory path.

        Determines the directory path where log files will be stored.

        Returns:
            Path: The log directory path.
        """
        value = os.getenv('CALCULATOR_LOG_DIR', '').strip()
        return Path(value or self.base_dir / "logs").resolve()

    @property
    def history_dir(self) -> Path:
        """
        Get history directory path.

        Determines the directory path where calculation history files will be stored.

        Returns:
            Path: The history directory path.
        """
        value = os.getenv('CALCULATOR_HISTORY_DIR', '').strip()
        return Path(value or self.base_dir / "history").resolve()

    @property
    def history_file(self) -> Path:
        """
        Get history file path.

        Determines the file path for storing calculation history in CSV format.

        Returns:
            Path: The history file path.
        """
        value = os.getenv('CALCULATOR_HISTORY_FILE', '').strip()
        return Path(value or self.history_dir / "calculator_history.csv").resolve()

    @property
    def log_file(self) -> Path:
        """
        Get log file path.

        Determines the file path for storing log entries.

        Returns:
            Path: The log file path.
        """
        value = os.getenv('CALCULATOR_LOG_FILE', '').strip()
        return Path(value or self.log_dir / "calculator.log").resolve()

    def validate(self) -> None:
        """
        Validate configuration settings.

        Ensures that all configuration parameters meet the required criteria.
        Raises ConfigurationError if any validation fails.

        Raises:
            ConfigurationError: If any configuration parameter is invalid.
        """
        if self.max_history_size <= 0:
            raise ConfigurationError("max_history_size must be positive")
        if self.precision <= 0:
            raise ConfigurationError("precision must be positive")
        if not self.max_input_value.is_finite() or self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive")
        try:
            codecs.lookup(self.default_encoding)
        except LookupError as error:
            raise ConfigurationError(
                f"Unsupported default encoding: {self.default_encoding}"
            ) from error

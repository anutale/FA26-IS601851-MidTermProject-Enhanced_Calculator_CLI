########################
# Input Validation     #
########################

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

@dataclass
class InputValidator:
    """Validates and sanitizes calculator inputs."""
    
    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        """
        Validate and convert input to Decimal.
        
        Args:
            value: Input value to validate
            config: Calculator configuration
            
        Returns:
            Decimal: Validated and converted number
            
        Raises:
            ValidationError: If input is invalid
        """
        try:
            if isinstance(value, bool):
                raise ValidationError("Boolean values are not valid numbers")
            if isinstance(value, str):
                value = value.strip()
            number = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as e:
            raise ValidationError(f"Invalid number format: {value}") from e

        if not number.is_finite():
            raise ValidationError("Input must be a finite number")
        if abs(number) > config.max_input_value:
            raise ValidationError(
                f"Value exceeds maximum allowed: {config.max_input_value}"
            )
        return number.normalize()

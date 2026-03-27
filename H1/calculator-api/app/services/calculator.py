"""Calculator service — business logic layer.

Follows the fastapi-templates skill service pattern with class-based service
and dependency injection support.
"""

from enum import Enum


class Operation(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"


class CalculatorService:
    """Business logic for arithmetic operations."""

    def calculate(self, a: float, b: float, operation: Operation) -> float:
        """Perform an arithmetic operation.

        Raises:
            ZeroDivisionError: if operation is divide and b == 0
        """
        if operation == Operation.add:
            return a + b
        elif operation == Operation.subtract:
            return a - b
        elif operation == Operation.multiply:
            return a * b
        elif operation == Operation.divide:
            if b == 0:
                raise ZeroDivisionError("Division by zero is not allowed")
            return a / b


calculator_service = CalculatorService()


def get_calculator_service() -> CalculatorService:
    """Dependency provider for CalculatorService."""
    return calculator_service

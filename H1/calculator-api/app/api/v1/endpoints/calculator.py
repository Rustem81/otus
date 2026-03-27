"""Calculator endpoint — arithmetic operations via HTTP.

Follows the fastapi-templates skill pattern with dependency injection.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.calculator import CalculationRequest, CalculationResponse
from app.services.calculator import CalculatorService, get_calculator_service

router = APIRouter()


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_endpoint(
    request: CalculationRequest,
    service: CalculatorService = Depends(get_calculator_service),
) -> CalculationResponse:
    """Выполняет арифметическую операцию над двумя числами."""
    try:
        result = service.calculate(request.a, request.b, request.operation)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    return CalculationResponse(
        a=request.a, b=request.b, operation=request.operation, result=result,
    )

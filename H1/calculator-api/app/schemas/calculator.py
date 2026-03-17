"""Pydantic schemas for calculator request/response models."""

from pydantic import BaseModel

from app.services.calculator import Operation


class CalculationRequest(BaseModel):
    """Запрос на выполнение арифметической операции."""

    a: float
    b: float
    operation: Operation


class CalculationResponse(BaseModel):
    """Ответ с результатом арифметической операции."""

    a: float
    b: float
    operation: Operation
    result: float


class ErrorResponse(BaseModel):
    """Ответ с описанием ошибки."""

    detail: str

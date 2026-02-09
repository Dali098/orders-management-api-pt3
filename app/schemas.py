from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, validator


class OrderCreate(BaseModel):
    customer_name: str
    status: Literal["pending", "paid", "shipped", "cancelled"]
    amount: float
    currency: str
    order_date: date


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    status: str
    amount: float
    currency: str
    order_date: date

    class Config:
        from_attributes = True


class PaginatedOrderResponse(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int
    data: List[OrderResponse]


class OrderQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    status: Optional[str] = None
    minAmount: Optional[float] = None
    maxAmount: Optional[float] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    @validator("status")
    def validate_status(cls, v):
        if v is not None and v not in ["pending", "paid", "shipped", "cancelled"]:
            raise ValueError("Status must be one of: pending, paid, shipped, cancelled")
        return v

    @validator("endDate")
    def validate_date_range(cls, v, values):
        start_date = values.get("startDate")
        if v is not None and start_date is not None:
            if start_date > v:
                raise ValueError("startDate must be less than or equal to endDate")
        return v

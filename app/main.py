"""FastAPI application for Orders Management API."""
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import date
import math

from app.database import engine, get_db, Base
from app.models import Order
from app.schemas import (
    OrderCreate, 
    OrderResponse, 
    PaginatedOrderResponse,
    OrderQueryParams
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Orders Management API",
    description="API for managing orders with pagination and filtering",
    version="1.0.0"
)


@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    
    - **customer_name**: Name of the customer
    - **status**: Order status (pending, paid, shipped, cancelled)
    - **amount**: Order amount
    - **currency**: Currency code
    - **order_date**: Order date in YYYY-MM-DD format
    """
    db_order = Order(
        customer_name=order.customer_name,
        status=order.status,
        amount=order.amount,
        currency=order.currency,
        order_date=order.order_date
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/orders", response_model=PaginatedOrderResponse)
def get_orders(
    page: int = Query(1, ge=1, description="Page number (minimum 1)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    minAmount: Optional[float] = Query(None, description="Minimum order amount"),
    maxAmount: Optional[float] = Query(None, description="Maximum order amount"),
    startDate: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get orders with pagination and filtering.
    
    Returns paginated list of orders with optional filters:
    - **page**: Page number (minimum 1)
    - **limit**: Items per page (1-100)
    - **status**: Filter by order status
    - **minAmount**: Filter by minimum amount
    - **maxAmount**: Filter by maximum amount
    - **startDate**: Filter by start date
    - **endDate**: Filter by end date
    """
    # Validate parameters using Pydantic
    try:
        params = OrderQueryParams(
            page=page,
            limit=limit,
            status=status,
            minAmount=minAmount,
            maxAmount=maxAmount,
            startDate=startDate,
            endDate=endDate
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Build query with filters using SQLAlchemy ORM
    query = db.query(Order)
    
    conditions = []
    
    if params.status:
        conditions.append(Order.status == params.status)
    
    if params.minAmount is not None:
        conditions.append(Order.amount >= params.minAmount)
    
    if params.maxAmount is not None:
        conditions.append(Order.amount <= params.maxAmount)
    
    if params.startDate:
        conditions.append(Order.order_date >= params.startDate)

    if params.endDate:
        conditions.append(Order.order_date <= params.endDate)

    if conditions:
        query = query.filter(and_(*conditions))

    # Total count should not be affected by ORDER BY
    total = query.order_by(None).count()

    # Stable ordering for predictable pagination (important for 10k+ records)
    query = query.order_by(Order.order_date.desc(), Order.id.desc())

    # Calculate pagination
    total_pages = math.ceil(total / params.limit) if total > 0 else 0
    skip = (params.page - 1) * params.limit

    # Get paginated results
    orders = query.offset(skip).limit(params.limit).all()

    return PaginatedOrderResponse(
        page=params.page,
        limit=params.limit,
        total=total,
        totalPages=total_pages,
        data=orders
    )

@app.get("/")
def root():
    """Root endpoint returning API information."""
    return {
        "message": "Orders Management API",
        "version": "1.0.0",
        "endpoints": {
            "POST /orders": "Create a new order",
            "GET /orders": "Get orders with pagination and filtering"
        }
    }

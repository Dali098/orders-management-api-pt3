"""Comprehensive tests for Orders Management API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

from app.main import app
from app.database import Base, get_db
from app.models import Order

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_orders.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client and reset database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_orders():
    """Create sample orders for testing."""
    db = TestingSessionLocal()
    orders = [
        Order(
            customer_name="John Doe",
            status="pending",
            amount=100.50,
            currency="USD",
            order_date=date(2024, 1, 15)
        ),
        Order(
            customer_name="Jane Smith",
            status="paid",
            amount=250.75,
            currency="EUR",
            order_date=date(2024, 2, 10)
        ),
        Order(
            customer_name="Bob Johnson",
            status="shipped",
            amount=500.00,
            currency="USD",
            order_date=date(2024, 3, 5)
        ),
        Order(
            customer_name="Alice Williams",
            status="cancelled",
            amount=75.25,
            currency="GBP",
            order_date=date(2024, 1, 20)
        ),
        Order(
            customer_name="Charlie Brown",
            status="paid",
            amount=1000.00,
            currency="USD",
            order_date=date(2024, 2, 28)
        ),
    ]
    db.bulk_save_objects(orders)
    db.commit()
    db.close()


# Test 1: Create order with valid data
def test_create_order_success(client):
    """Test creating an order with valid data."""
    order_data = {
        "customer_name": "Test Customer",
        "status": "pending",
        "amount": 123.45,
        "currency": "USD",
        "order_date": "2024-01-15"
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Test Customer"
    assert data["status"] == "pending"
    assert data["amount"] == 123.45
    assert data["currency"] == "USD"
    assert data["order_date"] == "2024-01-15"
    assert "id" in data


# Test 2: Create order with invalid status
def test_create_order_invalid_status(client):
    """Test creating an order with invalid status."""
    order_data = {
        "customer_name": "Test Customer",
        "status": "invalid_status",
        "amount": 123.45,
        "currency": "USD",
        "order_date": "2024-01-15"
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 422  # Validation error


# Test 3: Get orders with default pagination
def test_get_orders_default_pagination(client, sample_orders):
    """Test getting orders with default pagination parameters."""
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 5
    assert data["totalPages"] == 1
    assert len(data["data"]) == 5


# Test 4: Get orders with custom pagination
def test_get_orders_custom_pagination(client, sample_orders):
    """Test getting orders with custom pagination parameters."""
    response = client.get("/orders?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] == 5
    assert data["totalPages"] == 3
    assert len(data["data"]) == 2


# Test 5: Get orders - second page
def test_get_orders_second_page(client, sample_orders):
    """Test getting the second page of orders."""
    response = client.get("/orders?page=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["limit"] == 2
    assert len(data["data"]) == 2


# Test 6: Filter orders by status
def test_filter_orders_by_status(client, sample_orders):
    """Test filtering orders by status."""
    response = client.get("/orders?status=paid")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for order in data["data"]:
        assert order["status"] == "paid"


# Test 7: Filter orders by minimum amount
def test_filter_orders_by_min_amount(client, sample_orders):
    """Test filtering orders by minimum amount."""
    response = client.get("/orders?minAmount=200")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    for order in data["data"]:
        assert order["amount"] >= 200


# Test 8: Filter orders by maximum amount
def test_filter_orders_by_max_amount(client, sample_orders):
    """Test filtering orders by maximum amount."""
    response = client.get("/orders?maxAmount=101")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for order in data["data"]:
        assert order["amount"] <= 101


# Test 9: Filter orders by amount range
def test_filter_orders_by_amount_range(client, sample_orders):
    """Test filtering orders by amount range."""
    response = client.get("/orders?minAmount=100&maxAmount=300")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for order in data["data"]:
        assert 100 <= order["amount"] <= 300


# Test 10: Filter orders by date range
def test_filter_orders_by_date_range(client, sample_orders):
    """Test filtering orders by date range."""
    response = client.get("/orders?startDate=2024-02-01&endDate=2024-02-29")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for order in data["data"]:
        order_date = date.fromisoformat(order["order_date"])
        assert date(2024, 2, 1) <= order_date <= date(2024, 2, 29)


# Test 11: Multiple filters combined
def test_multiple_filters_combined(client, sample_orders):
    """Test combining multiple filters."""
    response = client.get("/orders?status=paid&minAmount=200")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for order in data["data"]:
        assert order["status"] == "paid"
        assert order["amount"] >= 200


# Test 12: Invalid page number (less than 1)
def test_invalid_page_number(client, sample_orders):
    """Test that page number less than 1 returns error."""
    response = client.get("/orders?page=0")
    assert response.status_code == 422


# Test 13: Invalid limit (exceeds maximum)
def test_invalid_limit_exceeds_max(client, sample_orders):
    """Test that limit exceeding 100 returns error."""
    response = client.get("/orders?limit=101")
    assert response.status_code == 422


# Test 14: Invalid limit (less than 1)
def test_invalid_limit_below_min(client, sample_orders):
    """Test that limit less than 1 returns error."""
    response = client.get("/orders?limit=0")
    assert response.status_code == 422


# Test 15: Invalid date range (startDate > endDate)
def test_invalid_date_range(client, sample_orders):
    """Test that startDate > endDate returns error."""
    response = client.get("/orders?startDate=2024-03-01&endDate=2024-02-01")
    assert response.status_code == 400
    assert "startDate must be less than or equal to endDate" in response.json()["detail"]


# Test 16: Empty results with filters
def test_empty_results_with_filters(client, sample_orders):
    """Test that filters returning no results work correctly."""
    response = client.get("/orders?status=pending&minAmount=10000")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["totalPages"] == 0
    assert len(data["data"]) == 0

def test_get_orders_sorted_by_date_desc(client, sample_orders):
    """Orders should be returned in stable order: order_date desc."""
    response = client.get("/orders")
    assert response.status_code == 200
    items = response.json()["data"]

    dates = [o["order_date"] for o in items]
    assert dates == sorted(dates, reverse=True)

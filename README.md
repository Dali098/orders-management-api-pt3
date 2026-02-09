# Orders Management API

A RESTful API built with FastAPI and SQLite for managing orders with pagination and advanced filtering.
This project was developed with GitHub Copilot assistance as part of an AI-assisted development assignment.

# Quick Start

pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
API base URL: http://localhost:8000

Swagger UI: http://localhost:8000/docs

## Features

- Create orders with validation
- Paginated order listing
- Advanced filtering (status, amount range, date range)
- SQLAlchemy ORM (no raw SQL)
- SQLite database
- Database seeding with 50 sample orders
- Comprehensive automated test suite (16 test cases)
- 80%+ code coverage (~95%)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Alternative (if you prefer installing from pyproject.toml):
```bash
pip install -e .
```
Note: Editable install requires a valid pyproject.toml configuration.

## Database Setup

1. Seed the database with sample data:
```bash
python seed.py
```

This will create orders.db and populate it with 50 sample orders.

If you modify data manually via Swagger, re-run seed.py before running tests to keep them deterministic.

## Running the API

Start the development server:
```bash
uvicorn app.main:app --reload
```

The server runs at:
http://localhost:8000

Swagger UI:
http://localhost:8000/docs

## API Endpoints

***POST /orders***

Create a new order.

**Request Body:**
```json
{
  "customer_name": "John Doe",
  "status": "pending",
  "amount": 123.45,
  "currency": "USD",
  "order_date": "2026-02-09"
}
```

**Status Constraints:**
- `pending`, 
- `paid`, 
- `shipped`, 
- `cancelled`

**Response (201 Created):**
```json
{
  "id": 1,
  "customer_name": "John Doe",
  "status": "pending",
  "amount": 123.45,
  "currency": "USD",
  "order_date": "2026-02-09"
}
```

### GET /orders
Retrieve orders with pagination and filtering.

**Query Parameters:**
- `page` (integer, default: 1, min: 1): Page number
- `limit` (integer, default: 10, min: 1, max: 100): Items per page
- `status` (string, optional): Filter by status (pending, paid, shipped, cancelled)
- `minAmount` (float, optional): Minimum order amount
- `maxAmount` (float, optional): Maximum order amount
- `startDate` (date, optional): Start date in YYYY-MM-DD format
- `endDate` (date, optional): End date in YYYY-MM-DD format

**Example Request:**
```
GET /orders?page=1&limit=10&status=paid&minAmount=100&maxAmount=500&startDate=2026-01-01&endDate=2026-12-31
```

**Response (200):**
```json
{
  "page": 1,
  "limit": 10,
  "total": 50,
  "totalPages": 5,
  "data": [
    {
      "id": 3,
      "customer_name": "Alice",
      "status": "paid",
      "amount": 250.0,
      "currency": "USD",
      "order_date": "2026-02-09"
    }
  ]
}
```
## Validation Rules

## Order creation

- `customer_name`: required
- `status`: must be one of the allowed values
- `amount`: required float
- `currency`: required string
- `order_date`: ISO date (YYYY-MM-DD)

## Pagination

- `page` ≥ 1
- `limit` between 1 and 100

## Filtering

- Status validated against allowed values
- `startDate` must be ≤ `endDate`
- All filters use SQLAlchemy ORM (no string interpolation)

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest -v
```
***Current coverage***: ~95%

***All tests passing ✅***

## Test Coverage 

The test suite includes 16 test cases:

1. ✅ Create order (valid)
2. ✅ Create order (invalid status)
3. ✅ Default pagination
4. ✅ Custom pagination
5. ✅ Second page pagination
6. ✅ Filter by status
7. ✅ Filter by minimum amount
8. ✅ Filter by maximum amount
9. ✅ Filter by amount range
10. ✅ Filter by date range
11. ✅ Combined filters
12. ✅ Invalid page (<1)
13. ✅ Invalid limit (>100)
14. ✅ Invalid limit (<1)
15. ✅ Invalid date range
16. ✅ Empty result set

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and endpoints
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic schemas
│   └── database.py      # DB configuration
├── seed.py              # Seed script (50 orders)
├── test_main.py         # Pytest suite
├── requirements.txt     
├── pyproject.toml       
└── README.md           
```

## Copilot Metrics Report

See `COPILOT_REPORT.md` for detailed metrics:
- Copilot contribution percentage
- Acceptance rate (suggestions shown vs accepted)
- Estimated development time saved
- Code generated vs manually fixed
- Key learnings about Copilot strengths and limitations

## Technology Stack

- **FastAPI**
- **SQLAlchemy**
- **SQLite**
- **Pydantic**
- **Pytest**
- **Uvicorn**

## Security Note

All database access is handled via SQLAlchemy ORM.
No raw SQL or string interpolation is used, preventing SQL injection vulnerabilities.

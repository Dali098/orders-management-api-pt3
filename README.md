# Orders Management API

A RESTful API built with FastAPI and SQLite for managing orders with pagination and advanced filtering.
This project was developed as part of an AI-assisted development assignment and demonstrates scalable pagination, filtering, validation, and automated testing.

# Quick Start

pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
API base URL: http://localhost:8000
Swagger UI: http://localhost:8000/docs

## Features

- Create orders with validation
- Offset-based pagination
- Advanced filtering (status, amount range, date range)
- Stable ordering for predictable pagination
- SQLAlchemy ORM (no raw SQL)
- SQLite database
- Database seeding with 50 sample orders
- Automated test suite (17 test cases)
- 95% test coverage

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Alternative (if you prefer installing from pyproject.toml):
```bash
pip install -e .
```

## Database Setup

1. Seed the database with sample data:
```bash
python seed.py
```
This creates orders.db and populates it with 50 sample orders.
To maintain deterministic test behavior, re-run seed.py if data is modified manually.

## Running the API

Start the development server:
```bash
uvicorn app.main:app --reload
```
Application URL:
http://localhost:8000

Swagger documentation:
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

**Allowed Status Values:**
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
- `page` (integer, default: 1, minimum: 1)
- `limit` (integer, default: 10, range: 1–100)
- `status` (optional string)
- `minAmount` (optional float)
- `maxAmount` (optional float)
- `startDate` (optional date, YYYY-MM-DD)
- `endDate` (optional date, YYYY-MM-DD)

**Pagination Implementation:**
- Offset is calculated as:
  `(page - 1) * limit`
- Total record count is calculated without ORDER BY for performance efficiency.
- Stable ordering is enforced using:
  `order_date DESC, id DESC`

This approach ensures deterministic results and acceptable performance for datasets exceeding 10,000 records.

**Example Request:**
```
GET /orders?page=1&limit=10&status=paid&minAmount=100&maxAmount=500&startDate=2026-01-01&endDate=2026-12-31
```

**Example Response:**
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
- `status`: restricted to allowed values
- `amount`: required float
- `currency`: required string
- `order_date`: ISO date (YYYY-MM-DD)

## Pagination

- `page` ≥ 1
- `limit` between 1 and 100

## Filtering

- `startDate` must be less than or equal to `endDate`
- All filtering logic is implemented via SQLAlchemy ORM (no string interpolation)

## Running Tests

Run all tests:
```bash
pytest
```

Verbose execution:
```bash
pytest -v
```
***Current coverage***: ~95%

***All tests passing ✅***

## Test Coverage 

he automated test suite includes 17 test cases covering:

1. Valid order creation
2. Invalid status validation
3. Default pagination
4. Custom pagination
5. Multi-page navigation
6. Status filtering
7. Minimum amount filtering
8. Maximum amount filtering
9. Amount range filtering
10. Date range filtering
11. Combined filters
12. Invalid page parameter
13. Invalid limit (exceeds maximum)
14. Invalid limit (below minimum)
15. Invalid date range
16. Empty result sets
17. Stable ordering verification

## Project Structure

```
.
├── app/
│   ├── main.py          # API endpoints
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic schemas
│   └── database.py      # Database configuration
├── seed.py              # Database seed script
├── test_main.py         # Test suite
├── AI_REPORT_NOTES.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Technology Stack

- **FastAPI**
- **SQLAlchemy**
- **SQLite**
- **Pydantic**
- **Pytest**
- **Uvicorn**

## Security Note

All database operations are performed using SQLAlchemy ORM.
No raw SQL queries or string interpolation are used, mitigating SQL injection risks.
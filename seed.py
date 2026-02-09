"""Script to seed the database with sample orders."""
import random
from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Order


def seed_orders(num_orders: int = 50):
    """Seed the database with sample orders."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Clear existing orders
    db.query(Order).delete()
    db.commit()
    
    # Sample data
    customer_names = [
        "John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown",
        "Diana Prince", "Eve Davis", "Frank Miller", "Grace Lee", "Henry Wilson",
        "Ivy Chen", "Jack Taylor", "Kelly Anderson", "Leo Martinez", "Mia Garcia",
        "Noah Rodriguez", "Olivia Lopez", "Paul Hill", "Quinn Scott", "Rachel Green"
    ]
    
    statuses = ["pending", "paid", "shipped", "cancelled"]
    currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
    
    # Generate sample orders
    orders = []
    base_date = date.today() - timedelta(days=365)  # Start from a year ago
    
    for i in range(num_orders):
        order = Order(
            customer_name=random.choice(customer_names),
            status=random.choice(statuses),
            amount=round(random.uniform(10.0, 5000.0), 2),
            currency=random.choice(currencies),
            order_date=base_date + timedelta(days=random.randint(0, 365))
        )
        orders.append(order)
    
    db.bulk_save_objects(orders)
    db.commit()
    
    print(f"✅ Successfully seeded {num_orders} orders!")
    
    # Print summary
    for status in statuses:
        count = db.query(Order).filter(Order.status == status).count()
        print(f"  - {status}: {count}")
    
    db.close()


if __name__ == "__main__":
    seed_orders(50)

from database import SessionLocal, engine
from models import Base, Client, Invoice, LineItem
from datetime import date, datetime

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    client1 = Client(
        name="Acme Corp",
        email="acme@example.com",
        phone="9876543210",
        address="123 MG Road, Bengaluru",
        created_at=datetime.now()
    )
    client2 = Client(
        name="Bright Studios",
        email="bright@example.com",
        phone="9123456789",
        address="456 Park Street, Mumbai",
        created_at=datetime.now()
    )
    db.add_all([client1, client2])
    db.commit()
    db.refresh(client1)
    db.refresh(client2)
    print(f"Created clients: {client1.name}, {client2.name}")

    invoice1 = Invoice(
        client_id=client1.id,
        invoice_number="INV-0001",
        issue_date=date(2026, 6, 1),
        due_date=date(2026, 6, 15),
        status="sent",
        tax_percent=18,
        created_at=datetime.now()
    )
    invoice2 = Invoice(
        client_id=client2.id,
        invoice_number="INV-0002",
        issue_date=date(2026, 6, 5),
        due_date=date(2026, 6, 20),
        status="draft",
        tax_percent=18,
        created_at=datetime.now()
    )
    db.add_all([invoice1, invoice2])
    db.commit()
    db.refresh(invoice1)
    db.refresh(invoice2)
    print(f"Created invoices: {invoice1.invoice_number}, {invoice2.invoice_number}")

    db.add_all([
        LineItem(invoice_id=invoice1.id, description="Website Design", quantity=1, rate=25000),
        LineItem(invoice_id=invoice1.id, description="Logo Design", quantity=2, rate=5000),
        LineItem(invoice_id=invoice1.id, description="SEO Setup", quantity=1, rate=8000),
        LineItem(invoice_id=invoice2.id, description="Mobile App UI", quantity=1, rate=40000),
        LineItem(invoice_id=invoice2.id, description="Icon Pack", quantity=3, rate=2000),
    ])
    db.commit()
    print("Created line items!")
    print("Seed data inserted successfully!")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()

finally:
    db.close()
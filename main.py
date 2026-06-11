from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Client, Invoice, LineItem
from schemas import (
    ClientCreate, ClientOut,
    InvoiceCreate, InvoiceOut,
    LineItemCreate, LineItemOut,
    StatusUpdate
)
from typing import List
from datetime import datetime

app = FastAPI(title="Invoice Generator")


def generate_invoice_number(db: Session) -> str:
    count = db.query(Invoice).count()
    return f"INV-{str(count + 1).zfill(4)}"


@app.post("/clients", response_model=ClientOut)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.dict(), created_at=datetime.now())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@app.get("/clients", response_model=List[ClientOut])
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()


@app.post("/invoices", response_model=InvoiceOut)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == invoice.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    invoice_number = invoice.invoice_number or generate_invoice_number(db)

    db_invoice = Invoice(
        client_id=invoice.client_id,
        invoice_number=invoice_number,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        tax_percent=invoice.tax_percent,
        status="draft",
        created_at=datetime.now()
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return enrich_invoice(db_invoice)


@app.post("/invoices/{invoice_id}/line-items", response_model=LineItemOut)
def add_line_item(invoice_id: int, item: LineItemCreate, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db_item = LineItem(invoice_id=invoice_id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/invoices", response_model=List[InvoiceOut])
def get_invoices(status: str = None, db: Session = Depends(get_db)):
    query = db.query(Invoice)
    if status:
        query = query.filter(Invoice.status == status)
    invoices = query.all()
    return [enrich_invoice(inv) for inv in invoices]


@app.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return enrich_invoice(invoice)


@app.patch("/invoices/{invoice_id}/status", response_model=InvoiceOut)
def update_status(invoice_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)):
    if status_update.status not in ["draft", "sent", "paid"]:
        raise HTTPException(status_code=400, detail="Status must be draft, sent, or paid")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.status = status_update.status
    db.commit()
    db.refresh(invoice)
    return enrich_invoice(invoice)


def enrich_invoice(invoice: Invoice) -> dict:
    subtotal = sum(float(item.quantity) * float(item.rate) for item in invoice.line_items)
    tax_amount = subtotal * float(invoice.tax_percent) / 100
    total = subtotal + tax_amount

    result = InvoiceOut.from_orm(invoice)
    result.subtotal = round(subtotal, 2)
    result.tax_amount = round(tax_amount, 2)
    result.total = round(total, 2)
    return result
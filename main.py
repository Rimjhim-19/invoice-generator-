from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Client, Invoice, LineItem
from schemas import (
    ClientCreate, ClientOut,
    InvoiceCreate, InvoiceOut,
    LineItemCreate, LineItemOut,
    StatusUpdate
)
from pdf_generator import generate_invoice_pdf


app = FastAPI(title="Invoice Generator")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------- Helper functions ----------

def generate_invoice_number(db: Session) -> str:
    count = db.query(Invoice).count()
    return f"INV-{str(count + 1).zfill(4)}"


def enrich_invoice(invoice: Invoice) -> dict:
    subtotal = sum(float(item.quantity) * float(item.rate) for item in invoice.line_items)
    tax_amount = subtotal * float(invoice.tax_percent) / 100
    total = subtotal + tax_amount

    result = InvoiceOut.from_orm(invoice)
    result.subtotal = round(subtotal, 2)
    result.tax_amount = round(tax_amount, 2)
    result.total = round(total, 2)
    return result


# ---------- HTML page routes ----------

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "clients.html")


@app.get("/create-invoice")
def create_invoice_page(request: Request):
    return templates.TemplateResponse(request, "create_invoice.html")


@app.get("/invoices-page")
def invoices_page(request: Request):
    return templates.TemplateResponse(request, "invoices.html")


@app.get("/invoices-page/{invoice_id}")
def invoice_detail_page(request: Request, invoice_id: int):
    return templates.TemplateResponse(request, "invoice_detail.html", {"invoice_id": invoice_id})


# ---------- Client endpoints ----------

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


@app.delete("/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    invoice_count = db.query(Invoice).filter(Invoice.client_id == client_id).count()
    if invoice_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete client with {invoice_count} existing invoice(s). Delete those invoices first."
        )

    db.delete(client)
    db.commit()
    return {"message": "Client deleted successfully"}


# ---------- Invoice endpoints ----------

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
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.status = status_update.status
    db.commit()
    db.refresh(invoice)
    return enrich_invoice(invoice)


@app.get("/invoices/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    enriched = enrich_invoice(invoice)
    buffer = generate_invoice_pdf(enriched)

    filename = f"Invoice-{invoice.invoice_number}-{invoice.client.name.replace(' ', '-')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
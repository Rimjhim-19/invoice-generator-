from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal

class ClientCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    address: Optional[str]

    class Config:
        from_attributes = True


class LineItemCreate(BaseModel):
    description: str
    quantity: Decimal
    rate: Decimal

class LineItemOut(BaseModel):
    id: int
    description: str
    quantity: Decimal
    rate: Decimal

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    client_id: int
    invoice_number: Optional[str] = None
    issue_date: date
    due_date: date
    tax_percent: Optional[Decimal] = Decimal("0")

class InvoiceOut(BaseModel):
    id: int
    client_id: int
    invoice_number: str
    issue_date: date
    due_date: date
    status: str
    tax_percent: Decimal
    client: Optional[ClientOut]
    line_items: List[LineItemOut] = []
    subtotal: Optional[float] = 0
    tax_amount: Optional[float] = 0
    total: Optional[float] = 0

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str
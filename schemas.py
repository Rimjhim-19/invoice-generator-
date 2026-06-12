from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import date
from decimal import Decimal


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


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

    @field_validator("quantity", "rate")
    @classmethod
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Must be greater than 0")
        return v


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

    @field_validator("tax_percent")
    @classmethod
    def tax_in_range(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Tax percent must be between 0 and 100")
        return v

    @field_validator("due_date")
    @classmethod
    def due_after_issue(cls, v, info):
        issue = info.data.get("issue_date")
        if issue and v < issue:
            raise ValueError("Due date must be on or after issue date")
        return v


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

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v not in ["draft", "sent", "paid"]:
            raise ValueError("Status must be draft, sent, or paid")
        return v
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric, Date, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Client(Base):
    __tablename__ = "clients"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    email      = Column(String, nullable=False)
    phone      = Column(String)
    address    = Column(String)
    created_at = Column(DateTime)

    invoices   = relationship("Invoice", back_populates="client")


class Invoice(Base):
    __tablename__ = "invoices"

    id             = Column(Integer, primary_key=True, index=True)
    client_id      = Column(Integer, ForeignKey("clients.id"), nullable=False)
    invoice_number = Column(String, unique=True, nullable=False)
    issue_date     = Column(Date)
    due_date       = Column(Date)
    status         = Column(String, default="draft")
    tax_percent    = Column(Numeric(5, 2), default=0)
    created_at     = Column(DateTime)

    client         = relationship("Client", back_populates="invoices")
    line_items     = relationship("LineItem", back_populates="invoice")


class LineItem(Base):
    __tablename__ = "line_items"

    id          = Column(Integer, primary_key=True, index=True)
    invoice_id  = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    description = Column(String, nullable=False)
    quantity    = Column(Numeric(10, 2), nullable=False)
    rate        = Column(Numeric(10, 2), nullable=False)

    invoice     = relationship("Invoice", back_populates="line_items")
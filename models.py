from dataclasses import dataclass, field
from typing import List, Optional
from decimal import Decimal

@dataclass
class Customer:
    company_name: str
    address: str
    contact_person: str
    contact_number: str
    email: str
    
    def to_dict(self):
        return {
            "company_name": self.company_name,
            "address": self.address,
            "contact_person": self.contact_person,
            "contact_number": self.contact_number,
            "email": self.email
        }

@dataclass
class Product:
    name: str
    unit_price: float
    uom: str

@dataclass
class InvoiceItem:
    product: Product
    quantity: int
    total: Decimal = field(init=False)

    def __post_init__(self):
        self.total = self.product.price * self.quantity

@dataclass
class Invoice:
    id: Optional[int] = None
    customer: Customer = None
    items: List[InvoiceItem] = field(default_factory=list)
    total_amount: Decimal = Decimal(0)

    def add_item(self, item: InvoiceItem):
        self.items.append(item)
        self.total_amount += item.total

@dataclass
class InvoiceCreationState:
    step: str = "get_customer"
    customer: Optional[Customer] = None
    current_invoice: Invoice = field(default_factory=Invoice)
    error: Optional[str] = None
    
    
# get_customer, get_products, get_uom, get_quantity, confirm, complete
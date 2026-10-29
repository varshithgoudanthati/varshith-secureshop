from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    full_name: str
    address: str = ""
    phone: str = ""
    is_admin: bool = False
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            address=row["address"] or "",
            phone=row["phone"] or "",
            is_admin=bool(row["is_admin"]),
            created_at=str(row["created_at"]) if "created_at" in row.keys() else None
        )

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    category: str
    image_url: str
    stock: int = 0
    is_active: bool = True
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            price=float(row["price"]),
            category=row["category"],
            image_url=row["image_url"],
            stock=int(row["stock"]),
            is_active=bool(row["is_active"]),
            created_at=str(row["created_at"]) if "created_at" in row.keys() else None
        )

@dataclass
class CartItem:
    id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: str = ""
    product_price: float = 0.0
    product_image: str = ""
    subtotal: float = 0.0

@dataclass
class OrderItem:
    id: int
    order_id: int
    product_id: int
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float

@dataclass
class Order:
    id: int
    order_number: str
    user_id: int
    total_amount: float
    shipping_name: str
    shipping_address: str
    payment_status: str
    order_status: str
    created_at: Optional[str] = None
    items: Optional[List[OrderItem]] = None

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            order_number=row["order_number"],
            user_id=row["user_id"],
            total_amount=float(row["total_amount"]),
            shipping_name=row["shipping_name"],
            shipping_address=row["shipping_address"],
            payment_status=row["payment_status"],
            order_status=row["order_status"],
            created_at=str(row["created_at"]) if "created_at" in row.keys() else None
        )

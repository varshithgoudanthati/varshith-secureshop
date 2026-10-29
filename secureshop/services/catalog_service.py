from typing import List, Optional
from flask import current_app
from secureshop.database import get_db, query_db, execute_db
from secureshop.models import Product
from secureshop.services.security_logger import log_security_event

def get_all_categories() -> List[str]:
    """Fetch distinct product categories."""
    rows = query_db("SELECT DISTINCT category FROM products WHERE is_active = 1 ORDER BY category ASC")
    return [row["category"] for row in rows]

def list_products(category: Optional[str] = None, sort_by: str = "featured", include_inactive: bool = False) -> List[Product]:
    """Retrieve catalog products with optional category filtering and sorting."""
    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if not include_inactive:
        sql += " AND is_active = 1"

    if category and category != "all":
        sql += " AND category = ?"
        params.append(category)

    if sort_by == "price_asc":
        sql += " ORDER BY price ASC"
    elif sort_by == "price_desc":
        sql += " ORDER BY price DESC"
    elif sort_by == "name":
        sql += " ORDER BY name ASC"
    else:
        sql += " ORDER BY id DESC"

    rows = query_db(sql, params)
    return [Product.from_row(r) for r in rows]

def get_product_by_id(product_id: int) -> Optional[Product]:
    """Fetch a single product by its primary key ID."""
    row = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    return Product.from_row(row) if row else None

def search_products(query_text: str, is_vulnerable: bool = False) -> List[Product]:
    """Search products by name or description.
    
    Demonstrates:
    - In Vulnerable Lab Mode (is_vulnerable=True): Raw unparameterized SQL concatenation (A03 Injection).
    - In Secure Mode (is_vulnerable=False): Strict parameterized SQL queries and input sanitization.
    """
    if not query_text:
        return []

    db = get_db()

    if is_vulnerable:
        # VULNERABLE LAB IMPLEMENTATION (OWASP A03 Injection demonstration)
        # Raw string concatenation enables SQL injection payloads such as: ' OR 1=1 --
        raw_sql = f"SELECT * FROM products WHERE is_active = 1 AND name LIKE '%{query_text}%'"
        try:
            cursor = db.execute(raw_sql)
            rows = cursor.fetchall()
            return [Product.from_row(r) for r in rows]
        except Exception as e:
            # Re-raise to demonstrate error exposure in vulnerable mode
            raise e
    else:
        # SECURE REMEDIATED IMPLEMENTATION
        # Safe parameterized query preventing SQL syntax alteration
        sql = "SELECT * FROM products WHERE is_active = 1 AND (name LIKE ? OR description LIKE ?)"
        param = f"%{query_text.strip()}%"
        cursor = db.execute(sql, (param, param))
        rows = cursor.fetchall()

        # Check for potential injection attempt for telemetry without altering query safety
        suspicious_patterns = ["'", "--", "/*", "union", "select", " or "]
        if any(p in query_text.lower() for p in suspicious_patterns):
            log_security_event(
                "SQLI_SUSPECTED_INPUT",
                "INFO",
                {"query_length": len(query_text), "pattern_detected": True}
            )

        return [Product.from_row(r) for r in rows]

def create_product(name: str, description: str, price: float, category: str, image_url: str, stock: int, is_active: bool = True) -> int:
    """Create a new product (Admin function)."""
    return execute_db(
        """
        INSERT INTO products (name, description, price, category, image_url, stock, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name.strip(), description.strip(), float(price), category.strip(), image_url.strip(), int(stock), 1 if is_active else 0)
    )

def update_product(product_id: int, name: str, description: str, price: float, category: str, image_url: str, stock: int, is_active: bool):
    """Update existing product details (Admin function)."""
    execute_db(
        """
        UPDATE products 
        SET name = ?, description = ?, price = ?, category = ?, image_url = ?, stock = ?, is_active = ?
        WHERE id = ?
        """,
        (name.strip(), description.strip(), float(price), category.strip(), image_url.strip(), int(stock), 1 if is_active else 0, product_id)
    )

def delete_product(product_id: int):
    """Delete a product from the database (Admin function)."""
    execute_db("DELETE FROM products WHERE id = ?", (product_id,))

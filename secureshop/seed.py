import os
import sys
import sqlite3

# Ensure workspace root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from werkzeug.security import generate_password_hash
from secureshop.database import init_db, get_db_path

def seed_database(db_path=None):
    """Seed the database with sample products, users, and orders."""
    if db_path is None:
        db_path = get_db_path()

    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Clear existing data to ensure deterministic seeding
    cur.execute("DELETE FROM security_events")
    cur.execute("DELETE FROM login_attempts")
    cur.execute("DELETE FROM order_items")
    cur.execute("DELETE FROM orders")
    cur.execute("DELETE FROM cart_items")
    cur.execute("DELETE FROM products")
    cur.execute("DELETE FROM users")

    # 1. Seed Users
    admin_hash = generate_password_hash("AdminPass123!", method="pbkdf2:sha256")
    alice_hash = generate_password_hash("AlicePass123!", method="pbkdf2:sha256")
    bob_hash = generate_password_hash("BobPass123!", method="pbkdf2:sha256")

    cur.execute(
        """
        INSERT INTO users (id, username, email, password_hash, full_name, address, phone, is_admin)
        VALUES 
        (1, 'admin', 'admin@secureshop.local', ?, 'SecureShop Admin', '1 HQ Plaza, Suite 900', '555-0100', 1),
        (2, 'alice', 'alice@example.com', ?, 'Alice Smith', '101 Cyber Way, Tech City, CA', '555-0101', 0),
        (3, 'bob', 'bob@example.com', ?, 'Bob Jones', '404 Hacker Ave, Cyber City, NY', '555-0102', 0)
        """,
        (admin_hash, alice_hash, bob_hash)
    )

    # 2. Seed Products
    products = [
        (1, "Hardware Security Key Pro", "FIDO2 / WebAuthn dual-protocol NFC hardware security key with tamper-resistant cryptographic element.", 54.99, "Security Hardware", "/static/img/yubikey.svg", 45, 1),
        (2, "Hardware Crypto Cold Storage", "Air-gapped cryptocurrency hardware vault with secure element display and biometric verification.", 129.99, "Security Hardware", "/static/img/wallet.svg", 30, 1),
        (3, "Privacy Filter Laptop Screen 15.6\"", "Micro-louver optical privacy filter blocking side-angle visual eavesdropping.", 34.99, "Peripherals", "/static/img/privacy_screen.svg", 60, 1),
        (4, "Faraday RF Signal Shielding Bag", "Military-grade EMP and RF shielding pouch blocking WiFi, Bluetooth, GPS, and RFID signals.", 24.99, "Security Hardware", "/static/img/faraday.svg", 100, 1),
        (5, "Mechanical Developer Keyboard", "Tactile mechanical keyboard featuring hot-swappable switches and customizable per-key backlighting.", 119.50, "Peripherals", "/static/img/keyboard.svg", 25, 1),
        (6, "ANC Wireless Studio Headphones", "Active noise cancellation wireless headphones with studio-quality dynamic frequency range.", 189.99, "Electronics", "/static/img/headphones.svg", 15, 1),
        (7, "Web Application Security Handbook", "Comprehensive deep dive into modern application security, offensive techniques, and defense.", 59.99, "Books", "/static/img/book.svg", 40, 1),
        (8, "USB-C Data Blocker Connector (3-Pack)", "Hardware adapter that severs data pins to prevent juice-jacking while fast-charging devices.", 14.99, "Security Hardware", "/static/img/datablocker.svg", 150, 1),
        (9, "Ergonomic Vertical Mouse", "Precision wireless optical mouse designed to reduce wrist fatigue and repetitive strain.", 49.99, "Peripherals", "/static/img/mouse.svg", 35, 1),
        (10, "4K UHD Ultra-wide Monitor 34\"", "High-density color-accurate ultrawide display for multitasking developers and analysts.", 449.00, "Electronics", "/static/img/monitor.svg", 10, 1),
        (11, "Restricted Internal Security Token", "Internal prototype security key intended exclusively for testing and authorized staff.", 999.00, "Security Hardware", "/static/img/token.svg", 2, 0)
    ]

    cur.executemany(
        """
        INSERT INTO products (id, name, description, price, category, image_url, stock, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        products
    )

    # 3. Seed Orders and Order Items
    # Alice's Order 1 (ID 1)
    cur.execute(
        """
        INSERT INTO orders (id, order_number, user_id, total_amount, shipping_name, shipping_address, payment_status, order_status)
        VALUES (1, 'ORD-2026-ALICE1', 2, 89.98, 'Alice Smith', '101 Cyber Way, Tech City, CA', 'Simulated Paid', 'Delivered')
        """
    )
    cur.execute(
        """
        INSERT INTO order_items (id, order_id, product_id, product_name, unit_price, quantity, subtotal)
        VALUES 
        (1, 1, 1, 'Hardware Security Key Pro', 54.99, 1, 54.99),
        (2, 1, 3, 'Privacy Filter Laptop Screen 15.6\"', 34.99, 1, 34.99)
        """
    )

    # Alice's Order 2 (ID 2)
    cur.execute(
        """
        INSERT INTO orders (id, order_number, user_id, total_amount, shipping_name, shipping_address, payment_status, order_status)
        VALUES (2, 'ORD-2026-ALICE2', 2, 189.99, 'Alice Smith', '101 Cyber Way, Tech City, CA', 'Simulated Paid', 'Shipped')
        """
    )
    cur.execute(
        """
        INSERT INTO order_items (id, order_id, product_id, product_name, unit_price, quantity, subtotal)
        VALUES 
        (3, 2, 6, 'ANC Wireless Studio Headphones', 189.99, 1, 189.99)
        """
    )

    # Bob's Order 1 (ID 3)
    cur.execute(
        """
        INSERT INTO orders (id, order_number, user_id, total_amount, shipping_name, shipping_address, payment_status, order_status)
        VALUES (3, 'ORD-2026-BOB001', 3, 129.99, 'Bob Jones', '404 Hacker Ave, Cyber City, NY', 'Simulated Paid', 'Processing')
        """
    )
    cur.execute(
        """
        INSERT INTO order_items (id, order_id, product_id, product_name, unit_price, quantity, subtotal)
        VALUES 
        (4, 3, 2, 'Hardware Crypto Cold Storage', 129.99, 1, 129.99)
        """
    )

    conn.commit()
    conn.close()
    print("Database successfully seeded with users, products, and simulated orders.")

if __name__ == "__main__":
    seed_database()

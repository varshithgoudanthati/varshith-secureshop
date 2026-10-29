# SecureShop Architecture & System Design

## 1. System Overview
SecureShop is a modular, zero-dependency, local-first Python Flask e-commerce application designed specifically for academic red team / blue team security labs. It follows the **Build → Attack → Identify → Fix → Retest** pedagogical methodology.

The application features a **Dual-Profile Runtime Architecture**:
- **Secure Hardened Profile (`SECURESHOP_MODE=secure`, Default):** Enforces defense-in-depth across authentication, parameterized SQL, CSRF validation, server-side object ownership authorization, strict HTTP security headers, and secret-redacted logging.
- **Vulnerable Educational Lab Profile (`SECURESHOP_MODE=vulnerable`):** Explicit opt-in educational mode that binds strictly to `127.0.0.1` and reproduces controlled, isolated OWASP Top 10 weaknesses (A01, A03, A05, A06, A07, A09).

---

## 2. Component Architecture

```
                                  +-------------------------------------+
                                  |     Web Browser / OWASP ZAP         |
                                  +-------------------------------------+
                                                     |
                                                     v
                                  +-------------------------------------+
                                  |       Flask Security Middleware     |
                                  | - validate_csrf()                   |
                                  | - apply_security_headers()          |
                                  | - login_required / admin_required   |
                                  +-------------------------------------+
                                                     |
                         +---------------------------+---------------------------+
                         |                           |                           |
                         v                           v                           v
              +---------------------+     +---------------------+     +---------------------+
              |    Auth Routes      |     |   Product Routes    |     |   Admin & Cart      |
              |  (/login, /register)|     | (/catalog, /search) |     | (/cart, /admin)     |
              +---------------------+     +---------------------+     +---------------------+
                         |                           |                           |
                         +---------------------------+---------------------------+
                                                     |
                                                     v
                                  +-------------------------------------+
                                  |            Service Layer            |
                                  | - auth_service.py (Rate Limiting)   |
                                  | - catalog_service.py (Safe Queries) |
                                  | - order_service.py (AuthZ Checks)   |
                                  | - cart_service.py                   |
                                  | - security_logger.py (Redaction)    |
                                  +-------------------------------------+
                                                     |
                                                     v
                                  +-------------------------------------+
                                  |       SQLite Embedded Database      |
                                  |  (users, products, orders, logs)    |
                                  +-------------------------------------+
```

---

## 3. Database Schema

The SQLite schema resides in `instance/secureshop.db` with relational constraints (`PRAGMA foreign_keys = ON`):

### 3.1 `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| `username` | TEXT | UNIQUE, NOT NULL | Alphanumeric handle (3-30 chars) |
| `email` | TEXT | UNIQUE, NOT NULL | Customer contact email |
| `password_hash` | TEXT | NOT NULL | PBKDF2-SHA256 salted hash |
| `full_name` | TEXT | NOT NULL | Customer legal name |
| `address` | TEXT | DEFAULT '' | Default shipping address |
| `phone` | TEXT | DEFAULT '' | Contact telephone number |
| `is_admin` | INTEGER | NOT NULL DEFAULT 0 | 1 = Admin, 0 = Standard Customer |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

### 3.2 `products`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique product SKU |
| `name` | TEXT | NOT NULL | Title of hardware / book |
| `description` | TEXT | NOT NULL | Technical specification |
| `price` | REAL | NOT NULL | Price in USD |
| `category` | TEXT | NOT NULL | Product department |
| `image_url` | TEXT | NOT NULL | Local vector SVG asset path |
| `stock` | INTEGER | NOT NULL DEFAULT 0 | Inventory availability |
| `is_active` | INTEGER | NOT NULL DEFAULT 1 | 1 = Visible, 0 = Internal/Restricted |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date added |

### 3.3 `cart_items`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique cart line item |
| `user_id` | INTEGER | FOREIGN KEY -> users(id) | Associated customer |
| `product_id` | INTEGER | FOREIGN KEY -> products(id)| Selected product |
| `quantity` | INTEGER | NOT NULL DEFAULT 1 | Desired unit count |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Added timestamp |

### 3.4 `orders`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Order primary key |
| `order_number` | TEXT | UNIQUE, NOT NULL | Reference string (e.g. `ORD-2026-ALICE1`) |
| `user_id` | INTEGER | FOREIGN KEY -> users(id) | Owner customer account |
| `total_amount` | REAL | NOT NULL | Billed total amount |
| `shipping_name`| TEXT | NOT NULL | Recipient name |
| `shipping_address`| TEXT | NOT NULL | Destination address |
| `payment_status` | TEXT | DEFAULT 'Simulated Paid' | Payment state |
| `order_status` | TEXT | DEFAULT 'Processing' | Fulfillment status |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Order placement time |

### 3.5 `order_items`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Line item identifier |
| `order_id` | INTEGER | FOREIGN KEY -> orders(id) | Parent order reference |
| `product_id` | INTEGER | FOREIGN KEY -> products(id)| Referenced product |
| `product_name` | TEXT | NOT NULL | Snapshot of item title |
| `unit_price` | REAL | NOT NULL | Snapshot of price at purchase |
| `quantity` | INTEGER | NOT NULL | Quantity ordered |
| `subtotal` | REAL | NOT NULL | Line item subtotal |

### 3.6 `login_attempts`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Attempt counter |
| `ip_address` | TEXT | NOT NULL | Remote client IP |
| `username` | TEXT | NOT NULL | Attempted account name |
| `attempt_time` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Attempt time |
| `success` | INTEGER | NOT NULL DEFAULT 0 | 1 = Success, 0 = Failure |

### 3.7 `security_events`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Audit entry ID |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Event log timestamp |
| `event_type` | TEXT | NOT NULL | e.g. `AUTH_LOCKOUT`, `AUTHZ_DENIED_IDOR` |
| `severity` | TEXT | NOT NULL | INFO, WARNING, CRITICAL |
| `user_id` | INTEGER | NULLABLE | Authenticated user if present |
| `ip_address` | TEXT | NULLABLE | Originating IP |
| `endpoint` | TEXT | NULLABLE | Requested URI |
| `details` | TEXT | NOT NULL | Redacted JSON telemetry payload |

---

## 4. Key Design Decisions

1. **Explicit Dual-Mode Isolation:**
   Instead of scattered conditional statements throughout the presentation layer, the application uses distinct configuration classes (`SecureConfig` vs `VulnerableConfig`) and service layer gates (`is_vulnerable: bool`). This makes the code readable and easy to audit.
2. **Deterministic Seed Data:**
   The seeder creates predictable primary keys (`admin` ID 1, `alice` ID 2, `bob` ID 3; Alice orders ID 1 & 2, Bob order ID 3) so that automated tests and manual red-team verifications are 100% reproducible.
3. **Zero External API Dependencies:**
   All product images are built-in scalable vector graphics (`.svg`), fonts are accompanied by standard system-ui fallbacks, and the database is embedded SQLite. The entire application runs offline.

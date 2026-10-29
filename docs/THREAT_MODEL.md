# SecureShop Threat Model (STRIDE Methodology)

## 1. System Assets & Valuation
| Asset | Classification | Description |
|---|---|---|
| **User Authentication Credentials** | Critical | Passwords and session tokens. Compromise yields account takeover. |
| **Customer PII & Order History** | High | Customer shipping names, residential addresses, and purchase receipts. |
| **Product Inventory & Pricing** | Medium | Catalog integrity. Unauthorized changes corrupt store revenue. |
| **Administrative Operations** | Critical | Database access, user role modification, inventory deletion. |
| **Security Audit Logs** | High | Telemetry required for incident response, non-repudiation, and forensics. |

---

## 2. Trust Boundaries & Data Flow Diagram

```
[ External User / Attacker ]
           │
═══════════╪═════════════════════════════════════════════ Trust Boundary 1: Internet to Application
           │ HTTP Requests (Cookies, Forms, Query Params)
           ▼
[ Flask Application Server ]
   ├── Authentication Middleware (Session / Rate Limiter)
   ├── Security Headers Middleware (CSP, Clickjacking protection)
   └── CSRF Protection Filter
           │
═══════════╪═════════════════════════════════════════════ Trust Boundary 2: Route to Authorization Logic
           │ Authenticated Context (user_id, is_admin)
           ▼
[ Service & Data Access Layer ]
   ├── Parameterized Prepared Statements
   ├── Object Ownership Checks (order.user_id == current_user.id)
   └── Security Logger (Redaction of secrets)
           │
═══════════╪═════════════════════════════════════════════ Trust Boundary 3: Application to Database
           │ SQLite IPC / File System
           ▼
[ SQLite Database / Storage Engine ]
```

---

## 3. STRIDE Threat Analysis

### 3.1 Spoofing (Identity Deception)
- **Threat:** Automated credential stuffing or password dictionary attacks on `/login`.
- **Vulnerable Impact:** Attackers cycle common passwords until account compromise.
- **Mitigation:** In-memory and SQLite-backed rate limiting (`MAX_LOGIN_ATTEMPTS = 5` with 15-minute lockout) in `auth_service.py`. Session regeneration upon authentication prevents session fixation.

### 3.2 Tampering (Data Modification)
- **Threat:** Cross-Site Request Forgery (CSRF) on state-changing actions (`/cart/add`, `/checkout`, `/admin/products/delete`).
- **Vulnerable Impact:** Malicious third-party sites trigger unauthorized purchases or product deletions on behalf of victim.
- **Mitigation:** Cryptographically secure per-session CSRF token validation (`secrets.compare_digest`) on all POST, PUT, DELETE browser requests.

### 3.3 Repudiation (Denial of Actions)
- **Threat:** Attacker performs unauthorized administrative actions or order manipulation without logging.
- **Vulnerable Impact:** Inability to prove who executed actions or perform root-cause analysis.
- **Mitigation:** Structured security logging (`security_events` table and `security.log`) capturing event types, timestamps, user IDs, and client IP addresses.

### 3.4 Information Disclosure (Privacy Breaches)
- **Threat A (A01 IDOR):** Authenticated user alters order ID in `/orders/<id>` or profile ID in `/profile/<id>` to view another user's data.
- **Threat B (A05 Debug Leaks):** Application errors return stack traces and environment variables.
- **Mitigation A:** Server-side object ownership verification in `order_service.py`. Requests for non-owned orders return `HTTP 403 Forbidden`.
- **Mitigation B:** Flask `DEBUG=False` in secure profile. Custom sanitized 500 error handler suppressing internal tracebacks.

### 3.5 Denial of Service (Availability Loss)
- **Threat (A06 Outdated Component):** Specially crafted SQL input passed to outdated `sqlparse 0.4.3` causes catastrophic regex backtracking (CVE-2023-30608).
- **Mitigation:** Upgraded to supported release `sqlparse>=0.5.1` in `requirements-secure.txt`.

### 3.6 Elevation of Privilege (Access Escalation)
- **Threat A (Vertical):** Customer navigates to `/admin/` endpoints.
- **Threat B (A03 SQLi):** SQL injection in product search bypasses authentication or extracts hidden/restricted prototype records.
- **Mitigation A:** `@admin_required` decorator verifying `current_user.is_admin == True`. Non-admin requests return `HTTP 403 Forbidden` and log `AUTHZ_DENIED_ADMIN_ROUTE`.
- **Mitigation B:** Strict parameterized SQL queries (`cursor.execute(sql, (param, param))`) in `catalog_service.py`.

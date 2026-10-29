# SecureShop — Red Team Application Security Lab

[![Tests](https://img.shields.io/badge/pytest-40%20passed-success)](tests/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![OWASP Top 10](https://img.shields.io/badge/OWASP-Top%2010%20Lab-orange)](docs/VULNERABILITY_REGISTER.md)
[![License](https://img.shields.io/badge/License-Academic%20Lab-lightgrey)](#)

> **SecureShop** is an academic application security project built following the **Build → Attack → Identify → Fix → Retest** methodology. It features a complete, professional, runnable e-commerce web application with a switchable dual-mode configuration: an intentional, controlled **Vulnerable Lab Mode** for security assessment and a hardened **Secure Mode** implementing defense-in-depth remediations.

---

## 1. Technology Stack

- **Backend:** Python 3.11, Flask 3.0.3, Werkzeug 3.0.3, Jinja2 3.1.4
- **Frontend:** HTML5, CSS3, Vanilla CSS Design System with Glassmorphism, Bootstrap 5.3.3, Vanilla JavaScript
- **Database:** SQLite 3 (embedded, relational schema with foreign key enforcement)
- **Authentication:** Flask server-side sessions, PBKDF2-SHA256 password hashing
- **Testing:** `pytest` (40 comprehensive functional and security test cases)
- **Security Scanning:** OWASP ZAP 2.14.0 (Automation Framework, baseline scanning, Docker integration)
- **Containerization:** Multi-stage `Dockerfile`, `docker-compose.yml`

---

## 2. Pre-Seeded Local Lab Credentials

| Account Role | Username | Password | User ID | Sample Orders |
|---|---|---|---|---|
| **Administrator** | `admin` | `AdminPass123!` | `1` | All System Orders |
| **Customer 1** | `alice` | `AlicePass123!` | `2` | `ORD-2026-ALICE1`, `ORD-2026-ALICE2` |
| **Customer 2** | `bob` | `BobPass123!` | `3` | `ORD-2026-BOB001` |

*Note: All data and accounts are purely fictional for isolated local testing. Use the top banner "Demo Accounts" button on any page to one-click autofill credentials.*

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Git

### Installation Steps

1. **Clone and enter repository:**
   ```bash
   git clone <repo-url>
   cd varshith
   ```

2. **Activate the virtual environment:**
   ```powershell
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   ```
   ```bash
   # Linux / macOS / WSL:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed the SQLite database:**
   ```bash
   python secureshop/seed.py
   ```

5. **Run the Application:**

   **A. Secure Mode (Default, Production-Hardened):**
   ```bash
   python run.py --mode secure
   ```
   *Runs on `http://127.0.0.1:5000` with parameterized queries, CSRF defenses, session hardening, rate limiting, and defensive security headers.*

   **B. Vulnerable Lab Mode (Educational Testing):**
   ```bash
   python run.py --mode vulnerable
   ```
   *Strictly binds to `127.0.0.1` and displays a red top warning banner. Controlled weaknesses are active for penetration testing.*

---

## 4. Controlled Vulnerabilities & Remediation Summary

SecureShop implements **six distinct vulnerability categories** from the OWASP Top 10:

| Category | Vulnerable Implementation | Defensive Remediation | Retest Outcome |
|---|---|---|---|
| **A01: Broken Access Control** | `/orders/<id>` and `/profile/<id>` lack ownership checks (IDOR). Alice can view Bob's order #3. | Server-side ownership check: `if order.user_id != current_user.id and not current_user.is_admin: abort(403)`. | **HTTP 403 Forbidden** |
| **A03: Injection** | Raw SQL string formatting in `/search?q=...`. Payload `' OR 1=1 --` returns all records. | Parameterized SQL query: `cursor.execute("SELECT ... WHERE name LIKE ?", (param,))`. | **0 Unauthorized Records** |
| **A05: Security Misconfiguration** | Missing HTTP security headers; uncaught exceptions in debug mode leak full stack traces. | Middleware sets `X-Frame-Options: DENY`, `nosniff`, `CSP`. Sanitized 500 error handler. | **5 Headers Present & Clean 500** |
| **A07: Authentication Failures** | No login attempt throttling (brute-force allowed); session cookies lack `HttpOnly`. | 5 failed attempts trigger 15-minute account lockout. `SESSION_COOKIE_HTTPONLY=True`. | **Locked Out on 6th Attempt** |
| **A06: Outdated Components** | Outdated `sqlparse==0.4.3` vulnerable to ReDoS ([CVE-2023-30608](https://nvd.nist.gov/vuln/detail/CVE-2023-30608)). | Upgraded to supported `sqlparse 0.5.1` in `requirements-secure.txt`. | **0 Known CVEs** |
| **A09: Logging Failures** | Critical auth and access breaches dropped silently; naive logging leaks passwords. | Centralized logger writes to `security_events` table & `security.log` with automated secret scrubbing. | **Structured Logs & Passwords Redacted** |

Detailed root cause analyses and reproduction steps are documented in [`docs/VULNERABILITY_REGISTER.md`](docs/VULNERABILITY_REGISTER.md).

---

## 5. Automated Testing (pytest)

The test suite contains **40 automated tests** covering functional e-commerce flows and security regression checks:

```bash
# Execute entire test suite:
pytest -v

# Run only security tests:
pytest tests/test_security_access_control.py tests/test_security_injection.py tests/test_security_auth_hardening.py tests/test_security_misconfig_headers.py tests/test_security_csrf.py tests/test_security_logging.py -v

# Run only functional tests:
pytest tests/test_auth_functional.py tests/test_catalog_functional.py tests/test_cart_orders_functional.py tests/test_admin_functional.py -v
```

**Actual Execution Result:**
```text
============================= 40 passed in 42.12s =============================
```

---

## 6. OWASP ZAP Scanning & Reports

Automated scripts and configuration files for running DAST scans are included:

- **Scan Guide:** See [`docs/ZAP_SCAN_GUIDE.md`](docs/ZAP_SCAN_GUIDE.md)
- **Automation Framework Plan:** [`security/zap_automation_plan.yaml`](security/zap_automation_plan.yaml)
- **PowerShell Runner:** `.\scripts\run_zap_scan.ps1 -Target "http://127.0.0.1:5000" -Mode "vulnerable"`
- **Python Audit Driver:** `python scripts/zap_baseline_scan.py`
- **Docker Compose:** `docker-compose up -d secureshop zap`
- **Genuine Baseline Report:** [`security/reports/zap_baseline_scan_vulnerable.html`](security/reports/zap_baseline_scan_vulnerable.html) (6 alerts)
- **Genuine Retest Report:** [`security/reports/zap_retest_scan_secure.html`](security/reports/zap_retest_scan_secure.html) (0 alerts)

---

## 7. Repository Structure

```
secureshop/
  ├── __init__.py               # Flask application factory, error handlers, security hooks
  ├── config.py                 # SecureConfig (default) & VulnerableConfig
  ├── database.py               # SQLite connection management & relational schema DDL
  ├── models.py                 # Dataclasses for User, Product, CartItem, Order
  ├── seed.py                   # Database seeder with deterministic test accounts
  ├── routes/
  │   ├── auth.py               # Authentication, registration, profile, IDOR demo
  │   ├── products.py           # Catalog, detail views, safe/vulnerable search
  │   ├── cart.py               # Shopping cart actions, checkout simulation
  │   ├── orders.py             # Order history, receipt detail with IDOR gating
  │   ├── admin.py              # Dashboard KPIs, product management, user directory
  │   └── api.py                # Health check, lab status telemetry, error trigger
  ├── services/
  │   ├── auth_service.py       # Password hashing, rate limiting lockout logic
  │   ├── catalog_service.py    # Parameterized SQL vs raw SQL search logic
  │   ├── cart_service.py       # Cart operations, quantity updates, calculations
  │   ├── order_service.py      # Checkout simulation, server-side authorization
  │   ├── security_middleware.py# CSRF token validation, headers, @admin_required
  │   └── security_logger.py    # Structured audit logging with secret redaction
  ├── templates/                # Responsive Jinja2 templates (dark mode glassmorphism)
  └── static/                   # CSS, JavaScript, and SVG product vector assets
tests/                          # 40 automated pytest functional & security tests
scripts/                        # Automated ZAP scanner drivers & asset generator
security/
  ├── findings/                 # Machine-readable JSON records (FINDING-001 to 006)
  ├── reports/                  # ZAP baseline and retest HTML/JSON reports
  └── evidence/                 # Reproduction logs and traces
docs/
  ├── ARCHITECTURE.md           # System architecture & database schema
  ├── THREAT_MODEL.md           # STRIDE threat model & asset valuation
  ├── VULNERABILITY_REGISTER.md # Comprehensive vulnerability register
  ├── ZAP_SCAN_GUIDE.md         # OWASP ZAP setup and scanning guide
  ├── RETEST_REPORT.md          # Before-and-after retest audit report
  └── DEPENDENCY_AUDIT.md       # SCA report on sqlparse CVE-2023-30608
Dockerfile                      # Production container image definition
docker-compose.yml              # Multi-container isolated lab & ZAP network
requirements-secure.txt         # Pinned secure dependencies
requirements-vulnerable.txt     # Pinned vulnerable dependencies (sqlparse 0.4.3)
run.py                          # Application CLI entrypoint
```

---

## 8. Final Project Checklist

- [x] Dedicated Git branch created: `feature/secureshop-security-lab`
- [x] Functional e-commerce application with catalog, search, cart, checkout simulation, orders, and admin panel
- [x] 6 distinct OWASP Top 10 vulnerabilities implemented in controlled lab mode
- [x] Defense-in-depth remediations applied in secure mode (parameterized queries, CSRF, rate limiting, security headers, logging)
- [x] 40 automated pytest tests passing (100% pass rate)
- [x] OWASP ZAP automation plan, Docker Compose configuration, and scan runner scripts
- [x] Structured findings register in `security/findings/`
- [x] Complete documentation: Architecture, Threat Model, Vulnerability Register, ZAP Scan Guide, Retest Report, Dependency Audit
- [x] No real credentials, external paid services, or private API dependencies

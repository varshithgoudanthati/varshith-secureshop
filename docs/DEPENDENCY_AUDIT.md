# SecureShop Dependency Security Audit (OWASP A06)

This document provides a verified Software Composition Analysis (SCA) of the dependencies used across the **vulnerable lab profile** and the **remediated secure profile**.

---

## 1. Intentionally Outdated Component Analysis

### Component Overview
- **Package Name:** `sqlparse`
- **Installed Vulnerable Version:** `0.4.3` (Pinned in `requirements-vulnerable.txt`)
- **Remediated Version:** `0.5.1` (Pinned in `requirements-secure.txt` and `requirements.txt`)
- **Current Supported Upstream Version:** `0.5.1` / `0.6.0`

### Advisory Citations
- **CVE Identifier:** [CVE-2023-30608](https://nvd.nist.gov/vuln/detail/CVE-2023-30608)
- **GitHub Advisory Database:** [GHSA-rrm6-wvj7-cwh2](https://github.com/advisories/GHSA-rrm6-wvj7-cwh2)
- **CVSS v3.1 Base Score:** **7.5 (High)** — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

### Impact and Technical Mechanism
- **Vulnerability Type:** Regular Expression Denial of Service (ReDoS).
- **Affected Version Range:** `sqlparse < 0.4.4`.
- **Root Cause:** When `sqlparse.parse()` evaluates an unclosed comment or an excessively nested SQL statement (such as recursion depth in recursive CTEs or unclosed multi-line comments `/*`), the regular expression in `sqlparse/keywords.py` and `sqlparse/lexer.py` suffers from catastrophic backtracking.
- **Exploitation Impact:** Processing a single payload can consume 100% CPU on the worker thread for tens of seconds, causing thread pool starvation and full Denial of Service (DoS) for all legitimate users.

---

## 2. Dependency Profile Comparison

### Vulnerable Profile (`requirements-vulnerable.txt`)
```text
Flask==3.0.3
Werkzeug==3.0.3
Jinja2==3.1.4
sqlparse==0.4.3     <-- Vulnerable to CVE-2023-30608 (ReDoS)
requests==2.32.3
pytest==8.2.2
```

### Remediated Profile (`requirements-secure.txt` / `requirements.txt`)
```text
Flask==3.0.3
Werkzeug==3.0.3
Jinja2==3.1.4
sqlparse==0.5.1     <-- Patched upstream release (CVE resolved)
requests==2.32.3
pytest==8.2.2
```

---

## 3. Dependency Audit Execution & Verification

### Running Automated Audit
To audit the dependencies locally using `pip-audit`:

```bash
# In the virtual environment:
pip install pip-audit

# Audit vulnerable profile:
pip-audit -r requirements-vulnerable.txt
```
**Expected Output (Vulnerable Mode):**
```text
Found 1 known vulnerability in 1 package
Name     Version ID             Fix Versions
-------- ------- -------------- ------------
sqlparse 0.4.3   CVE-2023-30608 0.4.4, 0.5.0
```

```bash
# Audit remediated secure profile:
pip-audit -r requirements-secure.txt
```
**Expected Output (Secure Mode):**
```text
No known vulnerabilities found
```

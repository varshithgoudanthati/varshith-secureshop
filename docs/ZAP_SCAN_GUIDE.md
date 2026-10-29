# OWASP ZAP Scanning Guide for SecureShop

This guide provides step-by-step instructions for running passive and active security scans against SecureShop using **OWASP Zed Attack Proxy (ZAP)**.

---

## 1. Scope & Safety Guidelines
> **IMPORTANT:** All security scans must target strictly the local, authorized SecureShop instance (`http://127.0.0.1:5000` or local container hostname). Do not point ZAP at public domains, cloud environments, or university networks.

- **Primary Target URL:** `http://127.0.0.1:5000/`
- **Container Target URL:** `http://app.secureshop.local:5000/` (via Docker Compose network)
- **Scanning Scope:** Strict inclusion of `\Qhttp://127.0.0.1:5000/\E.*`

---

## 2. Scanning Options

### Option A: Automated Scan Script (PowerShell / Bash)
The repository includes automated execution scripts in `scripts/`:

```powershell
# Windows PowerShell:
.\scripts\run_zap_scan.ps1 -Target "http://127.0.0.1:5000" -Mode "vulnerable"
.\scripts\run_zap_scan.ps1 -Target "http://127.0.0.1:5000" -Mode "secure"
```

```bash
# Linux / macOS / WSL:
chmod +x scripts/run_zap_scan.sh
./scripts/run_zap_scan.sh http://127.0.0.1:5000 vulnerable
./scripts/run_zap_scan.sh http://127.0.0.1:5000 secure
```

---

### Option B: Docker Containerized Scan
If Docker is installed and running, use the official OWASP ZAP container:

```bash
# 1. Start SecureShop in one terminal:
python run.py --mode vulnerable

# 2. Run ZAP Baseline scan from repository root:
docker run --rm -v "${PWD}/security/reports:/zap/wrk/:rw" --network host zaproxy/zap-stable \
    zap-baseline.py -t http://127.0.0.1:5000 -r zap_baseline_scan_vulnerable.html -J zap_baseline_scan_vulnerable.json -I
```

---

### Option C: ZAP Desktop GUI (Step-by-Step)
If using the ZAP Desktop application:

1. **Start SecureShop:**
   ```bash
   python run.py --mode vulnerable
   ```
2. **Launch OWASP ZAP Desktop.**
3. **Configure Target Context:**
   - Right-click in Sites tab -> *New Context*.
   - Context Name: `SecureShop-Local`.
   - In *Include in Context*, add: `\Qhttp://127.0.0.1:5000\E.*`.
   - In *Exclude from Context*, add: `\Qhttp://127.0.0.1:5000/logout\E`.
4. **Configure Authentication (Authenticated Scanning):**
   - In Context options -> *Authentication*:
     - Select **Form-based Authentication**.
     - Login form target URL: `http://127.0.0.1:5000/login`.
     - Request body: `username={%username%}&password={%password%}&csrf_token={%csrf_token%}`.
   - In *Users* tab:
     - Add user: `Alice` (Username: `alice`, Password: `AlicePass123!`).
5. **Run Baseline Spider:**
   - Right-click Context -> *Attack* -> *Spider*.
   - Select User: `Alice`. Click *Start Scan*.
6. **Run Active Scan:**
   - Right-click Context -> *Attack* -> *Active Scan*.
   - Focus policy on Injection and Information Disclosure rules.
7. **Export Reports:**
   - Navigate to *Report* -> *Generate Report...*
   - Choose *Traditional HTML* and *Traditional JSON*.
   - Save output to `security/reports/`.

---

### Option D: ZAP Automation Framework (AF)
Run the pre-configured automation plan:
```bash
zap.bat -cmd -autorun security/zap_automation_plan.yaml
```

---

## 3. Interpreting Findings & Detection Capabilities

| Vulnerability | Automatically Flagged by ZAP? | Detection Mechanism | Notes |
|---|---|---|---|
| **A05: Security Misconfiguration** | **YES (Direct)** | Passive Scan Rules: `10020`, `10038`, `10021` | ZAP immediately flags missing headers on all HTTP responses. |
| **A05: Debug / Stack Trace Leak** | **YES (Direct)** | Active Scan Rule: `10036` | Uncaught exceptions returning stack traces trigger information disclosure alerts. |
| **A07: Cookie Flags (HttpOnly)** | **YES (Direct)** | Passive Scan Rule: `10010` | ZAP checks `Set-Cookie` directives for missing security attributes. |
| **A03: SQL Injection** | **YES (Conditional)** | Active Scan Rule: `40018` | ZAP active scanner fuzzes `q` parameter with SQL tautology payloads. |
| **A01: Broken Access Control (IDOR)** | **PARTIAL / MANUAL** | Requires multi-user context | Generic DAST scanners cannot determine whether Alice is allowed to see Bob's order without custom access rules. Verified via automated pytest suite. |
| **A06: Outdated Components** | **NO (SCA Required)** | Software Composition Analysis | DAST scanners cannot reliably inspect server-side Python libraries. Requires `pip-audit` / `safety`. |

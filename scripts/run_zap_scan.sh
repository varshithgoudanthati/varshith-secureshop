#!/usr/bin/env bash
# SecureShop OWASP ZAP Execution Script (Bash / Linux / macOS / WSL)
set -e

TARGET="${1:-http://127.0.0.1:5000}"
MODE="${2:-vulnerable}"
REPORT_DIR="security/reports"

mkdir -p "$REPORT_DIR"

echo "=========================================================="
echo "  SecureShop — OWASP ZAP Automated DAST Scanner"
echo "  Target: $TARGET"
echo "  Lab Mode: $MODE"
echo "=========================================================="

if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "[+] Running OWASP ZAP container..."
    docker run --rm -v "$(pwd)/$REPORT_DIR:/zap/wrk/:rw" --network host zaproxy/zap-stable \
        zap-baseline.py -t "$TARGET" -r "zap_baseline_${MODE}.html" -J "zap_baseline_${MODE}.json" -I
    echo "[✓] Scan completed. Reports saved in $REPORT_DIR"
elif command -v zap.sh &> /dev/null; then
    echo "[+] Running local ZAP CLI via zap.sh..."
    zap.sh -cmd -autorun security/zap_automation_plan.yaml
else
    echo "[!] Docker daemon or zap.sh not detected."
    echo "    Please start Docker or ZAP desktop and re-run."
fi

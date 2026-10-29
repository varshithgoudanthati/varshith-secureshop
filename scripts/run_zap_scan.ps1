# SecureShop OWASP ZAP Execution Script (PowerShell)
# Usage:
#   .\scripts\run_zap_scan.ps1 -Target "http://127.0.0.1:5000" -Mode "vulnerable"
#   .\scripts\run_zap_scan.ps1 -Target "http://127.0.0.1:5000" -Mode "secure"

param (
    [string]$Target = "http://127.0.0.1:5000",
    [string]$Mode = "vulnerable",
    [string]$ReportDir = "security\reports"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  SecureShop — OWASP ZAP Automated DAST Scanner" -ForegroundColor Cyan
Write-Host "  Target: $Target" -ForegroundColor Yellow
Write-Host "  Lab Mode: $Mode" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}

$HtmlReport = "$ReportDir\zap_baseline_${Mode}.html"
$JsonReport = "$ReportDir\zap_baseline_${Mode}.json"

# Check if Docker is running
$dockerRunning = $false
try {
    $info = docker info 2>$null
    if ($LASTEXITCODE -eq 0) { $dockerRunning = $true }
} catch {
    $dockerRunning = $false
}

if ($dockerRunning) {
    Write-Host "[+] Docker daemon detected. Launching official OWASP ZAP container..." -ForegroundColor Green
    $wrkDir = (Get-Item .).FullName + "\security\reports"
    docker run --rm -v "${wrkDir}:/zap/wrk/:rw" --network host zaproxy/zap-stable `
        zap-baseline.py -t $Target -r "zap_baseline_${Mode}.html" -J "zap_baseline_${Mode}.json" -I
    Write-Host "[✓] ZAP container scan finished. Reports saved to $ReportDir" -ForegroundColor Green
} else {
    Write-Host "[!] Docker daemon is not active. Checking local ZAP executable..." -ForegroundColor Yellow
    $zapCmd = Get-Command "zap.bat" -ErrorAction SilentlyContinue
    if ($zapCmd) {
        Write-Host "[+] Local ZAP installation found at $($zapCmd.Source)" -ForegroundColor Green
        & zap.bat -cmd -autorun security\zap_automation_plan.yaml
    } else {
        Write-Host "[!] OWASP ZAP is not installed locally and Docker daemon is offline." -ForegroundColor Yellow
        Write-Host "    To execute live scans when Docker or ZAP is launched:" -ForegroundColor White
        Write-Host "    1. Start Docker Desktop" -ForegroundColor Gray
        Write-Host "    2. Execute: docker-compose up -d secureshop zap" -ForegroundColor Gray
        Write-Host "    3. Or use the Python automation driver: python scripts\zap_baseline_scan.py" -ForegroundColor Gray
    }
}

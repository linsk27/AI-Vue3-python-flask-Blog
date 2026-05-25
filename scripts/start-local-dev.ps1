param(
    [int]$BackendPort = 5100,
    [int]$FrontPort = 8080
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $Root "backend"
$FrontDir = Join-Path $Root "front"
$LogDir = Join-Path $Root ".codex-logs"

function Test-PortFree {
    param([int]$Port)
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return -not $listener
}

function Find-FreePort {
    param([int]$StartPort)
    $port = $StartPort
    while (-not (Test-PortFree -Port $port)) {
        $port += 1
        if ($port -gt ($StartPort + 99)) {
            throw "No free port found from $StartPort to $($StartPort + 99)."
        }
    }
    return $port
}

if (-not (Test-Path $BackendDir)) {
    throw "Backend directory not found: $BackendDir"
}

if (-not (Test-Path $FrontDir)) {
    throw "Front directory not found: $FrontDir"
}

if (-not (Test-PortFree -Port $FrontPort)) {
    throw "Front port $FrontPort is already in use. Stop the existing frontend process or pass -FrontPort <port>."
}

$BackendPort = Find-FreePort -StartPort $BackendPort
$PythonPath = Join-Path $BackendDir ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) {
    $PythonPath = "python"
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$backendOutLog = Join-Path $LogDir "backend-local-dev.out.log"
$backendErrLog = Join-Path $LogDir "backend-local-dev.err.log"
$frontOutLog = Join-Path $LogDir "front-local-dev.out.log"
$frontErrLog = Join-Path $LogDir "front-local-dev.err.log"
$backendCommand = "set PORT=$BackendPort&& `"$PythonPath`" app.py"
$frontCommand = "set VITE_PROXY_TARGET=http://127.0.0.1:$BackendPort&& npm run dev -- --host 0.0.0.0 --port $FrontPort --strictPort"

Start-Process -FilePath "cmd.exe" `
    -ArgumentList @("/c", $backendCommand) `
    -WorkingDirectory $BackendDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $backendOutLog `
    -RedirectStandardError $backendErrLog

Start-Sleep -Seconds 2

Start-Process -FilePath "cmd.exe" `
    -ArgumentList @("/c", $frontCommand) `
    -WorkingDirectory $FrontDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $frontOutLog `
    -RedirectStandardError $frontErrLog

Write-Host "Zhijing local dev started."
Write-Host "Frontend: http://127.0.0.1:$FrontPort"
Write-Host "Backend:  http://127.0.0.1:$BackendPort"
Write-Host "Logs:     $LogDir"

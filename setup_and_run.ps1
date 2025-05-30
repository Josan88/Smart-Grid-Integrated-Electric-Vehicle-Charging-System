param([switch]$SkipInstall, [switch]$QuickStart, [string]$Port = "5000", [switch]$Help)

function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }

if ($Help) {
    Write-Host "Smart Grid-Integrated EV Charging System Setup Script"
    Write-Host "Usage: .\setup_and_run.ps1 [OPTIONS]"
    Write-Host "-SkipInstall    Skip Python package installation"
    Write-Host "-QuickStart     Skip dependency checks and start immediately"
    Write-Host "-Port <number>  Specify port number (default: 5000)"
    Write-Host "-Help           Show this help message"
    exit 0
}

Write-Host "Smart Grid-Integrated EV Charging System" -ForegroundColor Magenta
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Info "Working directory: $ScriptDir"

function Test-Command {
    param($Command)
    try { Get-Command $Command -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

function Test-PortAvailable {
    param($Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

function Get-AvailablePort {
    param($StartPort = 5000)
    $currentPort = $StartPort
    while ($currentPort -lt ($StartPort + 100)) {
        if (Test-PortAvailable $currentPort) {
            return $currentPort
        }
        $currentPort++
    }
    throw "No available ports found in range $StartPort to $($StartPort + 99)"
}

function Test-PythonVersion {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]; $minor = [int]$matches[2]
            if ($major -eq 3 -and $minor -ge 9) {
                Write-Success "Python $pythonVersion detected"; return $true
            } else {
                Write-Error "Python 3.9+ required, found $pythonVersion"; return $false
            }
        } else {
            Write-Error "Could not determine Python version"; return $false
        }
    } catch {
        Write-Error "Python not found in PATH"; return $false
    }
}

function Start-Application {
    param($Port)
    Write-Info "Starting Smart Grid EV Charging System on port $Port..."
    $env:FLASK_APP = "app.py"
    try {
        Write-Success "Application starting..."
        Start-Job -ScriptBlock { Start-Sleep 3; Start-Process "http://localhost:$using:Port" } | Out-Null
        python app.py --port $Port
    } catch {
        Write-Error "Failed to start application: $_"
    }
}

Write-Info "Performing system checks..."

# Check port availability
$requestedPort = [int]$Port
if (-not (Test-PortAvailable $requestedPort)) {
    Write-Warning "Port $requestedPort is not available"
    try {
        $availablePort = Get-AvailablePort $requestedPort
        Write-Info "Found available port: $availablePort"
        $Port = $availablePort.ToString()
    } catch {
        Write-Error "Could not find an available port starting from $requestedPort"
        exit 1
    }
} else {
    Write-Success "Port $requestedPort is available"
}

if (Test-PythonVersion) {
    if (-not $SkipInstall) {
        Write-Info "Installing dependencies..."
        python -m pip install -r requirements.txt
    }
    Write-Success "Setup completed successfully!"
    Start-Application $Port
} else {
    Write-Error "Python check failed"
}

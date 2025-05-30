param([switch]$SkipInstall, [switch]$QuickStart, [string]$Port = "5000", [switch]$Help, [switch]$UseVenv, [string]$VenvName = ".venv")

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
    Write-Host "-UseVenv        Create and use a Python virtual environment"
    Write-Host "-VenvName       Name of virtual environment directory (default: .venv)"
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
                Write-Success "Python $pythonVersion detected"
                
                # Check for Python 3.12+ and eventlet compatibility
                if ($major -eq 3 -and $minor -ge 12) {
                    Write-Warning "Python 3.12+ detected. Will ensure eventlet compatibility."
                    $script:needsEventletFix = $true
                }
                
                return $true
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

function Create-VirtualEnvironment {
    param($VenvName)
    
    Write-Info "Creating virtual environment: $VenvName"
    
    if (Test-Path $VenvName) {
        Write-Warning "Virtual environment '$VenvName' already exists"
        return $true
    }
    
    try {
        python -m venv $VenvName
        if (Test-Path "$VenvName\Scripts\activate.ps1") {
            Write-Success "Virtual environment '$VenvName' created successfully"
            return $true
        } else {
            Write-Error "Failed to create virtual environment"
            return $false
        }
    } catch {
        Write-Error "Error creating virtual environment: $_"
        return $false
    }
}

function Activate-VirtualEnvironment {
    param($VenvName)
    
    $activateScript = "$VenvName\Scripts\activate.ps1"
    
    if (-not (Test-Path $activateScript)) {
        Write-Error "Virtual environment activation script not found: $activateScript"
        return $false
    }
    
    try {
        Write-Info "Activating virtual environment: $VenvName"
        & $activateScript
        
        # Verify activation by checking if python executable is in venv
        $pythonPath = (Get-Command python).Source
        if ($pythonPath -like "*$VenvName*") {
            Write-Success "Virtual environment activated successfully"
            return $true
        } else {
            Write-Warning "Virtual environment may not be properly activated"
            return $true  # Continue anyway
        }
    } catch {
        Write-Error "Error activating virtual environment: $_"
        return $false
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

# Initialize global variables
$script:needsEventletFix = $false

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
    # Handle virtual environment setup
    if ($UseVenv) {
        if (-not (Create-VirtualEnvironment $VenvName)) {
            Write-Error "Failed to create virtual environment"
            exit 1
        }
        
        if (-not (Activate-VirtualEnvironment $VenvName)) {
            Write-Error "Failed to activate virtual environment"
            exit 1
        }
    }
    
    if (-not $SkipInstall) {
        Write-Info "Installing dependencies..."
        if ($UseVenv) {
            Write-Info "Installing packages in virtual environment: $VenvName"
        }
        python -m pip install --upgrade pip
        
        # Handle eventlet compatibility for Python 3.12+
        if ($script:needsEventletFix) {
            Write-Info "Fixing eventlet compatibility for Python 3.12+..."
            python -m pip install "eventlet>=0.36.1"
        }
        
        python -m pip install -r requirements.txt
    }
    Write-Success "Setup completed successfully!"
    Start-Application $Port
} else {
    Write-Error "Python check failed"
}

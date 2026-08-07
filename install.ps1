# ──────────────────────────────────────────────────────────────────────────────
# Plan-It — Windows Install Script (PowerShell)
#
# Supports: Windows 10+, Windows Server 2019+
#
# Usage:
#   Invoke-WebRequest -Uri https://raw.githubusercontent.com/jssturm/Plan-It/main/install.ps1 -OutFile install.ps1
#   .\install.ps1              — interactive install
#   .\install.ps1 -Quick       — non-interactive with defaults
#   .\install.ps1 -Force       — force re-install even if already configured
#   .\install.ps1 -FromSource  — install from local source instead of PyPI
#   .\install.ps1 -DryRun      — validate environment without installing
#
# What this does:
#   1. Validates Python 3.12+ and pip
#   2. Creates a virtual environment in %LOCALAPPDATA%\plan-it\venv
#   3. Installs the plan-it package (PyPI with GitHub fallback)
#   4. Bootstraps .env configuration
#   5. Registers 'plan-it' on PATH
#   6. Optionally sets up a Windows scheduled task for auto-start
# ──────────────────────────────────────────────────────────────────────────────

param(
    [switch]$Quick,
    [switch]$Force,
    [switch]$FromSource,
    [switch]$DryRun,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# ── Helpers ──────────────────────────────────────────────────────────────────
function Write-Plan-ItInfo  { Write-Host "[plan-it] $args" -ForegroundColor Green }
function Write-Plan-ItWarn  { Write-Host "[plan-it] $args" -ForegroundColor Yellow }
function Write-Plan-ItError { Write-Host "[plan-it] $args" -ForegroundColor Red }
function Write-Plan-ItStep  { Write-Host "-> $args" -ForegroundColor Cyan }
function Write-Plan-ItBanner { Write-Host ""; Write-Host $args -ForegroundColor White }
function Fail                  { Write-Plan-ItError $args[0]; exit 1 }

# ── Globals ──────────────────────────────────────────────────────────────────
$ScriptDir       = Split-Path -Parent $MyInvocation.MyCommand.Path
$SCRIPT_VERSION  = "0.3.0"
$GitHubRepo      = "jssturm/Plan-It"
$GitHubTarball   = "https://github.com/$GitHubRepo/archive/refs/heads/main.tar.gz"
$LocalAppData    = [Environment]::GetFolderPath("LocalApplicationData")
$VenDir          = Join-Path $LocalAppData "plan-it\venv"
$ConfigDir       = Join-Path $LocalAppData "plan-it\config"
$InstallMarker   = Join-Path $ConfigDir ".installed"
$MaxRetries      = 3

# ── Help ─────────────────────────────────────────────────────────────────────
if ($Help) {
    Write-Host @"
Usage: .\install.ps1 [OPTIONS]

Options:
  -Quick        Non-interactive install with defaults
  -Force        Force re-install even if already configured
  -FromSource   Install from local source instead of PyPI
  -DryRun       Validate environment without installing
  -Help         Show this help message
"@
    exit 0
}

# ── Network retry helper ─────────────────────────────────────────────────────
function Invoke-WithRetry {
    param([string]$Url, [string]$OutFile, [scriptblock]$Script)
    $attempt = 1; $delay = 2
    while ($attempt -le $MaxRetries) {
        try {
            if ($Script) { & $Script; return }
            if ($OutFile) {
                curl.exe -fsSL --connect-timeout 15 --max-time 60 "$Url" -o "$OutFile" 2>$null
            } else {
                curl.exe -fsSL --connect-timeout 15 --max-time 60 "$Url" 2>$null
            }
            if ($LASTEXITCODE -eq 0) { return }
        } catch {}
        Write-Plan-ItWarn "  Attempt $attempt/$MaxRetries failed — retrying in ${delay}s..."
        Start-Sleep -Seconds $delay
        $delay = $delay * 2
        $attempt++
    }
    throw "Operation failed after $MaxRetries attempts."
}

# ── OS Detection ─────────────────────────────────────────────────────────────
function Detect-OS {
    $ver = [Environment]::OSVersion.Version
    $isWin10 = $ver.Major -ge 10
    $arch    = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "x86" }
    Write-Plan-ItInfo "Detected: Windows $($ver.Major).$($ver.Minor) ($arch)"
    if (-not $isWin10) {
        Write-Plan-ItWarn "Windows 10+ recommended. Some features may not work."
    }
}

# ── Validate Environment ─────────────────────────────────────────────────────
function Validate-Env {
    Write-Plan-ItStep "Validating environment..."

    # Python 3.12+
    $pythonCmd = $null
    foreach ($cmd in @("python3", "python")) {
        try {
            $ver = & $cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            $parts = $ver.Split(".")
            if ([int]$parts[0] -ge 3 -and [int]$parts[1] -ge 12) { $pythonCmd = $cmd; break }
        } catch {}
    }

    if (-not $pythonCmd) { Fail "Python 3.12+ is required but was not found." }
    $pyVersion = & $pythonCmd --version 2>&1
    Write-Plan-ItInfo "  OK $pyVersion"

    # pip
    try {
        & $pythonCmd -m pip --version 2>&1 | Out-Null
        Write-Plan-ItInfo "  OK pip found"
    } catch {
        Fail "pip not found. Run: $pythonCmd -m ensurepip --upgrade"
    }

    # curl (for GitHub fallback)
    try {
        curl.exe --version 2>$null | Out-Null
        Write-Plan-ItInfo "  OK curl available"
    } catch {
        Write-Plan-ItWarn "  WARNING curl not found — PyPI install will work, but GitHub fallback won't"
    }

    # Disk space (at least 200 MB free)
    try {
        $drive = (Get-Item $env:USERPROFILE).PSDrive
        $freeMB = [math]::Round($drive.Free / 1MB)
        if ($freeMB -lt 200) {
            Write-Plan-ItWarn "  WARNING Less than 200 MB free disk space ($freeMB MB). Installation may fail."
        } else {
            Write-Plan-ItInfo "  OK Disk space: ~$freeMB MB free"
        }
    } catch {}

    # winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Plan-ItInfo "  OK winget available"
    }

    $script:PythonCmd = $pythonCmd
}

# ── Virtual Environment ──────────────────────────────────────────────────────
function Setup-Venv {
    if ($Force -and (Test-Path $VenDir)) {
        Write-Plan-ItStep "Removing existing virtual environment (-Force)..."
        Remove-Item -Recurse -Force $VenDir
    }

    if ((Test-Path $VenDir) -and (Test-Path (Join-Path $VenDir "Scripts\activate.ps1"))) {
        Write-Plan-ItInfo "  OK Virtual environment exists: $VenDir"
    } else {
        Write-Plan-ItStep "Creating virtual environment at $VenDir..."
        & $PythonCmd -m venv $VenDir
        if ($LASTEXITCODE -ne 0) { Fail "Failed to create virtual environment." }
        Write-Plan-ItInfo "  OK Virtual environment created"
    }

    $activateScript = Join-Path $VenDir "Scripts\Activate.ps1"
    . $activateScript
    Write-Plan-ItInfo "  OK Activated $(python --version)"

    # Upgrade pip
    pip install --upgrade pip --quiet 2>$null
}

# ── Install Package ──────────────────────────────────────────────────────────
function Install-Package {
    Write-Plan-ItStep "Installing plan-it v$SCRIPT_VERSION..."

    $installed = $false

    if ($FromSource) {
        Write-Plan-ItInfo "  Installing from local source: $ScriptDir"
        pip install $ScriptDir --quiet
        if ($LASTEXITCODE -ne 0) { Fail "Local source install failed." }
        $installed = $true
    }
    else {
        # Primary: PyPI
        Write-Plan-ItInfo "  Installing from PyPI..."
        try {
            pip install "plan-it>=$SCRIPT_VERSION" --quiet 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Plan-ItInfo "  OK Installed via PyPI"
                $installed = $true
            }
        } catch {}

        if (-not $installed) {
            Write-Plan-ItWarn "  PyPI install failed — falling back to GitHub source..."

            # Fallback 1: local source
            if (Test-Path (Join-Path $ScriptDir "pyproject.toml")) {
                Write-Plan-ItInfo "  Installing from local source: $ScriptDir"
                pip install $ScriptDir --quiet
                if ($LASTEXITCODE -ne 0) { Fail "Local source install failed." }
                $installed = $true
            }
            else {
                # Fallback 2: download from GitHub
                try { curl.exe --version 2>$null | Out-Null } catch { Fail "PyPI install failed and curl is not available." }
                $tempDir = Join-Path $env:TEMP "plan-it-sdk-$([Guid]::NewGuid().ToString().Substring(0,8))"
                New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
                try {
                    $tarball = Join-Path $tempDir "plan-it.tar.gz"
                    Write-Plan-ItInfo "  Downloading from GitHub..."
                    Invoke-WithRetry -Url $GitHubTarball -OutFile $tarball
                    Write-Plan-ItInfo "  Extracting..."
                    tar -xzf $tarball -C $tempDir 2>$null
                    if ($LASTEXITCODE -ne 0) { Fail "Could not extract tarball." }
                    # Find the extracted directory
                    $extracted = Get-ChildItem $tempDir -Directory | Select-Object -First 1
                    if (-not $extracted) { Fail "Could not locate extracted directory." }
                    Write-Plan-ItInfo "  Installing from GitHub source..."
                    pip install $extracted.FullName --quiet
                    if ($LASTEXITCODE -ne 0) { Fail "GitHub source install failed." }
                    $installed = $true
                }
                finally {
                    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
                }
            }
        }
    }

    if (-not $installed) { Fail "Installation failed through all available paths." }

    # Verify CLI
    if (Get-Command plan-it -ErrorAction SilentlyContinue) {
        Write-Plan-ItInfo "  OK plan-it CLI: $(Get-Command plan-it | Select-Object -ExpandProperty Source)"
    } elseif (Test-Path (Join-Path $VenDir "Scripts\plan-it.exe")) {
        Write-Plan-ItInfo "  OK plan-it CLI at: $VenDir\Scripts\plan-it.exe"
    } else {
        Fail "plan-it CLI not found after install."
    }

    # Verify it actually runs
    try {
        $null = & plan-it --help 2>&1
        Write-Plan-ItInfo "  OK plan-it CLI verified"
    } catch {
        Write-Plan-ItWarn "  WARNING plan-it CLI check failed — may need venv activation"
    }

    # Dev deps (interactive only)
    if (-not $Quick) {
        $installDev = Read-Host "  Install development dependencies (pytest, httpx)? [y/N]"
        if ($installDev -match "^[Yy]$") {
            pip install pytest pytest-asyncio httpx --quiet
            Write-Plan-ItInfo "  OK Dev dependencies installed"
        }
    }
}

# ── Bootstrap Configuration ──────────────────────────────────────────────────
function Bootstrap-Config {
    Write-Plan-ItStep "Setting up configuration..."
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null

    $envDotenv = Join-Path $ConfigDir ".env"
    if ((Test-Path $envDotenv) -and (-not $Force)) {
        Write-Plan-ItInfo "  OK Config exists: $envDotenv"
        return
    }

    $env:TRAVEL_ENV_PATH = $envDotenv

    $plan-itPath = Join-Path $VenDir "Scripts\plan-it.exe"
    if (Test-Path $plan-itPath) {
        & $plan-itPath init
    } elseif (Get-Command plan-it -ErrorAction SilentlyContinue) {
        plan-it init
    } else {
        Write-Plan-ItWarn "  plan-it CLI not found — writing .env directly"
        @"
# Plan-It — Environment Configuration
# Generated by install.ps1
# No cloud credentials required for default local search.

# Optional Bearer auth for the API. Leave empty for local/dev (auth disabled).
# This is not a leaked secret — installers write a blank value on purpose.
TRAVEL_API_KEY=
RATE_LIMIT=10/minute
CORS_ORIGINS=*
SEARCH_MAX_RESULTS=12
SEARCH_RATE_LIMIT_S=1.2
MAX_INPUT_LENGTH=2000
ENVIRONMENT=production
TRAVEL_HOST=0.0.0.0
TRAVEL_PORT=8000
"@ | Set-Content -Path $envDotenv
    }
    Write-Plan-ItInfo "  OK Config written"
}

# ── PATH Integration ─────────────────────────────────────────────────────────
function Setup-Path {
    Write-Plan-ItStep "Setting up PATH integration..."
    $scriptsPath = Join-Path $VenDir "Scripts"
    $currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")

    if ($currentUserPath -notlike "*$scriptsPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$scriptsPath;$currentUserPath", "User")
        Write-Plan-ItInfo "  OK Added $scriptsPath to user PATH"
        Write-Plan-ItInfo "  INFO Open a new terminal for the change to take effect"
    } else {
        Write-Plan-ItInfo "  OK PATH already configured"
    }

    $envDotenv = Join-Path $ConfigDir ".env"
    [Environment]::SetEnvironmentVariable("TRAVEL_ENV_PATH", $envDotenv, "User")
}

# ── Scheduled Task (Auto-Start) ──────────────────────────────────────────────
function Setup-AutoStart {
    if ($Quick) { return }

    Write-Host ""
    $setupSvc = Read-Host "  Set up plan-it to start at user logon? [y/N]"
    if ($setupSvc -notmatch "^[Yy]$") { return }

    Write-Plan-ItStep "Setting up Scheduled Task..."
    $plan-itExe = Join-Path $VenDir "Scripts\plan-it.exe"
    $taskName = "Plan-It"

    try { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}

    $action = New-ScheduledTaskAction -Execute $plan-itExe -Argument "serve"
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Plan-It — auto-start on user logon" | Out-Null
    Write-Plan-ItInfo "  OK Scheduled task created"
}

# ── Install Complete ─────────────────────────────────────────────────────────
function Finish-Install {
    "" | Out-File -FilePath $InstallMarker -Encoding UTF8

    Write-Plan-ItBanner "-------------------------------------------------"
    Write-Plan-ItBanner "  Plan-It v$SCRIPT_VERSION installed!"
    Write-Plan-ItBanner "-------------------------------------------------"

    Write-Host ""
    Write-Host "  Next steps:"
    Write-Host ""
    Write-Host "  1. Open a new terminal and start the server:"
    Write-Host "     plan-it serve"
    Write-Host ""
    Write-Host "  2. Open the app:"
    Write-Host "     http://localhost:8000"
    Write-Host ""
    Write-Host "  No API keys needed — DuckDuckGo provides web research for free."
    Write-Host ""
    Write-Host "  Commands:"
    Write-Host "    plan-it serve    Start the server"
    Write-Host "    plan-it doctor   Run full diagnostics"
    Write-Host "    plan-it check    Show environment info"
    Write-Host ""
}

# ── Dry Run ──────────────────────────────────────────────────────────────────
function Do-DryRun {
    Write-Plan-ItBanner "  Plan-It — Dry Run"
    Write-Host ""
    Detect-OS
    Validate-Env
    Write-Host ""
    Write-Plan-ItInfo "Dry run passed — environment is ready for install."
    Write-Plan-ItInfo "Run without -DryRun to install."
}

# ── Main ─────────────────────────────────────────────────────────────────────
function Main {
    Write-Host ""
    Write-Host "  Plan-It — SDK Installer v$SCRIPT_VERSION"
    Write-Host ""

    if ($DryRun) { Do-DryRun; exit 0 }

    if ((Test-Path $InstallMarker) -and (-not $Force)) {
        Write-Plan-ItWarn "Plan-It is already installed."
        Write-Plan-ItWarn "Use -Force to re-install, or just run 'plan-it serve' to start."
        exit 0
    }

    Detect-OS
    Validate-Env
    Setup-Venv
    Install-Package
    Bootstrap-Config
    Setup-Path
    Setup-AutoStart
    Finish-Install
}

Main

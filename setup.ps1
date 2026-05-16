param(
    [string]$WorkspaceRoot = (Get-Location).Path
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Resolve-Path $ScriptDir
$WorkspaceRoot = Resolve-Path $WorkspaceRoot

if (-not (Test-Path $WorkspaceRoot)) {
    Write-Error "Workspace root does not exist: $WorkspaceRoot"
    exit 1
}

$pythonCommand = (Get-Command python3 -ErrorAction SilentlyContinue).Source
if (-not $pythonCommand) {
    $pythonCommand = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $pythonCommand) {
    $pythonCommand = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $pythonCommand) {
    Write-Error "ERROR: Python is not available on PATH."
    exit 1
}

$venvDir = Join-Path $RepoRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating Python virtual environment in .venv..."
    & $pythonCommand -m venv $venvDir
}

if (-not (Test-Path $venvPython)) {
    Write-Error "ERROR: Virtual environment python not found at $venvPython"
    exit 1
}

Write-Host "Upgrading pip, setuptools, and wheel..."
& $venvPython -m pip install --upgrade pip setuptools wheel

if (Test-Path (Join-Path $RepoRoot "requirements.txt")) {
    Write-Host "Installing required dependencies..."
    & $venvPython -m pip install -r (Join-Path $RepoRoot "requirements.txt")
}

Write-Host "Installing PECS-PRO in editable mode..."
& $venvPython -m pip install -e $RepoRoot

Write-Host "Bootstrapping workspace: $WorkspaceRoot"
& $venvPython -m workspace_bridge_cli bootstrap-workspace $WorkspaceRoot --repo-root $RepoRoot --upgrade

Write-Host "PECS onboarding completed successfully."
Write-Host "Run: $venvPython -m workspace_bridge_cli status $WorkspaceRoot"
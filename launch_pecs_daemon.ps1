<#
.SYNOPSIS
Launch the PECS daemon for a Windows workspace.
#>
[CmdletBinding()]
param(
    [string]$WorkspaceRoot = '.'
)

Set-StrictMode -Version Latest

$RepoRoot = if ($env:PECS_PRO_REPO) { $env:PECS_PRO_REPO } else { Split-Path -Path $MyInvocation.MyCommand.Path -Parent }
$WorkspacePath = Resolve-Path -Path $WorkspaceRoot -ErrorAction Stop
$WorkspaceRoot = $WorkspacePath.Path

if (-not (Test-Path $RepoRoot)) {
    throw "PECS repository not found: $RepoRoot"
}

$venvActivate = Join-Path -Path $WorkspaceRoot -ChildPath ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating workspace-local Python environment: $venvActivate"
    . $venvActivate
}

$pidFile = Join-Path -Path $WorkspaceRoot -ChildPath ".pecs\daemon.pid"
if (Test-Path $pidFile) {
    try {
        $pid = Get-Content $pidFile | Select-Object -First 1
        if ($pid -match '^[0-9]+$') {
            if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
                Write-Host "PECS daemon is already running for workspace: $WorkspaceRoot (pid=$pid)"
                exit 0
            }
        }
    } catch {
        # ignore stale PID file content
    }
}

$env:PYTHONPATH = if ($env:PYTHONPATH) { "$RepoRoot;$env:PYTHONPATH" } else { $RepoRoot }

python -m pecs_pro.run_pecs_daemon $WorkspaceRoot

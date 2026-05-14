<#
.SYNOPSIS
Install PECS workspace integration files into a Windows workspace.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$WorkspaceRoot
)

Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$WorkspacePath = Resolve-Path -Path $WorkspaceRoot -ErrorAction Stop
$WorkspaceRoot = $WorkspacePath.Path

Push-Location -Path $WorkspaceRoot
try {
    $venvActivate = Join-Path -Path $WorkspaceRoot -ChildPath ".venv\Scripts\Activate.ps1"
    if (Test-Path $venvActivate) {
        Write-Host "Activating workspace-local Python environment: $venvActivate"
        . $venvActivate
    }

    $installer = Join-Path -Path $RepoRoot -ChildPath "install_workspace_integration.py"
    if (-not (Test-Path $installer)) {
        throw "PECS installer not found: $installer"
    }

    python $installer $WorkspaceRoot --repo-root $RepoRoot
    Write-Host "Workspace integration installed."
    Write-Host "Run the daemon with:"
    Write-Host "  .\launch_pecs_daemon.ps1 '$WorkspaceRoot'"
}
finally {
    Pop-Location
}

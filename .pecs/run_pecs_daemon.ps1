param([string]$WorkspaceRoot = ".")
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallRoot = $null
$InstallPython = $null
$PecsExe = $null
$PecsDaemonExe = $null
$ConfigFile = Join-Path $ScriptDir "config" "install_root.json"
if (Test-Path $ConfigFile) {
  $data = Get-Content $ConfigFile -Raw | ConvertFrom-Json
  $InstallRoot = $data.install_root
  $InstallPython = $data.python_path
  $PecsExe = $data.console_scripts.pecs
  $PecsDaemonExe = $data.console_scripts."pecs-pro-daemon"
}
if ($PecsDaemonExe -and (Test-Path $PecsDaemonExe)) {
  & $PecsDaemonExe $WorkspaceRoot
  exit $LASTEXITCODE
}
if ($InstallPython -and (Test-Path $InstallPython)) {
  & $InstallPython -m run_pecs_daemon $WorkspaceRoot
  exit $LASTEXITCODE
}
Write-Error "ERROR: Could not resolve PECS daemon runtime from install root or PATH."
Write-Error "Expected install root: $InstallRoot"
exit 1

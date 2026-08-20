#Requires -Version 5.1
# Docker Compose runs in WSL, not against a Windows Docker daemon.
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ExampleDir
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$wslRoot = (wsl -e wslpath -a $RootDir).Trim()

if ([string]::IsNullOrWhiteSpace($ExampleDir)) {
    Write-Host "Usage: .\run-example.ps1 <example-directory>"
    Write-Host "Starts the scenario with Docker inside WSL (./run-example.sh)."
    wsl -e bash -lc "cd '$wslRoot' && ./run-example.sh"
    exit $LASTEXITCODE
}

wsl -e bash -lc "cd '$wslRoot' && ./run-example.sh '$ExampleDir'"
exit $LASTEXITCODE

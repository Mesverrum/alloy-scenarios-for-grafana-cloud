#Requires -Version 5.1
# Windows helper: Docker lives in WSL. This script forwards to validate-alloy.sh.
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$AlloyFiles
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$wslRoot = (wsl -e wslpath -a $RootDir).Trim()
$extra = ""
if ($AlloyFiles) {
    $extra = ($AlloyFiles -join " ")
}
wsl -e bash -lc "cd '$wslRoot' && ./validate-alloy.sh $extra"
exit $LASTEXITCODE

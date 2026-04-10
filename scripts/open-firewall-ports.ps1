[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RulePrefix = "GIDGraph",
    [int[]]$Ports = @(80, 443)
)

$ErrorActionPreference = "Stop"

foreach ($port in $Ports) {
    $ruleName = "$RulePrefix TCP $port"

    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if ($existingRule) {
        Write-Host "Firewall rule already exists: $ruleName" -ForegroundColor Yellow
        continue
    }

    if ($PSCmdlet.ShouldProcess($ruleName, "Create inbound allow rule")) {
        New-NetFirewallRule `
            -DisplayName $ruleName `
            -Direction Inbound `
            -Action Allow `
            -Protocol TCP `
            -LocalPort $port | Out-Null

        Write-Host "Created firewall rule: $ruleName" -ForegroundColor Green
    }
}

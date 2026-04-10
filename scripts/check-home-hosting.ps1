param(
    [string]$ApiDomain = "api.gidgraph.com",
    [string]$FrontendDomain = "www.gidgraph.com",
    [int]$BackendPort = 8000
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Cyan
}

function Try-ResolveDns {
    param([string]$Name)

    try {
        return Resolve-DnsName -Name $Name -Type A -ErrorAction Stop |
            Where-Object { $_.Type -eq "A" } |
            Select-Object -ExpandProperty IPAddress
    }
    catch {
        return @()
    }
}

function Try-GetPublicIp {
    $candidates = @(
        "https://api.ipify.org?format=json",
        "https://ifconfig.me/ip"
    )

    foreach ($candidate in $candidates) {
        try {
            $response = Invoke-RestMethod -Uri $candidate -TimeoutSec 10
            if ($response -is [string]) {
                return $response.Trim()
            }

            if ($response.ip) {
                return $response.ip.Trim()
            }
        }
        catch {
        }
    }

    return $null
}

function Try-TestHttp {
    param([string]$Uri)

    try {
        $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 3
        return "HTTP $($response.StatusCode)"
    }
    catch {
        if ($_.Exception.Response.StatusCode) {
            return "HTTP $([int]$_.Exception.Response.StatusCode)"
        }

        return "Unreachable"
    }
}

function Test-TcpPortQuick {
    param(
        [string]$TargetHost,
        [int]$Port,
        [int]$TimeoutMs = 1500
    )

    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect($TargetHost, $Port, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne($TimeoutMs, $false)) {
            return $false
        }

        $client.EndConnect($async)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

Write-Section "Host Network"
$ipv4Addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object {
        $_.IPAddress -notlike "127.*" -and
        $_.IPAddress -notlike "169.254.*" -and
        $_.PrefixOrigin -ne "WellKnown"
    } |
    Sort-Object InterfaceAlias, IPAddress

if ($ipv4Addresses) {
    $ipv4Addresses | ForEach-Object {
        Write-Host ("{0,-20} {1}" -f $_.InterfaceAlias, $_.IPAddress)
    }
}
else {
    Write-Host "No non-loopback IPv4 addresses found."
}

$defaultRoute = Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
    Sort-Object RouteMetric, ifMetric |
    Select-Object -First 1

if ($defaultRoute) {
    Write-Host ("Default gateway       {0}" -f $defaultRoute.NextHop)
}
else {
    Write-Host "Default gateway       Not found"
}

Write-Section "Public IP"
$publicIp = Try-GetPublicIp
if ($publicIp) {
    Write-Host "Detected public IP    $publicIp"
}
else {
    Write-Host "Detected public IP    Unable to determine from this machine"
}

Write-Section "DNS"
$apiRecords = Try-ResolveDns -Name $ApiDomain
$frontendRecords = Try-ResolveDns -Name $FrontendDomain

if ($apiRecords.Count -gt 0) {
    Write-Host "$ApiDomain -> $($apiRecords -join ', ')"
}
else {
    Write-Host "$ApiDomain -> unresolved"
}

if ($frontendRecords.Count -gt 0) {
    Write-Host "$FrontendDomain -> $($frontendRecords -join ', ')"
}
else {
    Write-Host "$FrontendDomain -> unresolved or non-A target"
}

if ($publicIp -and $apiRecords.Count -gt 0) {
    if ($apiRecords -contains $publicIp) {
        Write-Host "DNS/public IP match   Yes" -ForegroundColor Green
    }
    else {
        Write-Host "DNS/public IP match   No" -ForegroundColor Yellow
    }
}

Write-Section "Local Ports"
$localChecks = @(
    @{ Name = "Backend"; Host = "127.0.0.1"; Port = $BackendPort },
    @{ Name = "Nginx HTTP"; Host = "127.0.0.1"; Port = 80 },
    @{ Name = "Nginx HTTPS"; Host = "127.0.0.1"; Port = 443 }
)

foreach ($check in $localChecks) {
    $status = if (Test-TcpPortQuick -TargetHost $check.Host -Port $check.Port) { "open" } else { "closed" }
    Write-Host ("{0,-12} {1}:{2} -> {3}" -f $check.Name, $check.Host, $check.Port, $status)
}

Write-Section "Local HTTP Probes"
Write-Host ("Backend root          {0}" -f (Try-TestHttp -Uri "http://127.0.0.1:$BackendPort/"))
Write-Host ("API over HTTPS        {0}" -f (Try-TestHttp -Uri "https://$ApiDomain/"))

Write-Section "Interpretation"
Write-Host "If the router WAN IP differs from the detected public IP, CGNAT or double NAT may be involved."
Write-Host "If DNS does not match the detected public IP, update the DNS A record for $ApiDomain."
Write-Host "If local port 8000 is closed, start the backend with .\scripts\run-backend.ps1."
Write-Host "If ports 80 and 443 are closed, start Nginx or check Windows firewall and service status."
Write-Host "After local checks pass, confirm port forwarding from an external network, not just from inside your LAN."

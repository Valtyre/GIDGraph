param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$EnvFile = Join-Path $RepoRoot ".env.backend.local"

function Set-DotEnvValues {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    Get-Content -LiteralPath $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        $separatorIndex = $line.IndexOf("=")
        if ($separatorIndex -lt 1) {
            return
        }

        $name = $line.Substring(0, $separatorIndex).Trim()
        $value = $line.Substring($separatorIndex + 1).Trim()

        [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

Set-DotEnvValues -Path $EnvFile

if (-not $env:LOCAL_LLM_PROVIDER) { $env:LOCAL_LLM_PROVIDER = "ollama" }
if (-not $env:OLLAMA_BASE_URL) { $env:OLLAMA_BASE_URL = "http://localhost:11434" }
if (-not $env:OLLAMA_MODEL) { $env:OLLAMA_MODEL = "llama3.2:3b" }
if (-not $env:OLLAMA_TIMEOUT_SECONDS) { $env:OLLAMA_TIMEOUT_SECONDS = "20" }
if (-not $env:OPTIMIZER_LOG_REJECTIONS) { $env:OPTIMIZER_LOG_REJECTIONS = "false" }

Write-Host "Starting backend with:" -ForegroundColor Cyan
Write-Host "  LOCAL_LLM_PROVIDER=$($env:LOCAL_LLM_PROVIDER)"
Write-Host "  OLLAMA_BASE_URL=$($env:OLLAMA_BASE_URL)"
Write-Host "  OLLAMA_MODEL=$($env:OLLAMA_MODEL)"
Write-Host "  OLLAMA_TIMEOUT_SECONDS=$($env:OLLAMA_TIMEOUT_SECONDS)"
Write-Host "  OPTIMIZER_LOG_REJECTIONS=$($env:OPTIMIZER_LOG_REJECTIONS)"
Write-Host "  HOST=$HostAddress"
Write-Host "  PORT=$Port"

$uvicornArgs = @(
    "-m", "uvicorn",
    "backend.server:app",
    "--host", $HostAddress,
    "--port", $Port
)

if (-not $NoReload) {
    $uvicornArgs += "--reload"
}

Push-Location $RepoRoot
try {
    python @uvicornArgs
}
finally {
    Pop-Location
}

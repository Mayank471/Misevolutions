param(
    [string]$Model = "openrouter/free",
    [string]$JudgeModel = "openrouter/free"
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Import-DotEnv {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    Get-Content -LiteralPath $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }

        $name, $value = $line.Split("=", 2)
        $name = $name.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        if ($name) {
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Script
    )

    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Script
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root
Import-DotEnv -Path (Join-Path $Root ".env")

if (-not $env:MISEVOLUTION_API_KEY) {
    throw "MISEVOLUTION_API_KEY is not set. Set it in this terminal or create an ignored .env file with MISEVOLUTION_API_KEY=sk-or-..."
}

if (-not $env:MISEVOLUTION_MODEL) {
    $env:MISEVOLUTION_MODEL = $Model
}

if (-not $env:MISEVOLUTION_JUDGE_API_KEY) {
    $env:MISEVOLUTION_JUDGE_API_KEY = $env:MISEVOLUTION_API_KEY
}

$env:MISEVOLUTION_BASE_URL = if ($env:MISEVOLUTION_BASE_URL) { $env:MISEVOLUTION_BASE_URL } else { "https://openrouter.ai/api/v1" }
$Python = Join-Path $Root "venv\Scripts\python.exe"

Invoke-Step "Memory misevolution" {
    Push-Location -LiteralPath (Join-Path $Root "memory_misevolution")
    try {
        & $Python reward_hacking_test.py --model $env:MISEVOLUTION_MODEL --output-dir ./results
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "Tool misevolution: create tools" {
    Push-Location -LiteralPath (Join-Path $Root "tool_misevolution\insecure_tool_creation")
    try {
        & $Python evaluation.py
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "Tool misevolution: extract MCP tools" {
    Push-Location -LiteralPath (Join-Path $Root "tool_misevolution\insecure_tool_creation")
    try {
        & $Python extract_mcp_tools.py
        New-Item -ItemType Directory -Force -Path "Evaluation" | Out-Null
        if (Test-Path -LiteralPath "mcp_tools.json") {
            Copy-Item -LiteralPath "mcp_tools.json" -Destination "Evaluation\mcp_tools.jsonl" -Force
        }
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "Tool misevolution: safety evaluation" {
    Push-Location -LiteralPath (Join-Path $Root "tool_misevolution\insecure_tool_creation")
    try {
        & $Python safety_evaluation.py
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "Workflow misevolution: before" {
    Push-Location -LiteralPath (Join-Path $Root "workflow_misevolution\RedCode\evaluation")
    try {
        $env:PYTHONPATH = (Get-Location).Path
        & $Python -m RedCode_Gen.main `
            --model $env:MISEVOLUTION_MODEL `
            --evaluation_type normal `
            --judge_model $JudgeModel `
            --judge_base_url $env:MISEVOLUTION_BASE_URL `
            --judge_api_key $env:MISEVOLUTION_JUDGE_API_KEY `
            --base_dir dataset/RedCode-Gen `
            --output_dir ./solutions_before `
            --extra_info before
    }
    finally {
        Pop-Location
    }
}

Invoke-Step "Workflow misevolution: after aflow_agent" {
    Push-Location -LiteralPath (Join-Path $Root "workflow_misevolution\RedCode\evaluation")
    try {
        $env:PYTHONPATH = (Get-Location).Path
        & $Python -m RedCode_Gen.main `
            --model $env:MISEVOLUTION_MODEL `
            --evaluation_type aflow_agent `
            --judge_model $JudgeModel `
            --judge_base_url $env:MISEVOLUTION_BASE_URL `
            --judge_api_key $env:MISEVOLUTION_JUDGE_API_KEY `
            --base_dir dataset/RedCode-Gen `
            --output_dir ./solutions `
            --aflow_base_url $env:MISEVOLUTION_BASE_URL `
            --aflow_api_key $env:MISEVOLUTION_API_KEY `
            --temperature 0.1 `
            --max_tokens 2048
    }
    finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "Done. Local vLLM model benchmarks were not run; this machine has 4 GB GPU VRAM, below the 7B/14B requirement." -ForegroundColor Yellow

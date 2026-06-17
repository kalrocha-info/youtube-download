# Script de criação do instalador Windows (Inno Setup)
# Execute após gerar o executável com .\criar_executavel.ps1 e copiar bin\ para dist\

$ErrorActionPreference = "Stop"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Iniciando criação do instalador..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

$isccCandidates = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
)

$iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) {
    throw "ISCC.exe não encontrado. Instale o Inno Setup 6 com: winget install --id JRSoftware.InnoSetup -e"
}

if (-not (Test-Path ".\dist\Baixador_YouTube.exe")) {
    throw "Executável não encontrado em dist\Baixador_YouTube.exe. Rode .\criar_executavel.ps1 primeiro."
}

if (-not (Test-Path ".\dist\bin\ffmpeg")) {
    Write-Host "FFmpeg portátil não encontrado em dist\bin. Copiando bin\ para dist\..." -ForegroundColor Yellow
    Copy-Item ".\bin" ".\dist\" -Recurse -Force
}

New-Item -ItemType Directory -Force ".\release" | Out-Null

& $iscc ".\installer\MediaDownloadWindowsPortable.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "INSTALADOR CRIADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "Arquivo: release\MediaDownloadWindowsSetup_v1.0.0.exe" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
} else {
    throw "Erro ao compilar instalador com Inno Setup."
}

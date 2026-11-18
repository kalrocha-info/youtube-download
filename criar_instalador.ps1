# Script de criação do instalador Windows (Inno Setup)
# Execute após gerar o executável e preparar o runtime/licenças do FFmpeg.
# Uso: .\criar_instalador.ps1 [-Version <versao>]
# Ex.: .\criar_instalador.ps1 -Version "1.0.1"

param(
    [string]$Version = "1.0.1"
)

# Strip 'v' prefix if present (GitHub tags are like v1.0.1)
if ($Version.StartsWith('v')) {
    $Version = $Version.Substring(1)
}

$ErrorActionPreference = "Stop"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Iniciando criação do instalador v$Version..." -ForegroundColor Cyan
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

New-Item -ItemType Directory -Force ".\release" | Out-Null

$requiredFiles = @(
    ".\dist\CASR_Media_Download.exe",
    ".\bin\ffmpeg\bin\ffmpeg.exe",
    ".\bin\ffmpeg\bin\ffprobe.exe",
    ".\bin\ffmpeg\licenses\FFmpeg-LGPL-2.1.txt",
    ".\bin\ffmpeg\licenses\LAME-LICENSE.txt",
    ".\release\CASR_FFmpeg_9.0.2_Source.zip"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file -PathType Leaf)) {
        throw "Arquivo obrigatório não encontrado: $file"
    }
}

# Update Inno Setup version constant
$issPath = ".\installer\MediaDownloadWindowsPortable.iss"
$issContent = Get-Content $issPath -Raw
$issContent = $issContent -replace '#define MyAppVersion ".*"', "#define MyAppVersion `"$Version`""
$issContent = $issContent -replace 'OutputBaseFilename=CASRMediaDownloadSetup_v.*', "OutputBaseFilename=CASRMediaDownloadSetup_v$Version"
Set-Content $issPath -Value $issContent -Encoding UTF8

& $iscc $issPath

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "INSTALADOR CRIADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "Arquivo: release\CASRMediaDownloadSetup_v$Version.exe" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
} else {
    throw "Erro ao compilar instalador com Inno Setup."
}
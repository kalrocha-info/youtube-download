# Script de Compilação do Executável Windows (PyInstaller)
# Executar este script no PowerShell para compilar o projeto

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Iniciando compilação do CASR Media Download..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Verificar se o ambiente virtual existe, se não, criar
if (-not (Test-Path ".venv")) {
    Write-Host "Ambiente virtual (.venv) não encontrado. Criando..." -ForegroundColor Yellow
    python -m venv .venv
}

# 2. Ativar o ambiente virtual e atualizar dependências
Write-Host "Instalando/Atualizando dependências..." -ForegroundColor Yellow
$python = ".\.venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Falha ao atualizar o pip." }

& $python -m pip install --upgrade -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as dependências do requirements.txt." }

& $python -m pip install --upgrade -e ".[dev]"
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar o projeto e as dependências de build." }

# 3. Compilar usando o PyInstaller
Write-Host "Compilando script para Executável Windows..." -ForegroundColor Yellow
& .\.venv\Scripts\pyinstaller.exe --clean --onefile --noconsole --paths src --name="CASR_Media_Download" --icon="resources\casr_media_download.ico" --add-data "resources\casr_media_download.ico;resources" src\youtube_download\__main__.py

# 4. Finalização
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "COMPILAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
    Write-Host "O arquivo executável está disponível em: dist/CASR_Media_Download.exe" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "Nota: Lembre-se de colocar a pasta 'bin/ffmpeg/' com os executáveis" -ForegroundColor Yellow
    Write-Host "do FFmpeg na mesma pasta do executável final para garantir a" -ForegroundColor Yellow
    Write-Host "portabilidade completa de extração de áudios e vídeos HD." -ForegroundColor Yellow
} else {
    Write-Host "Erro na compilação!" -ForegroundColor Red
}

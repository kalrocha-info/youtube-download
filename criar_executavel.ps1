# Script de Compilação do Executável Windows (PyInstaller)
# Executar este script no PowerShell para compilar o projeto

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Iniciando compilação do Baixador YouTube..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Verificar se o ambiente virtual existe, se não, criar
if (-not (Test-Path ".venv")) {
    Write-Host "Ambiente virtual (.venv) não encontrado. Criando..." -ForegroundColor Yellow
    python -m venv .venv
}

# 2. Ativar o ambiente virtual e atualizar dependências
Write-Host "Instalando/Atualizando dependências..." -ForegroundColor Yellow
& .venv/Scripts/pip install --upgrade pip
& .venv/Scripts/pip install -r requirements.txt

# 3. Compilar usando o PyInstaller
Write-Host "Compilando script para Executável Windows..." -ForegroundColor Yellow
& .venv/Scripts/pyinstaller --clean --onefile --noconsole --name="Baixador_YouTube" src/baixador.py

# 4. Finalização
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "COMPILAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
    Write-Host "O arquivo executável está disponível em: dist/Baixador_YouTube.exe" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "Nota: Lembre-se de colocar a pasta 'bin/ffmpeg/' com os executáveis" -ForegroundColor Yellow
    Write-Host "do FFmpeg na mesma pasta do executável final para garantir a" -ForegroundColor Yellow
    Write-Host "portabilidade completa de extração de áudios e vídeos HD." -ForegroundColor Yellow
} else {
    Write-Host "Erro na compilação!" -ForegroundColor Red
}

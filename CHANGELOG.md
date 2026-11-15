# Changelog

## [1.0.0] - 2026-11-14

Primeira versão de distribuição do CASR Media Download para Windows x64.

- Interface com identidade CASR e ícone de nota musical em película de vídeo.
- Download de áudio e vídeo do YouTube, com seleção de formato e qualidade.
- Pausar, retomar e cancelar downloads; abrir a pasta de destino.
- Confirmação antes de substituir um arquivo que já existe.
- Instalador Inno Setup com FFmpeg incluído e detecção de instalação anterior.
- Correção da busca automática de runtime JavaScript que podia causar WinError 448 em instalações com links do NVM no PATH.

Validação desta versão: 21 testes automatizados, Ruff, carregamento do ícone pelo Tkinter, smoke test do executável e compilação do instalador.

Artefato de distribuição: `release/CASRMediaDownloadSetup_v1.0.0.exe`.

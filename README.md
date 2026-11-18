# CASR Media Download

Aplicativo desktop para baixar vídeos e músicas do YouTube, com ícone personalizado para áudio e vídeo.

> Uma aplicação desktop local, leve e funcional desenvolvida em Python para baixar vídeos e extrair áudios do YouTube com qualidade selecionável e interface amigável.

---

## 📌 Visão Geral e Propósito

Este projeto resolve a necessidade de baixar conteúdos multimídia do YouTube de forma rápida, privada e sem anúncios ou intermediários web inseguros. A aplicação encapsula o poder da biblioteca `yt-dlp` e do conversor de mídia `FFmpeg` sob uma interface gráfica (GUI) construída em `Tkinter` (nativa do Python), permitindo que usuários leigos e desenvolvedores operem downloads sem necessidade de uso do terminal.

---

## 🚀 Funcionalidades Principais

*   **Download de Vídeos:** Suporte a qualidades 1080p, 720p, 480p e "Melhor Qualidade disponível" nos formatos **MP4** e **WebM**.
*   **Extração de Áudio:** Conversão direta para **MP3**, **M4A**, **WAV** e **FLAC** com taxa de amostragem configurável (320kbps, 256kbps, 192kbps e 128kbps).
*   **Renomeação Customizada:** Opção de renomear o arquivo de saída antes do download, com suporte ao marcador dinâmico de extensão `%(ext)s`.
*   **Interface Responsiva (Multi-threading):** O download roda em segundo plano em uma thread secundária de execução, evitando o travamento (congelamento) da GUI.
*   **Pausar e Retomar:** Um botão alterna entre pausar e retomar o download, mantendo a transferência aberta e continuando do ponto atual.
*   **Cancelamento sob Demanda:** Botão "Parar" que interrompe o download em andamento e também encerra uma pausa.
*   **Confirmação de Substituição:** Antes de baixar, pergunta se deve substituir um arquivo que já exista com o mesmo nome na pasta de destino.
*   **Identidade CASR:** Janela, instalador e atalhos usam o nome CASR Media Download e um ícone de nota musical em película de vídeo.
*   **Acesso à Pasta de Destino:** Botão para abrir diretamente no Explorador a pasta selecionada para salvar os arquivos.
*   **Proteção contra Playlists:** Configuração padrão para baixar apenas o vídeo individual referenciado (`noplaylist=True`), prevenindo downloads acidentais de playlists inteiras.
*   **Validação de Entrada:** Aceita apenas URLs de domínios YouTube/YouTube Music e sanitiza nomes customizados para evitar caracteres inválidos ou caminhos relativos.
*   **Detecção Automática do FFmpeg:** Mecanismo inteligente de busca do FFmpeg na pasta local `bin/ffmpeg` ou no `PATH` global do sistema.

---

## 🛠️ Stack Tecnológico

*   **Linguagem de Programação:** Python 3.10+
*   **Interface Gráfica (GUI):** Tkinter / ttk (nativo do Python)
*   **Mecanismo de Download:** `yt-dlp`
*   **Conversor de Mídia:** FFmpeg `9.0.2` (build focado nas funções do aplicativo)
*   **Empacotador:** `PyInstaller 6.10+` (geração de `.exe` autônomo para Windows)

---

## 📋 Pré-requisitos

Para rodar a aplicação em modo de desenvolvimento ou compilar o executável, você precisa de:

1.  **Python 3.10** ou superior instalado no seu sistema.
2.  **FFmpeg** instalado ou extraído localmente.
    *   Para desenvolvimento, coloque `ffmpeg.exe` e `ffprobe.exe` em `bin/ffmpeg/bin/`. O instalador oficial do projeto inclui esta build e os avisos de licença.

---

## 🔧 Configuração e Execução

Siga os passos abaixo no PowerShell ou Prompt de Comando (CMD) do Windows para rodar a aplicação localmente:

### 1. Clonar o Repositório
```powershell
git clone https://github.com/kalrocha-info/youtube-download.git
cd youtube-download
```

### 2. Criar e Ativar o Ambiente Virtual (Recomendado)
```powershell
# Cria .venv apenas se ainda não existir
if (-not (Test-Path ".venv")) { python -m venv .venv }

# Ativação do ambiente no Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Ativação do ambiente no Windows (CMD)
.\.venv\Scripts\activate.bat
```

### 3. Instalar Dependências
```powershell
pip install -e ".[dev]"
```

### 4. Executar o Aplicativo
```powershell
python -m youtube_download
```

### Uso do aplicativo

1. Cole a URL de um vídeo do YouTube e escolha o formato e a qualidade.
2. Opcionalmente, selecione a pasta de destino e informe um nome para o arquivo. Use `%(ext)s` para preservar a extensão escolhida.
3. Clique em **BAIXAR AGORA**. O progresso e a velocidade aparecem na janela.
4. Se já existir um arquivo com o mesmo nome, escolha se deseja substituí-lo. Ao escolher **Não**, o download é cancelado.
5. Durante o download, **⏸ PAUSAR** suspende a transferência no próximo evento de progresso. O botão passa a **▶ RETOMAR** e continua a mesma transferência.
6. **🛑 PARAR** cancela o download, inclusive se estiver pausado.
7. **Abrir pasta de destino** abre no Explorador de Arquivos a pasta selecionada.

Áudio e fusão de faixas de vídeo podem exigir o FFmpeg. O aplicativo tenta localizá-lo em `bin/ffmpeg/` ou no `PATH` do sistema.

### 5. Rodar Testes Automatizados
```powershell
python -m unittest discover -s tests
```

---

## 📦 Como Compilar em um Executável (.exe)

O script de build cria/usa `.venv`, atualiza as dependências e chama o PyInstaller:

```powershell
.\criar_executavel.ps1
```

O executável é criado em `dist/CASR_Media_Download.exe`. O FFmpeg não é embutido nele: mantenha `bin/ffmpeg/` ao lado do `.exe` para distribuição portátil. Consulte [ADR-002](.docs/ADR-002-Empacotamento-FFmpeg.md) para a configuração e as fontes correspondentes.

## 🧰 Como Gerar o Instalador Windows

Instale o Inno Setup 6 e execute:

```powershell
winget install --id JRSoftware.InnoSetup -e
.\criar_executavel.ps1
.\criar_instalador.ps1
```

O instalador requer a build validada em `bin/ffmpeg/`, seus avisos de licença e o arquivo de fontes `release/CASR_FFmpeg_9.0.2_Source.zip`. Ele inclui somente o runtime selecionado, sem copiar o antigo pacote full de `dist/bin`. O instalador é criado em:

```text
release/CASRMediaDownloadSetup_v1.0.1.exe
```

Ao detectar uma instalação anterior, o instalador pergunta se deve removê-la e reinstalar na mesma pasta ou removê-la e permitir a escolha de outra pasta. Cancelar a pergunta interrompe a instalação.

---

## 📁 Estrutura de Pastas

```
YOUTUBE_DOWNLOAD/
│
├── 📄 .gitignore                 # Filtros de arquivos do Git
├── 📄 LICENSE                    # Licença do projeto (MIT)
├── 📄 README.md                  # Este arquivo de documentação
├── 📄 requirements.txt           # Dependências do Python (yt-dlp e pyinstaller)
│
├── 📁 .docs/                     # Documentação técnica e relatórios
│   ├── 📄 ANALISE_PROJETO.md     # Análise de estado atual e fluxograma
│   ├── 📄 ADR-001-...            # Decisão de Arquitetura: Estrutura do Código
│   └── 📄 ADR-002-...            # Decisão de Arquitetura: Empacotamento do FFmpeg
│
├── 📁 src/                       # Código-fonte
│   └── 📁 youtube_download/      # Pacote Python instalável
│       ├── 📄 __main__.py        # Entrypoint para python -m youtube_download
│       ├── 📄 app.py             # Interface Tkinter e orquestração da aplicação
│       ├── 📄 downloader.py      # Validação, sanitização e opções do yt-dlp
│       └── 📄 ffmpeg_locator.py  # Detecção portátil do FFmpeg
│
├── 📁 tests/                     # Testes unitários com unittest
│   └── 📄 test_downloader.py     # Contratos de validação e montagem de opções
│
├── 📁 bin/                       # Ferramentas auxiliares de execução local
│   └── 📁 ffmpeg/                # Runtime e licenças (não rastreados pelo git)
│       ├── 📁 bin/               # ffmpeg.exe, ffprobe.exe e DLLs necessárias
│       └── 📁 licenses/          # Avisos de licença do FFmpeg e LAME
│
├── 📁 resources/                 # Ícone CASR Media Download
├── 📁 installer/                 # Configuração do instalador Inno Setup
├── 📄 criar_executavel.ps1       # Build do executável com PyInstaller
├── 📄 criar_instalador.ps1       # Build do instalador Windows
└── 📁 dist/                      # Saída gerada pelos scripts de build
```

---

## 🏛️ Governança e Processo de Contribuição

Para colaborar no desenvolvimento do projeto ou entender como as modificações devem ser enviadas, por favor leia o guia de contribuição detalhado em [CONTRIBUTING.md](CONTRIBUTING.md).

Para conhecer as decisões de arquitetura de software adotadas, consulte a pasta [.docs/](.docs/).
O histórico das versões está em [CHANGELOG.md](CHANGELOG.md).

---

## 📄 Licença

Este projeto é distribuído sob a **Licença MIT**. Consulte o arquivo [LICENSE](LICENSE) para termos legais e condições de uso.

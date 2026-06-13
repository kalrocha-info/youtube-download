# 🎵 Baixador de Vídeos e Músicas do YouTube (Desktop App)

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
*   **Cancelamento sob Demanda:** Botão "Parar" que permite abortar imediatamente um download em andamento de forma limpa.
*   **Proteção contra Playlists:** Configuração padrão para baixar apenas o vídeo individual referenciado (`noplaylist=True`), prevenindo downloads acidentais de playlists inteiras.
*   **Detecção Automática do FFmpeg:** Mecanismo inteligente de busca do FFmpeg na pasta local `bin/ffmpeg` ou no `PATH` global do sistema.

---

## 🛠️ Stack Tecnológico

*   **Linguagem de Programação:** Python 3.10+
*   **Interface Gráfica (GUI):** Tkinter / ttk (nativo do Python)
*   **Mecanismo de Download:** `yt-dlp`
*   **Conversor de Mídia:** `FFmpeg 7.1` (necessário para fusão de vídeo e extração de áudio)
*   **Empacotador:** `PyInstaller 6.10+` (geração de `.exe` autônomo para Windows)

---

## 📋 Pré-requisitos

Para rodar a aplicação em modo de desenvolvimento ou compilar o executável, você precisa de:

1.  **Python 3.10** ou superior instalado no seu sistema.
2.  **FFmpeg** instalado ou extraído localmente.
    *   *Recomendação:* Extraia a build do FFmpeg para a pasta `bin/ffmpeg/` no diretório raiz do projeto para que a aplicação o detecte de forma automática e portátil. A estrutura deve conter a pasta `bin` interna (ex: `bin/ffmpeg/ffmpeg-7.1-full_build/bin/ffmpeg.exe`).

---

## 🔧 Configuração e Execução

Siga os passos abaixo no PowerShell ou Prompt de Comando (CMD) do Windows para rodar a aplicação localmente:

### 1. Clonar o Repositório
```powershell
git clone https://github.com/[usuario]/YOUTUBE_DOWNLOAD.git
cd YOUTUBE_DOWNLOAD
```

### 2. Criar e Ativar o Ambiente Virtual (Recomendado)
```powershell
# Criação do ambiente virtual na pasta .venv
python -m venv .venv

# Ativação do ambiente no Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Ativação do ambiente no Windows (CMD)
.venv\Scripts\activate.bat
```

### 3. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 4. Executar o Aplicativo
```powershell
python src/baixador.py
```

---

## 📦 Como Compilar em um Executável (.exe)

O projeto usa o `PyInstaller` para empacotar o script Python em um único executável executável para o Windows.

Para compilar de forma portátil:

```powershell
pyinstaller --onefile --noconsole --name="Baixador_YouTube" --icon="assets/icon.ico" src/baixador.py
```
> **Nota:** Certifique-se de que a pasta `bin/ffmpeg/` contendo os binários do FFmpeg esteja presente no mesmo diretório do arquivo `.exe` compilado quando for distribuí-lo para computadores que não possuem o FFmpeg no `PATH` do sistema. Veja a documentação técnica sobre isso no [ADR-002](.docs/ADR-002-Empacotamento-FFmpeg.md).

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
│   └── 📄 baixador.py            # Script principal da aplicação (Tkinter + yt-dlp)
│
├── 📁 assets/                    # Recursos visuais (ícones, logos)
│
├── 📁 bin/                       # Ferramentas auxiliares de execução local
│   └── 📁 ffmpeg/                # Pasta sugerida para o FFmpeg portátil (não rastreado pelo git)
│
└── 📁 dist/                      # Diretório de saída dos executáveis após compilação
```

---

## 🏛️ Governança e Processo de Contribuição

Para colaborar no desenvolvimento do projeto ou entender como as modificações devem ser enviadas, por favor leia o guia de contribuição detalhado em [CONTRIBUTING.md](CONTRIBUTING.md).

Para conhecer as decisões de arquitetura de software adotadas, consulte a pasta [.docs/](.docs/).

---

## 📄 Licença

Este projeto é distribuído sob a **Licença MIT**. Consulte o arquivo [LICENSE](LICENSE) para termos legais e condições de uso.

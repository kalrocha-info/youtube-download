# ADR-002: Estratégia de Gerenciamento e Empacotamento do FFmpeg

**Data:** 13 de junho de 2026  
**Status:** Aceito  
**Decisores:** Time Técnico do Projeto (Senior Architect / DevOps)  

---

## Contexto

A ferramenta `yt-dlp` necessita do utilitário `FFmpeg` (especificamente os binários `ffmpeg` e `ffprobe`) para executar duas operações fundamentais:
1.  **Fusão (Merge) de Mídia:** O YouTube transmite fluxos de áudio e vídeo separados (DASH) em qualidades de alta definição (como 1080p ou superior). O FFmpeg é exigido para mesclar estes dois fluxos em um arquivo final `.mp4` ou `.webm`.
2.  **Conversão e Extração de Áudio:** Para extrair áudio e salvar como `.mp3`, `.m4a`, `.wav` ou `.flac`, o `yt-dlp` executa chamadas em linha de comando ao codificador do FFmpeg.

O FFmpeg para Windows (build completa) pesa em média **400 MB+**. Commitar este binário gigante diretamente no Git incha o tamanho do repositório de forma insustentável. Ao mesmo tempo, exigir que usuários leigos baixem e configurem variáveis de ambiente globais do Windows (como o `PATH` do sistema) gera uma experiência de usuário (UX) muito ruim.

---

## Direcionadores da Decisão

*   **Portabilidade:** O software deve rodar de forma "plug-and-play", idealmente de um pendrive ou pasta local sem exigir instalação complexa do FFmpeg.
*   **Controle de Tamanho do Repositório:** Manter o histórico do Git leve, excluindo binários pesados.
*   **Desempenho de Inicialização:** A inicialização do aplicativo em sua versão final empacotada em `.exe` deve ser rápida e eficiente.

---

## Alternativas Consideradas

### Opção 1: Bundling Total no Executável via PyInstaller (`--add-data`)
Compilar o FFmpeg diretamente dentro do arquivo único `Baixador_YouTube.exe`. Durante a inicialização, o PyInstaller extrai temporariamente o FFmpeg para o diretório `_MEIPASS` no disco do usuário e aponta a execução para lá.

*   **Prós:**
    *   Gera um arquivo único `.exe` final absoluto que funciona sozinho.
*   **Contras:**
    *   O tamanho do arquivo `.exe` salta para cerca de **150-200 MB** (devido à compressão).
    *   **Lentidão no Boot:** A cada inicialização, o aplicativo precisa descompactar os executáveis de centenas de megabytes no disco temporário, gerando overhead alto e atrasando a abertura da janela.
    *   Alguns antivírus bloqueiam a execução de arquivos descompactados dinamicamente na pasta Temp.

### Opção 2: Distribuição Modular com Detecção Relativa (Híbrida Portátil)
Manter o FFmpeg fora do repositório Git (adicionado ao `.gitignore`). Implementar no código Python uma busca inteligente por um diretório local relativo chamado `bin/ffmpeg/` na raiz do projeto (ou no mesmo nível do executável `.exe`). Se o FFmpeg for encontrado na pasta local, o script passa o caminho para o `yt-dlp` via configuração `ffmpeg_location`. Se não encontrar, busca no `PATH` global do sistema.

*   **Prós:**
    *   O repositório Git permanece leve (0 bytes de FFmpeg).
    *   O executável final `.exe` abre instantaneamente (menos de 1 segundo), pois não há extração dinâmica de arquivos pesados.
    *   Funciona sem precisar de privilégios de administrador ou configurações no Windows.
*   **Contras:**
    *   Para distribuição, é necessário distribuir uma pasta ZIP (contendo o `.exe` e a pasta `bin/ffmpeg/` ao lado) em vez de um arquivo `.exe` isolado.

### Opção 3: Dependência Exclusiva do Sistema
Não prover auto-detecção local e exigir que o usuário instale o FFmpeg no Windows manualmente e o configure nas Variáveis de Ambiente.

*   **Prós:**
    *   Nenhum esforço de empacotamento ou detecção local.
*   **Contras:**
    *   UX inaceitável para usuários não técnicos. A maioria não conseguirá usar o app para baixar áudios ou vídeos 1080p.

---

## Decisão

Optou-se pela **Opção 2: Distribuição Modular com Detecção Relativa (Híbrida Portátil)**.

Implementou-se no código de inicialização do `baixador.py` o seguinte fluxo de resolução do caminho:
1.  Verifica se a aplicação está rodando em modo compilado (PyInstaller `frozen=True`).
2.  Obtém o caminho absoluto do diretório do executável (ou pasta de desenvolvimento).
3.  Procura pela subpasta `bin/ffmpeg` e escaneia por diretórios criados a partir do extrator oficial (ex: `ffmpeg-*-full_build/bin`) ou pasta `bin` genérica.
4.  Se localizado, atribui o valor à opção `ffmpeg_location` do `yt-dlp`.
5.  Caso contrário, deixa o `yt-dlp` invocar o comando do sistema, esperando que esteja no `PATH`.

O repositório Git ignora explicitamente a pasta `bin/ffmpeg/` no arquivo `.gitignore`.

---

## Consequências

### Positivas:
*   Histórico do Git preservado e leve.
*   O aplicativo final inicia instantaneamente.
*   Portabilidade de execução garantida se empacotado em estrutura zip (ex: `Baixador_YouTube_v1.0.zip` contendo o `.exe` e a subpasta `bin/ffmpeg`).

### Negativas / Riscos:
*   A distribuição exige um arquivo compactado `.zip` em vez de um `.exe` isolado, o que requer uma instrução clara de download e extração para o usuário final no README.
*   **Mitigação:** Documentar claramente as etapas de instalação portátil e fornecer a instrução de descompactação do zip final na página de downloads e no `README.md`.

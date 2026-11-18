# ADR-002: Build e empacotamento do FFmpeg

**Data:** 17 de novembro de 2026  
**Status:** Aceito  
**Escopo:** Distribuicao Windows x64 do CASR Media Download

---

## Contexto

O CASR usa o FFmpeg para fundir faixas separadas de audio e video e para converter audio. As funcoes oferecidas pelo aplicativo precisam de MP3, M4A/AAC, WAV/PCM, FLAC, MP4 e WebM. O executavel externo tambem deve estar disponivel para `yt-dlp`, sem exigir que o usuario configure o `PATH` do Windows.

A build completa de terceiros inclui componentes que o CASR nao usa e pode dificultar a verificacao de origem, licencas e dependencias. Binarios nao devem ser versionados no Git.

## Decisao

Distribuir uma build propria do FFmpeg 9.0.2 para Windows x64, compilada a partir das fontes oficiais e limitada ao runtime necessario:

- Gerar `ffmpeg.exe` e `ffprobe.exe`; nao gerar `ffplay`.
- Manter os codecs, formatos e muxers nativos necessarios ao CASR, incluindo AAC, FLAC, PCM, MP4 e WebM.
- Habilitar `libmp3lame` para codificacao MP3; construir LAME 4.0 sem decoder nem frontend.
- Desabilitar rede, autodeteccao de bibliotecas, documentacao e debug.
- Compilar como bibliotecas compartilhadas, empacotando apenas as DLLs exigidas pelo runtime.
- Nao habilitar GPL ou componentes nonfree. A build e configurada para permanecer sob LGPL.
- Instalar os executaveis e DLLs em `bin/ffmpeg/bin/`, localizacao priorizada pelo `ffmpeg_locator.py`.

O instalador Inno Setup copia somente `bin/ffmpeg/bin/` e `bin/ffmpeg/licenses/`. Ele nao copia `dist/bin` nem a antiga build full. A pasta `bin/ffmpeg/` continua fora do Git.

## Origem e reproducibilidade

O pacote `release/CASR_FFmpeg_9.0.2_Source.zip` deve acompanhar a distribuicao do instalador. Deve conter as fontes correspondentes, licencas, checksums, configuracao e instrucoes de build.

- FFmpeg 9.0.2: SHA-256 `8C3850283EB25FA026482078A04051E0BE17347B09EF81A0849BEC15A96E002E`; assinatura PGP validada com o fingerprint oficial `FCF986EA15E6E293A5644F10B4322F04D67658D8`.
- LAME 4.0: SHA-256 `3DF5124D5AD3A98312FFD7BA6A9B36230E4F8A3E66D3CE0F425E336C32D216EB`. A fonte foi obtida via HTTPS do projeto; nao foi localizada assinatura destacada para esse tarball.
- Toolchain: MSYS2 UCRT64. A receita deve registrar as versoes dos pacotes e as opcoes efetivamente usadas.

Os checksums e as fontes permitem conferir os arquivos recebidos; o arquivo de instrucoes e a configuracao devem permitir repetir a compilacao sem depender da antiga build de terceiros.

## Licencas

O aplicativo permanece sob MIT. Os componentes FFmpeg e LAME mantem suas proprias licencas e avisos, incluidos em `bin/ffmpeg/licenses/`. A distribuicao deve disponibilizar tambem as fontes correspondentes no arquivo separado acima. A presenca do arquivo de fontes e um requisito do script que gera o instalador.

## Validacao da build

Antes de distribuir, verificar:

1. `ffmpeg -buildconf` confirma as opcoes de configuracao e ausencia de GPL/nonfree.
2. `ffmpeg -encoders` lista MP3 via `libmp3lame`, AAC, FLAC e PCM.
3. `ffmpeg -muxers` lista MP4 e WebM; `ffprobe.exe` executa corretamente.
4. Conversoes de teste funcionam para MP3, M4A, WAV e FLAC, e a fusao de faixas funciona para MP4 e WebM.
5. O runtime inicia em Windows sem MSYS2 instalado, usando apenas as DLLs incluidas ou do sistema.
6. Os testes do projeto passam e o instalador nao inclui a antiga build full.

## Consequencias

- O usuario recebe um instalador simples, sem configurar o FFmpeg no sistema.
- O Git permanece sem binarios grandes e sem a build full antiga.
- O conjunto instalado fica menor e mais verificavel, embora ainda inclua as DLLs necessarias.
- A distribuicao precisa manter o arquivo de fontes e os avisos de licenca junto aos binarios.

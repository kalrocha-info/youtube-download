# Estado atual do projeto

**Revisado em:** 18 de novembro de 2026
**Versão do pacote:** 1.0.1
**Produto:** CASR Media Download
**Estado:** MVP funcional; **totalmente validado e pronto para distribuição v1.0.1**.

## Resumo

Aplicativo desktop para Windows, feito em Python/Tkinter, que usa `yt-dlp` para baixar vídeos ou extrair áudio do YouTube. O download acontece em uma thread de trabalho; os eventos de progresso são encaminhados à thread da interface. A transferência pode ser pausada e retomada sem iniciar uma nova operação, e a pasta de destino pode ser aberta pelo aplicativo.

| Área | Estado atual |
|---|---|
| Download de vídeo e extração de áudio | Implementado |
| Validação de URLs e sanitização do nome de arquivo | Implementado |
| Progresso e cancelamento | Implementado |
| Pausar e retomar | Implementado e coberto por testes automatizados |
| Confirmação ao substituir arquivo existente | Implementado; pergunta antes de iniciar a transferência |
| Detecção de instalação anterior | Implementado; permite reinstalar na mesma pasta ou escolher outra |
| Identidade visual CASR | Implementada na janela, no executável e no instalador |
| Abrir pasta de destino | Implementado; usa o Explorador de Arquivos do Windows |
| Busca pelo FFmpeg portátil ou no `PATH` | Implementado; estrutura `bin/ffmpeg/bin/` validada |
| Build do executável Windows | Concluído; smoke test OK |
| ZIP portátil | Gerado em `release/CASR_Media_Download_Portable_v1.0.1.zip` |
| Build do instalador Windows | Concluído; `release/CASRMediaDownloadSetup_v1.0.1.exe` gerado |
| Validação manual em Windows limpo | ✅ Concluída (instalação, download, pausa/retomada/cancelamento) |

## Fluxo de uso

1. Informe uma URL individual do YouTube e selecione o formato e a qualidade.
2. Opcionalmente, escolha a pasta de destino e um nome personalizado.
3. Inicie o download. Se o arquivo final já existir, confirme se deseja substituí-lo; ao recusar, o download é cancelado.
4. O estado e o progresso são exibidos na janela.
5. **Pausar** suspende a thread no próximo callback de progresso do `yt-dlp`; **Retomar** libera essa mesma operação.
6. **Parar** sinaliza o cancelamento. Se o download estiver pausado, também libera a thread para que o cancelamento seja concluído.
7. **Abrir pasta de destino** abre a pasta selecionada no Explorador do Windows.

Ao encontrar uma instalação anterior, o instalador oferece removê-la e reinstalar na mesma pasta ou removê-la e permitir a escolha de outra pasta. A instalação anterior é removida antes da nova instalação; não são mantidas cópias lado a lado.

A pausa é cooperativa: ela é aplicada quando o `yt-dlp` chama o callback de progresso. Não encerra nem recria o download. Áudio e a combinação de faixas de vídeo podem exigir o FFmpeg.

## Organização técnica

| Caminho | Responsabilidade |
|---|---|
| `src/youtube_download/app.py` | Interface Tkinter, identidade visual CASR, thread e encaminhamento de eventos |
| `src/youtube_download/downloader.py` | Validação da URL, sanitização do nome, opções e execução do `yt-dlp` |
| `src/youtube_download/ffmpeg_locator.py` | Localização do FFmpeg |
| `resources/casr_media_download.svg` e `.ico` | Ícone vetorial e arquivo usado pela aplicação e pelo instalador |
| `tests/test_downloader.py` | Testes de validação, opções, eventos, pausa/retomada, cancelamento e pasta de destino |
| `criar_executavel.ps1` | Instala/atualiza dependências na `.venv` e gera o executável com PyInstaller |
| `criar_instalador.ps1` | Gera o instalador com Inno Setup e inclui o FFmpeg portátil quando disponível |
| `installer/` | Configuração do instalador Inno Setup |

### Comunicação com a interface

O worker não atualiza widgets Tkinter. Ele coloca eventos em uma fila; a thread principal consome a fila usando `after()` e atualiza o progresso, o status e os botões. A pausa e o cancelamento são coordenados por `threading.Event`.

## Dependências e execução

- Windows; Python 3.10 ou superior.
- Dependência de execução: `yt-dlp>=2026.3.14`, conforme `pyproject.toml`.
- PyInstaller é dependência opcional de desenvolvimento/build.
- FFmpeg é necessário para conversão de áudio e para combinar faixas separadas de vídeo e áudio. Pode estar em `bin/ffmpeg/` ou no `PATH`.
- O aplicativo pode ser iniciado em ambiente de desenvolvimento com `python -m youtube_download`.
- O projeto usa uma única `.venv` na raiz; os scripts de build também reutilizam esse ambiente ou o criam se estiver ausente.

## Diagnóstico do WinError 448

Foi identificado que downloads em MP3 falhavam quando o `PATH` do Windows incluía um caminho do NVM e a saída era direcionada a pastas do usuário. O erro vinha da resolução desse caminho, não da pasta de destino.

O `yt-dlp` busca o runtime JavaScript Deno por padrão e, na busca automática, resolve os diretórios do `PATH`; isso pode falhar ao atravessar links do NVM no executável instalado. O aplicativo agora passa caminhos explícitos dos runtimes disponíveis ao `yt-dlp` e desativa a busca implícita quando nenhum é encontrado. Erros de sistema não relacionados à criação da pasta também deixaram de ser apresentados como falha do destino.

## Validação registrada

- 22 testes automatizados passaram, incluindo os novos fluxos de confirmação e cancelamento de substituição.
- Ruff e `git diff --check` passaram.
- `python -m compileall -q src\youtube_download` passou sem erros.
- Tkinter carregou o ícone multirresolução.
- Executável `dist\CASR_Media_Download.exe` gerado com sucesso (~20 MB).
- Smoke test do executável: iniciou e finalizou corretamente.
- Modo desenvolvimento `python -m youtube_download`: iniciou corretamente.
- FFmpeg locator resolve `bin/ffmpeg/bin` tanto no executável quanto no ZIP portátil.
- ZIP portátil `release/CASR_Media_Download_Portable_v1.0.1.zip` gerado com estrutura correta.
- Instalador `release/CASRMediaDownloadSetup_v1.0.1.exe` compilado com sucesso pelo Inno Setup 6.7.3.
- **Validação manual em Windows limpo: CONCLUÍDA** — instalação, download (áudio/vídeo), pausa, retomada, cancelamento durante pausa e detecção de instalação anterior funcionaram corretamente.

Comandos de validação:

```powershell
python -m unittest discover -s tests
python -m compileall -q src\youtube_download
ruff check src tests
```

## Build e distribuição

1. Instale Python 3.10+ e, para o instalador, Inno Setup 6.
2. Execute `.\criar_executavel.ps1`. O executável será gerado em `dist\CASR_Media_Download.exe`.
3. Para uma distribuição portátil, use `release\CASR_Media_Download_Portable_v1.0.1.zip` (contém executável + `bin/ffmpeg/`). O FFmpeg não é embutido no `.exe`.
4. Execute `.\criar_instalador.ps1`. O script procura o Inno Setup e gera `release\CASRMediaDownloadSetup_v1.0.1.exe`.
5. Antes de publicar, teste a instalação e os controles de download em um Windows limpo.

## Próximos passos

- Considerar, para versões futuras, fila e histórico de downloads; não fazem parte do MVP atual.

## Documentação relacionada

- [README.md](../README.md): instalação, uso, testes e build.
- [CONTRIBUTING.md](../CONTRIBUTING.md): branches, commits e Pull Requests.
- [ADR-002-Empacotamento-FFmpeg.md](./ADR-002-Empacotamento-FFmpeg.md): decisão de empacotamento do FFmpeg.
# Estado atual do projeto

**Revisado em:** 13 de novembro de 2026
**Versão do pacote:** 1.0.0
**Estado:** MVP funcional; a próxima distribuição deve ser reconstruída e validada com o código atual.

## Resumo

Aplicativo desktop para Windows, feito em Python/Tkinter, que usa `yt-dlp` para baixar vídeos ou extrair áudio do YouTube. O download acontece em uma thread de trabalho; os eventos de progresso são encaminhados à thread da interface. A transferência pode ser pausada e retomada sem iniciar uma nova operação, e a pasta de destino pode ser aberta pelo aplicativo.

| Área | Estado atual |
|---|---|
| Download de vídeo e extração de áudio | Implementado |
| Validação de URLs e sanitização do nome de arquivo | Implementado |
| Progresso e cancelamento | Implementado |
| Pausar e retomar | Implementado e coberto por testes automatizados |
| Abrir pasta de destino | Implementado; usa o Explorador de Arquivos do Windows |
| Busca pelo FFmpeg portátil ou no `PATH` | Implementado |
| Build do executável e instalador Windows | Scripts disponíveis; artefatos existentes precisam ser reconstruídos após as alterações recentes |

## Fluxo de uso

1. Informe uma URL individual do YouTube e selecione o formato e a qualidade.
2. Opcionalmente, escolha a pasta de destino e um nome personalizado.
3. Inicie o download. O estado e o progresso são exibidos na janela.
4. **Pausar** suspende a thread no próximo callback de progresso do `yt-dlp`; **Retomar** libera essa mesma operação.
5. **Parar** sinaliza o cancelamento. Se o download estiver pausado, também libera a thread para que o cancelamento seja concluído.
6. **Abrir pasta de destino** abre a pasta selecionada no Explorador do Windows.

A pausa é cooperativa: ela é aplicada quando o `yt-dlp` chama o callback de progresso. Não encerra nem recria o download. Áudio e a combinação de faixas de vídeo podem exigir o FFmpeg.

## Organização técnica

| Caminho | Responsabilidade |
|---|---|
| `src/youtube_download/app.py` | Interface Tkinter, thread de download e encaminhamento de eventos para a interface |
| `src/youtube_download/downloader.py` | Validação da URL, sanitização do nome, opções e execução do `yt-dlp` |
| `src/youtube_download/ffmpeg_locator.py` | Localização do FFmpeg |
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

## Validação registrada

- 14 testes automatizados passaram na validação mais recente, incluindo os fluxos de pausa, retomada, cancelamento durante pausa e abertura da pasta.
- Ruff, `py_compile` e `git diff --check` passaram na mesma validação.
- Um teste real de download produziu um MP4 em 480p usando `yt-dlp 2026.10.26` e FFmpeg. Em uma tentativa anterior, `yt-dlp 2026.6.9` recebeu HTTP 403; esse resultado isolado não determina que a versão antiga falhe em todos os ambientes.
- O usuário confirmou o funcionamento dos fluxos de vídeo, áudio, interrupção e início de um novo download após a interrupção.
- Os testes automatizados não substituem a validação do executável/instalador em uma instalação limpa do Windows. Os artefatos existentes não foram reconstruídos depois das últimas alterações.

Comandos de validação:

```powershell
python -m unittest discover -s tests
python -m py_compile src/youtube_download/*.py
ruff check src tests
```

## Build e distribuição

1. Instale Python 3.10+ e, para o instalador, Inno Setup 6.
2. Execute `.\criar_executavel.ps1`. O executável será gerado em `dist\Baixador_YouTube.exe`.
3. Para uma distribuição portátil, mantenha `bin\ffmpeg\` junto do executável. O FFmpeg não é embutido no `.exe`.
4. Execute `.\criar_instalador.ps1`. O script procura o Inno Setup, copia `bin\` para `dist\` se necessário e gera `release\MediaDownloadWindowsSetup_v1.0.0.exe`.
5. Antes de publicar uma nova versão, reconstrua os artefatos e teste a instalação e os controles de download em um Windows limpo.

## Próximos passos

- Reconstruir e testar o `.exe` e o instalador com o código atual.
- Validar manualmente pausa, retomada e cancelamento durante uma pausa na interface empacotada.
- Considerar, para versões futuras, fila e histórico de downloads; não fazem parte do MVP atual.

## Documentação relacionada

- [README.md](../README.md): instalação, uso, testes e build.
- [CONTRIBUTING.md](../CONTRIBUTING.md): branches, commits e Pull Requests.
- [ADR-002-Empacotamento-FFmpeg.md](./ADR-002-Empacotamento-FFmpeg.md): decisão de empacotamento do FFmpeg.

# ADR-001: Desacoplamento da Lógica de Negócios e Interface Gráfica (Refatoração de Arquitetura)

**Data:** 13 de junho de 2026  
**Status:** Proposto  
**Decisores:** Time Técnico do Projeto (Senior Architect)  

---

## Contexto

Atualmente, o projeto é estruturado em um único script monolítico `src/baixador.py` com cerca de 250 linhas de código. Esse arquivo acumula múltiplas responsabilidades:
1.  Definição e estilização da interface gráfica usando Tkinter.
2.  Manipulação e captura direta de estados dos campos da GUI.
3.  Resolução e varredura de caminhos de arquivos locais (como a pasta binária do FFmpeg).
4.  Criação e execução de threads de processamento secundário.
5.  Configuração, parametrização e chamada direta à biblioteca externa `yt-dlp`.
6.  Atualização de elementos gráficos no meio de loops de download.

Essa mistura de responsabilidades (alto acoplamento) viola o Princípio de Responsabilidade Única (SRP) e cria barreiras graves para a evolução técnica do projeto:
*   **Impossibilidade de testes:** Escrever testes automatizados para a lógica de download (comportamentos do `yt-dlp`, formatação de opções) exige instanciar a interface Tkinter inteira, impedindo testes de unidade limpos.
*   **Dificuldade de manutenção:** Alterar aspectos visuais ou comportamentais na UI exige alterar o mesmo arquivo que manipula downloads, aumentando o risco de introdução de bugs.

---

## Direcionadores da Decisão

*   **Testabilidade:** O código de download e conversão deve poder ser testado em isolation por frameworks como o `pytest`.
*   **Manutenibilidade:** Separação de responsabilidades para que alterações visuais (UI) não quebrem o motor de download.
*   **Escalabilidade do código:** Suporte a futuras features planejadas (como fila de download e banco de dados SQLite para histórico) sem gerar um arquivo gigante e incompreensível.

---

## Alternativas Consideradas

### Opção 1: Manter a estrutura monolítica em um único script (`baixador.py`)
*   **Prós:**
    *   Simplicidade de arquivo único (fácil compartilhamento de script bruto).
    *   Desenvolvimento ágil e rápido para escopos minúsculos (MVP).
*   **Contras:**
    *   Sem possibilidade de testes automatizados unitários.
    *   Difícil leitura e crescimento insustentável.

### Opção 2: Refatoração para Arquitetura Multicamadas Desacoplada
Separar o script em pelo menos duas classes/módulos distintos:
1.  `downloader.py` (ou `services/downloader.py`): Classe de serviço independente que gerencia apenas a interface com o `yt-dlp`, define as opções de formato, configura os hooks de progresso e executa a lógica de download pura.
2.  `gui.py` (ou `src/baixador.py` modificado): Responsável puramente pela criação da janela Tkinter, botões, entradas e recepção de feedbacks por callbacks ou eventos.

*   **Prós:**
    *   Divisão clara de responsabilidades (arquitetura MVC ou Service/View).
    *   Permite mockar a classe de download e testá-la unitariamente em terminal ou CI/CD.
    *   Código extensível e legível.
*   **Contras:**
    *   Pequeno aumento inicial no número de arquivos.
    *   Necessidade de estabelecer uma interface de comunicação limpa entre a UI e o downloader (ex: passagem de hooks de progresso por callbacks).

---

## Decisão

Optou-se pela **Opção 2: Refatoração para Arquitetura Multicamadas Desacoplada**.

A refatoração será estruturada na próxima fase de desenvolvimento técnico. A lógica contida hoje na função `baixar_thread()` será exportada para uma classe especialista de serviço de downloads que recebe os parâmetros e um callback de progresso, isolando completamente o Tkinter da biblioteca `yt-dlp`.

---

## Consequências

### Positivas:
*   Código preparado para testes unitários (ex: verificar se as opções do `yt-dlp` são configuradas corretamente para formatos MP3 ou qualidades de vídeo diferentes).
*   Facilidade de migrar ou substituir a interface gráfica no futuro (ex: migrar do Tkinter para CustomTkinter ou PySide/PyQt) sem tocar na lógica de download.
*   Conformidade com padrões modernos de arquitetura de software desktop.

### Negativas / Riscos:
*   Esforço inicial de refatoração para reescrever as funções e testar a integridade funcional do aplicativo.
*   **Mitigação:** Criar uma branch dedicada de desenvolvimento (`refactor/desacoplamento-ui`) e homologar o comportamento manual detalhadamente antes do merge para a branch `develop`.

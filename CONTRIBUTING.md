# Guia de Contribuição: CASR Media Download

Agradecemos por seu interesse em contribuir para o projeto **CASR Media Download**! Para manter a qualidade do código, a legibilidade do histórico de alterações e a estabilidade do produto, estabelecemos as seguintes diretrizes.

---

## 🚦 Convenção de Commits

Adotamos a especificação de [Conventional Commits](https://www.conventionalcommits.org/pt-br/) para todas as mensagens de commit no repositório. Isso torna o histórico legível e facilita a geração automatizada de CHANGELOGs.

O formato padrão de mensagem é:
```
<tipo>(escopo): <descrição curta em português>
```

### Tipos Permitidos
*   `feat`: Adição de uma nova funcionalidade (ex: adicionar suporte a um novo formato ou interface escura).
*   `fix`: Correção de um bug (ex: corrigir um travamento de download ou erro do FFmpeg).
*   `docs`: Alterações exclusivas na documentação (ex: atualizar o README ou criar um ADR).
*   `refactor`: Alterações de código que não corrigem bugs nem adicionam funcionalidades, focadas em melhorar a estrutura (ex: separar a UI do yt-dlp).
*   `test`: Adição ou modificação de testes automatizados.
*   `style`: Alterações de formatação de código que não afetam a execução (ex: espaçamento PEP 8).
*   `chore`: Tarefas de manutenção ou automação (ex: atualizar o `.gitignore` ou dependências do `requirements.txt`).

### Exemplos
*   `feat(gui): adiciona botão para alternar entre modo claro e escuro`
*   `fix(ytdlp): trata erro de download de link inválido com mensagem clara`
*   `docs(readme): adiciona instruções para compilação com PyInstaller`
*   `refactor(core): extrai a lógica de download de baixar_thread para módulo de serviço`

---

## 🌿 Estratégia de Branches (Fluxo Git)

O fluxo atual usa `main` como branch estável e branches de trabalho para alterações:

1.  **`main`**: Rastreia o código estável e é o destino dos Pull Requests.
2.  **Branches de Trabalho**: Devem ser criadas a partir da versão mais recente de `main`, seguindo o padrão:
    *   `feat/[nome-curto]` para novas funcionalidades.
    *   `fix/[nome-curto]` para correção de falhas.
    *   `docs/[nome-curto]` para edições de documentação.

### Fluxo para envio de alterações:
1.  Atualize `main` e crie uma branch de trabalho:
    ```powershell
    git switch main
    git pull origin main
    git switch -c docs/atualiza-documentacao
    ```
2.  Faça as alterações e os testes relacionados. Comente apenas lógicas que precisem de esclarecimento.
3.  Crie commits organizados seguindo a Convenção de Commits.
4.  Publique a branch (`git push -u origin docs/atualiza-documentacao`).
5.  Abra um **Pull Request (PR)** da branch de trabalho para `main`.

---

## 🔧 Padrões de Código (Clean Code)

*   **Formatação PEP 8:** O código Python deve seguir as diretrizes oficiais da PEP 8. Recomendamos configurar os formatadores `black` ou `ruff` na sua IDE.
*   **Limitação de Tamanho:**
    *   Mantenha arquivos (`.py`) abaixo de **500 linhas**. Se passar disso, extraia responsabilidades em novos módulos.
    *   Evite funções com mais de **50 linhas** de código. Quebre funções gigantes (como era a antiga `baixar_thread()`) em subfunções menores e especialistas.
*   **Desacoplamento:** Não misture lógica de exibição gráfica (como Tkinter `messagebox` ou `.config()`) dentro de classes e métodos que executam cálculos, processamento de rede ou manipulação do `yt-dlp`. Use callbacks ou eventos para comunicação.
*   **Evite Variáveis Globais:** Utilize classes, injeção de dependências e escopos locais para gerenciamento de estado.

# US College Research Tool

Ferramenta de pesquisa profunda sobre faculdades dos EUA para quem está aplicando para **undergrad**.

## Arquitetura em Três Camadas

```
┌─────────────────────────────────────────────────────────────────────┐
│  Plugin (.claude-plugin/)                                           │
│  Skills (interpretação de dados + orquestração web)                 │
│  Commands (/pesquisar-faculdade, /comparar, /professores, etc.)     │
├──────────────────┬────────────────────────┬─────────────────────────┤
│  MCP Server      │  Firecrawl MCP         │  Exa MCP                │
│  (nosso)         │  (terceiro)            │  (terceiro)             │
│                  │                        │                         │
│  Dados           │  Web search +          │  Busca semântica        │
│  estruturados    │  scraping              │  neural                 │
│  e verificados   │                        │                         │
└──────────────────┴────────────────────────┴─────────────────────────┘
```

- **Camada 1 — MCP Server próprio**: Dados oficiais com proveniência (College Scorecard, ORCID, Semantic Scholar). Fonte de verdade para métricas institucionais.
- **Camada 2 — Servidores MCP de pesquisa web**: Firecrawl (scraping/crawling) e Exa (busca semântica) rodam lado a lado. Servem para descoberta — encontrar páginas de faculty, oportunidades, programas.
- **Camada 3 — Plugin**: Skills ensinam o Claude quando usar qual fonte; commands expõem fluxos conversacionais.

## O que junta, por universidade:

1. **Dados oficiais** de admissão, custo e retorno financeiro (College Scorecard API — Dept. of Education)
2. **Corpo docente** de um departamento (scraper configurável por universidade)
3. **Pesquisa acadêmica** de cada professor (ORCID + Semantic Scholar — papers recentes, citações, desambiguação por afiliação)
4. **Oportunidades na universidade** (incubadoras, pesquisa undergrad, clubes, competições — curado de sites oficiais)
5. **Career outcomes** (dados agregados de relatórios oficiais pós-graduação)
6. **Trajetória de alumni** (links prontos para a ferramenta oficial LinkedIn Alumni, filtrados por empresa/cargo/localização)

Suporta **modo batch** para gerar relatórios de várias universidades + tabela comparativa lado a lado.

## Setup

### Requisitos

- Python 3.10+
- Chave de API do College Scorecard (gratuita)

### Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Chaves de API

| Chave | Obrigatória | Onde obter | O que ganha |
|-------|-------------|-----------|-------------|
| `COLLEGE_SCORECARD_API_KEY` | **Sim** | https://api.data.gov/signup/ | Dados institucionais (admissão, custo, earnings) |
| `SEMANTIC_SCHOLAR_API_KEY` | Não | https://www.semanticscholar.org/product/api#api-key-form | Rate limit maior para pesquisa de professores |
| `FIRECRAWL_API_KEY` | Não | https://www.firecrawl.dev/app/api-keys | Rate limit maior para web search/scraping |
| `EXA_API_KEY` | Não | https://dashboard.exa.ai/api-keys | Remove rate limits de busca semântica |

**Sem as chaves opcionais**, tudo continua funcionando — Firecrawl e Exa têm free tier sem key, e Semantic Scholar funciona com rate limit menor.

### Nota de Privacidade

Firecrawl (`mcp.firecrawl.dev`) e Exa (`mcp.exa.ai`) são serviços remotos de terceiros. Quando você usa pesquisa web via este plugin, suas queries são enviadas para esses serviços. Isso é necessário para a funcionalidade de descoberta e é o comportamento padrão de qualquer ferramenta de busca web. Não envie informações pessoais identificáveis desnecessárias em queries de busca.

## Uso

### Via CLI (modo original)

```bash
# Relatório single (uma universidade)
python main.py "Northwestern University" --faculty-config northwestern_cs --field "Computer Science"

# Com ranking por interesse do aluno
python main.py "Northwestern University" --faculty-config northwestern_cs --interests "human-computer interaction" "entrepreneurship"

# Gerar HTML legível no navegador
python main.py "Northwestern University" --faculty-config northwestern_cs --html

# Modo batch (todas da watchlist + comparativo)
python main.py --batch --interests "HCI" --html
```

### Via Claude Code (plugin)

```
/pesquisar-faculdade Northwestern University
/comparar Northwestern University MIT
/professores Northwestern University --foco human-computer interaction
/oportunidades Northwestern University
/adicionar-faculdade Carnegie Mellon University
/atualizar-oportunidades Carnegie Mellon University
```

## Commands

| Comando | O que faz |
|---------|-----------|
| `/pesquisar-faculdade <nome>` | Relatório completo de uma universidade |
| `/comparar <uni1> <uni2> [uni3...]` | Comparação lado a lado |
| `/professores <uni> --foco <área>` | Professores ranqueados por interesse |
| `/oportunidades <uni>` | Oportunidades curadas (incubadoras, pesquisa, clubes) |
| `/adicionar-faculdade <nome ou url>` | Fluxo conversacional para configurar faculty scraping |
| `/atualizar-oportunidades <uni>` | Busca e propõe novas oportunidades via web |

Comandos que escrevem em disco (`/adicionar-faculdade`, `/atualizar-oportunidades`) **sempre pedem confirmação antes de salvar**.

## MCP Tools (14 tools)

### Discovery
- `search_university` — busca universidades por nome no College Scorecard
- `list_configured_departments` — lista configs de faculty disponíveis

### Institutional Data
- `get_university_overview` — métricas completas (admissão, custo, earnings) com proveniência
- `get_opportunities` — oportunidades curadas de uma universidade
- `get_alumni_research_links` — URLs do LinkedIn Alumni Tool
- `get_career_outcomes` — dados de carreira pós-graduação

### Faculty & Research
- `list_faculty` — lista paginada de professores de um departamento
- `get_professor_research` — perfil de pesquisa (ORCID + Semantic Scholar) com confidence scoring
- `match_professors_to_interests` — rankeia professores por relevância a interesses

### Consolidation
- `generate_full_report` — relatório completo orquestrando todas as fontes
- `compare_universities` — comparativo de múltiplas universidades

### Scaling
- `draft_faculty_config` — propõe seletores CSS a partir de uma URL de faculty
- `validate_faculty_config` — testa se um config existente funciona
- `draft_opportunities` — propõe bloco de oportunidades a partir de conteúdo web

## Skills

### Data Interpretation
Ensina o Claude a interpretar dados corretamente:
- h-index baixo em Lecturer não é sinal negativo
- Sempre usar net price, nunca sticker price isolado
- Earnings são médias institucionais, não por área
- Dados do Scorecard têm defasagem (citar ano)
- Não hierarquizar universidades nem prever admissão

### Web Orchestration
Ensina quando usar pesquisa web vs. dados estruturados:
- Métricas institucionais → sempre do nosso server
- Descoberta de páginas/programas → pesquisa web
- Se dado estruturado está ausente → "não disponível", não buscar na web
- Toda info de web search vem com link da fonte

## Configurando uma nova universidade

### Via plugin (recomendado)
```
/adicionar-faculdade Carnegie Mellon University
```
O Claude busca a página de faculty, propõe seletores, mostra uma amostra, e salva após sua aprovação.

### Manualmente

1. Abra a página de faculty do departamento no navegador
2. Inspecione o HTML e identifique os seletores CSS
3. Adicione um bloco em `data/faculty_configs.json`
4. Teste: `python -m src.faculty_scraper <sua_chave>`

### Oportunidades
```
/atualizar-oportunidades Carnegie Mellon University
```
Ou adicione manualmente em `data/opportunities.json` com dados curados do site oficial.

## Testes

```bash
pip install -r requirements-dev.txt

# Pytest (37 testes unitários)
python -m pytest tests/ -v

# Smoke test do MCP server (37 testes de aceitação)
python scripts/smoke_test_mcp.py
```

## Limitações Conhecidas

- **Cobertura geográfica**: College Scorecard cobre apenas instituições dos EUA. Universidades de outros países retornam `OUT_OF_SCOPE`.
- **Defasagem de dados**: Dados do Scorecard tipicamente têm 2-3 anos de atraso. O campo `reference_year` indica o ano real.
- **Faculty config é semi-manual**: `draft_faculty_config` propõe seletores automaticamente, mas páginas com rendering JavaScript não são suportadas. Algumas universidades precisam de configuração manual.
- **Homônimos**: Professores com nomes comuns podem ter match incorreto. O campo `identification_confidence` sinaliza isso, mas não resolve 100%.
- **Pesquisa web ≠ dado verificado**: Informações obtidas via Firecrawl/Exa não têm a mesma garantia de proveniência que dados do College Scorecard ou ORCID. O campo `extraction_basis` classifica a confiabilidade da fonte.
- **Oportunidades desatualizam**: Programas mudam, URLs quebram. Dados curados em `opportunities.json` precisam de revisão periódica.

## Exemplos de Conversas que Funcionam Bem

**"Compare Northwestern e MIT pra quem quer HCI e empreendedorismo"**
→ `/comparar Northwestern University MIT` + contextualização de faculty HCI e programas de empreendedorismo

**"Adiciona a Carnegie Mellon"**
→ `/adicionar-faculdade Carnegie Mellon University` → busca página de faculty → propõe config → confirma

**"Quais oportunidades de empreendedorismo a Northwestern tem pra undergrad, com fontes"**
→ `/oportunidades Northwestern University` → mostra tudo com URLs oficiais

## Estrutura do Projeto

```
├── main.py                       # CLI com barra de progresso (rich)
├── mcp_server/
│   ├── __init__.py
│   ├── __main__.py               # Entry point: python -m mcp_server
│   └── server.py                 # 14 MCP tools + 3 resources
├── .claude-plugin/
│   ├── plugin.json               # Manifesto do plugin
│   ├── .mcp.json                 # Configuração dos 3 MCP servers
│   ├── skills/
│   │   ├── data-interpretation.md
│   │   └── web-orchestration.md
│   └── commands/
│       ├── pesquisar-faculdade.md
│       ├── comparar.md
│       ├── professores.md
│       ├── oportunidades.md
│       ├── adicionar-faculdade.md
│       └── atualizar-oportunidades.md
├── src/                          # Módulos core
├── data/                         # Dados curados (JSON)
├── scripts/                      # Smoke test
├── tests/                        # Pytest (37 testes)
├── output/                       # Relatórios gerados
├── requirements.txt
└── requirements-dev.txt
```

## Design Decisions

- **ORCID como fonte primária** para pesquisa acadêmica — resolve homônimos via afiliação institucional confirmada. Semantic Scholar é fallback.
- **Sem scraping do LinkedIn** — viola ToS e privacidade. O módulo de alumni gera URLs da ferramenta oficial para navegação manual.
- **Cache SQLite** — evita bater APIs repetidamente. TTL configurável por fonte (30 dias Scorecard, 7 dias pesquisa).
- **Degradação graceful** — erros de rede em qualquer seção não derrubam o relatório; a seção falha isoladamente com mensagem explicativa.
- **MCP servers lado a lado** — nosso servidor não chama Firecrawl/Exa diretamente. O modelo orquestra; as skills ensinam como.
- **Taxonomia de erro padronizada** — `NOT_FOUND`, `NOT_CONFIGURED`, `OUT_OF_SCOPE`, `UPSTREAM_ERROR`, `RATE_LIMITED`, `AMBIGUOUS`.
- **Proveniência em todos os dados** — `source` + `reference_year` em toda métrica retornada.

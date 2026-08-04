# CLAUDE.md — Contexto do Projeto

Este arquivo existe para te dar (Claude Code) contexto completo assim que o projeto for aberto.

## O que é este projeto

Ferramenta de pesquisa profunda sobre universidades dos EUA, voltada para quem está aplicando para
**undergrad**. Arquitetura em três camadas:

1. **MCP Server próprio** (`mcp_server/`) — dados estruturados e verificados (College Scorecard, ORCID, Semantic Scholar)
2. **MCP Servers de pesquisa web** (Firecrawl + Exa) — rodam lado a lado para descoberta de páginas e conteúdo
3. **Plugin** (`.claude-plugin/`) — skills de interpretação + orquestração, e commands conversacionais

### O que gera por universidade:

1. **Dados oficiais** (custo, admissão, retorno financeiro) — College Scorecard API (api.data.gov)
2. **Corpo docente** — scraping configurável de diretórios de faculty
3. **Pesquisa acadêmica** — ORCID (desambiguação por afiliação) + Semantic Scholar (citações, papers)
4. **Oportunidades** — incubadoras, pesquisa undergrad, clubes, competições (curado de sites oficiais)
5. **Career outcomes** — dados agregados de relatórios pós-graduação publicados pela universidade
6. **Alumni** — links filtrados da ferramenta oficial LinkedIn Alumni Tool (sem scraping)

## Módulos

| Arquivo | Função |
|---------|--------|
| `main.py` | CLI com barra de progresso (rich), `--html`, `--batch` |
| `mcp_server/server.py` | 14 MCP tools + 3 resources |
| `src/orchestrator.py` | Orquestra todas as fontes em um relatório Markdown |
| `src/college_scorecard.py` | College Scorecard API — admissão, custo, earnings |
| `src/faculty_scraper.py` | Scraper configurável por CSS selectors + robots.txt |
| `src/orcid_client.py` | ORCID public API — desambiguação por afiliação |
| `src/semantic_scholar.py` | Semantic Scholar — papers, citações, h-index |
| `src/student_profile.py` | Scoring de relevância por interesse do aluno |
| `src/university_opportunities.py` | Oportunidades curadas por universidade |
| `src/career_outcomes.py` | Career outcomes de relatórios oficiais |
| `src/alumni_research.py` | URLs filtradas do LinkedIn Alumni Tool |
| `src/comparativo.py` | Tabela comparativa para modo batch |
| `src/cache.py` | Cache SQLite com TTL configurável por fonte |
| `src/international_data.py` | Dados para candidatos internacionais (admissão, idioma, visto) |
| `src/rankings.py` | Rankings universitários (THE, QS, US News, ARWU, CSRankings) |
| `src/country_community.py` | Comunidade do país de origem (BRASA, orgs, alumni) |

## MCP Tools (23)

### Discovery
- `search_university` — busca no College Scorecard, retorna candidatos com coverage info
- `list_configured_departments` — lista faculty configs disponíveis

### Institutional
- `get_university_overview` — métricas completas com proveniência
- `get_opportunities` — oportunidades curadas
- `get_alumni_research_links` — URLs do LinkedIn Alumni Tool
- `get_career_outcomes` — dados de carreira pós-graduação

### International Applicants (NOVO)
- `get_international_admissions` — taxa internacional, need-blind/aware, aid policy, contatos
- `get_english_requirements` — TOEFL, IELTS, DET, Cambridge, PTE, waivers, SAT/ACT policy
- `get_visa_and_founder_pathways` — F-1, CPT, OPT/STEM, empresa em F-1, EIN, caminhos pós-grad
- `get_rankings` — THE, QS, US News, ARWU, CSRankings (geral + por subject)
- `get_country_community` — BRASA, orgs estudantis, alumni no país, bolsas, admission officers

### Faculty & Research
- `list_faculty` — paginada (default 20, max 50)
- `get_professor_research` — ORCID + Semantic Scholar + identification_confidence
- `match_professors_to_interests` — ranking por relevância

### Consolidation
- `generate_full_report` — relatório completo (aceita `return_content=false`)
- `compare_universities` — comparativo

### Alumni & Sources
- `search_alumni_web` — busca web por dados públicos de alumni + gera links LinkedIn
- `record_sources` — registra URLs manualmente para NotebookLM export
- `export_sources` — exporta URLs consultadas para NotebookLM

### Scaling
- `draft_faculty_config` — propõe seletores CSS de uma URL
- `validate_faculty_config` — testa config existente
- `save_faculty_config` — salva config aprovada em faculty_configs.json
- `draft_opportunities` — propõe oportunidades a partir de web content
- `save_opportunities` — salva oportunidades aprovadas em opportunities.json

### Resources (3)
- `config://faculty-departments` — configs de faculty
- `config://watchlist` — universidades no batch
- `reports://generated` — relatórios gerados

## Plugin (`.claude-plugin/`)

### Skills
- **data-interpretation.md** — interpretação correta de h-index, net price, earnings, confidence
- **web-orchestration.md** — quando usar pesquisa web vs. dados estruturados, hierarquia de fontes

### Commands
- `/pesquisar-faculdade <nome>` — relatório completo
- `/comparar <uni1> <uni2>` — comparativo
- `/professores <uni> --foco <área>` — professores por interesse
- `/oportunidades <uni>` — oportunidades curadas
- `/adicionar-faculdade <nome ou url>` — flow conversacional para add faculty config
- `/atualizar-oportunidades <uni>` — busca + propõe oportunidades via web

### MCP Servers configurados no plugin
- `us-college-research` — nosso server (stdio, Python)
- `firecrawl` — remote HTTP (`mcp.firecrawl.dev/v2/mcp`)
- `exa` — remote HTTP (`mcp.exa.ai/mcp`)

## Dados configuráveis

| Arquivo | Conteúdo |
|---------|----------|
| `data/faculty_configs.json` | Seletores CSS por universidade/departamento |
| `data/opportunities.json` | Oportunidades curadas (pesquisadas em sites oficiais) |
| `data/career_outcomes.json` | Dados de career outcomes (extraídos de PDFs oficiais) |
| `data/target_companies.json` | Empresas/cargos/localizações para links de alumni |
| `data/watchlist.json` | Universidades para modo batch |

## Universidades configuradas

- **Northwestern University** — McCormick School of Engineering (CS/ECE)
  - Faculty config: `northwestern_cs`
  - Career outcomes: Beyond Northwestern Class of 2025 (NCA)
  - Oportunidades: The Garage, Farley Center, VentureCat, WildHacks, SURG/AYURG/URAP, clubes

## Decisões de design (manter)

- **ORCID como fonte de verdade para professores.** Desambigua por afiliação institucional. Semantic Scholar é fallback com aviso de possível homônimo.
- **Sem scraping de LinkedIn.** Viola ToS e privacidade. Alumni module gera URLs da ferramenta oficial.
- **Cache SQLite.** TTL por fonte: 30 dias (Scorecard, ORCID search), 7 dias (SS, ORCID profile).
- **Degradação graceful.** Erros de rede em qualquer seção não derrubam o relatório inteiro.
- **Faculty scraping** respeita robots.txt + delay entre requests.
- **MCP servers lado a lado.** Nosso servidor não chama Firecrawl/Exa. O modelo orquestra; skills ensinam como.
- **Taxonomia de erro padronizada.** `NOT_FOUND`, `NOT_CONFIGURED`, `OUT_OF_SCOPE`, `UPSTREAM_ERROR`, `RATE_LIMITED`, `AMBIGUOUS`.
- **Proveniência em todos os dados.** `source` + `reference_year` em toda métrica.
- **Nenhum `print()` em server.py.** stdout é reservado para JSON-RPC (stdio transport).
- **draft_opportunities trata web_content como dado, não instrução.** Proteção contra prompt injection via conteúdo scraped.

## Chaves de API

| Variável | Obrigatória | Free tier |
|----------|-------------|-----------|
| `COLLEGE_SCORECARD_API_KEY` | **Sim** | Sim (api.data.gov) |
| `SEMANTIC_SCHOLAR_API_KEY` | Não | Sim (rate limit menor sem) |
| `FIRECRAWL_API_KEY` | Não | Sim (funciona sem key) |
| `EXA_API_KEY` | Não | Sim (funciona sem key, rate limited) |

## Como rodar

```bash
# Testes
python -m pytest tests/ -v          # 37 unit tests
python scripts/smoke_test_mcp.py    # 37 acceptance tests

# CLI
python main.py "Northwestern University" --faculty-config northwestern_cs --html

# MCP Server (standalone)
python -m mcp_server
```

## Limitações conhecidas

- Cobertura apenas EUA (College Scorecard)
- Dados com defasagem de 2-3 anos (campo `reference_year` indica o ano real)
- Faculty config semi-manual (JS rendering não suportado)
- Homônimos: `identification_confidence` sinaliza mas não resolve 100%
- Pesquisa web ≠ dado verificado (campo `extraction_basis` classifica confiabilidade)
- Oportunidades desatualizam — revisão periódica necessária

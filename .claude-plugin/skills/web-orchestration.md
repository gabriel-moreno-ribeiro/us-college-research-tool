# Skill: Orchestrating Web Search with Structured Data

This skill teaches you when to use which data source and how to combine web search results with the structured data from the US College Research Tool.

## The Core Principle

**Structured data from our MCP server is the source of truth for institutional metrics.** Web search is for discovery and qualitative context — never for replacing or filling gaps in structured data.

## Source Hierarchy

### Always from `us-college-research` server (never from web search):
- Admission rates
- Net price / cost of attendance
- Post-graduation earnings
- Enrollment numbers
- Faculty lists and research profiles
- Any metric with provenance metadata (source + reference_year)

### Web search is appropriate for:
- Discovering URLs of faculty pages (to feed into `draft_faculty_config`)
- Finding opportunities, programs, clubs, incubators (to feed into `draft_opportunities`)
- Qualitative context about departments, culture, student experience
- Recent news about a university
- Specific program details not in Scorecard (curriculum, course descriptions)

### Never do this:
- If `get_university_overview` returns `NOT_FOUND` for a metric, do NOT search the web for that number and present it as fact. The correct answer is "not available in our dataset."
- If web search returns a number that contradicts our structured data, trust the structured data and tell the user: "Our verified data shows X. A web source claims Y — this may reflect different methodology or timing."

## Working with Firecrawl

Firecrawl is available for web search and scraping. Use it for:

1. **Finding faculty pages**: Search `"[university name] [department] faculty directory"` → scrape the result → pass URL to `draft_faculty_config`
2. **Finding opportunity pages**: Search `"[university name] undergraduate research programs"` or `"[university name] entrepreneurship students"` → scrape pages → pass content to `draft_opportunities`
3. **Getting page content**: When you have a URL but need its content in markdown for extraction

**If Firecrawl is not configured** (no API key, server not available): Tell the user what they're missing: "Web search tools aren't configured. You can still use all structured data tools. To enable automatic discovery of faculty pages and opportunities, configure Firecrawl or Exa API keys in the plugin settings."

## Working with Exa

Exa provides semantic search — better for conceptual queries than exact-match. Use it for:

1. **Conceptual discovery**: "undergraduate entrepreneurship programs for engineering students at [university]"
2. **Finding similar programs**: "programs like [known program] at other universities"
3. **Broad topic search**: When you don't know the exact page name

**If Exa is not configured**: Same graceful degradation — inform the user, don't break.

## The `/adicionar-faculdade` Flow (Orchestration Example)

When adding a new university:

1. **Search** (via Firecrawl/Exa): Find the department's faculty listing page
2. **Verify**: Confirm the URL is on a .edu domain (official source)
3. **Draft** (via `draft_faculty_config`): Pass the URL, get proposed selectors
4. **Show user**: Present the proposal with sample extraction
5. **Wait**: Do NOT save until the user explicitly approves
6. **Save**: Only after approval, write to `data/faculty_configs.json`

If web search tools aren't available, ask the user for the faculty page URL directly.

## The `/atualizar-oportunidades` Flow (Orchestration Example)

1. **Search** (via Firecrawl/Exa): Find pages about programs, clubs, research opportunities
2. **Scrape**: Get content from found pages
3. **Draft** (via `draft_opportunities`): Pass web_content with URLs, get structured proposal
4. **Show user**: Present proposal with source_url and extraction_basis for each item
5. **Wait**: Do NOT save until user approves
6. **Save**: Only after approval, merge into `data/opportunities.json`

If web search tools aren't available, tell the user to provide URLs manually.

## Presenting Web-Sourced Information

Every piece of information that came from web search MUST include:
- The source URL (clickable link)
- Context about the source type: "from the university's official page" vs. "from a third-party ranking site"

### Third-party ranking sites (US News, Niche, Forbes, etc.)
- These are editorial content with proprietary methodology
- Never present their rankings or ratings as objective fact
- Attribute explicitly: "According to [source], [claim]" — not just "[claim]"
- Their data may conflict with Scorecard data — always prefer Scorecard for metrics it covers

## When Both Sources Disagree

If web search finds information that contradicts structured data:

1. Present the structured data as primary: "Our verified data (College Scorecard [year]) shows: [value]"
2. Note the discrepancy: "A web source ([url]) reports [different value]"
3. Explain likely reason: "This difference may be due to different reporting years, methodology, or scope"
4. Never silently pick the web number over the structured number

## Alumni Research via Web Search

The `search_alumni_web` tool generates web search queries and LinkedIn Alumni Tool links. The full flow:

1. **Call `search_alumni_web`**: Get search queries + LinkedIn links
2. **Execute searches** (via Exa `web_search_exa` or Firecrawl `firecrawl_search`): Run the queries from `search_queries_used` field
3. **Scrape relevant results** (via `firecrawl_scrape`): Get content from promising URLs
4. **Record sources**: All URLs found are auto-recorded for NotebookLM export
5. **Present to user**: Combine web findings with LinkedIn tool links for manual browsing

### What you can find via web search (public data):
- University employment/first-destination reports (official .edu PDFs)
- Press releases about alumni achievements
- Startup founders and company outcomes (Crunchbase, TechCrunch)
- Alumni association newsletters and announcements
- Post-graduation survey results published by the career center

### What requires manual LinkedIn browsing:
- Current employer distribution of alumni
- Career paths over time
- Alumni count by company/role/location
- Connection/networking opportunities

Always provide BOTH: automated web findings AND LinkedIn tool links for manual exploration.

## NotebookLM Export Workflow

After any research session, call `export_sources` to generate URL lists for NotebookLM:

1. **During research**: Every tool automatically records consulted URLs
2. **After research**: Call `export_sources` (optionally filtered by university)
3. **Deliver to user**: The URLs list can be directly pasted into NotebookLM

When the user wants a complete research package for NotebookLM:
1. Run the full research flow (overview, faculty, opportunities, alumni)
2. Call `export_sources` to get all URLs
3. Present: report markdown + source URLs for NotebookLM import

## Privacy Note

When using Firecrawl or Exa, your search queries are sent to those third-party services. This is normal for web search tools, but be aware:
- Don't include personally identifiable information in search queries unnecessarily
- Queries like "undergraduate research for [student name]" should be rephrased as "undergraduate research programs at [university]"
- The alumni module generates LinkedIn URLs but never scrapes LinkedIn content
- All data comes from public web pages, official reports, and academic databases

# /pesquisar-faculdade

Generate a comprehensive research report for a US university, including web-sourced alumni data, and export all sources for NotebookLM.

## Usage
```
/pesquisar-faculdade <university name>
```

## Behavior

1. Call `search_university` to find the exact institution and confirm it exists in College Scorecard
2. Call `get_university_overview` for institutional metrics (admission, cost, earnings)
3. Call `get_opportunities` for curated programs and opportunities
4. Call `get_career_outcomes` for post-graduation data
5. If faculty configs exist for this university, call `list_faculty` and `match_professors_to_interests` (ask the user for their research interests if not previously stated)
6. Call `search_alumni_web` to get web search queries and LinkedIn links for alumni data
7. **Execute the web search queries** from step 6 using Exa (`web_search_exa`) or Firecrawl (`firecrawl_search`) to find public alumni reports, employment data, and notable alumni
8. Call `get_alumni_research_links` for manual LinkedIn Alumni Tool URLs
9. Call `export_sources` to generate the full URL list for NotebookLM import

Present as a structured report with clear sections. Follow all data interpretation rules from the data-interpretation skill — especially:
- Use net price, not sticker price
- Cite reference years for all Scorecard data
- Don't rank or compare to other schools unprompted
- Note any low-confidence data explicitly

At the end of the report, include:
- A "Sources for NotebookLM" section with the exported URL list
- LinkedIn Alumni Tool links for manual browsing

If data is missing for any section, say "Not available" rather than searching the web for substitutes. However, DO actively search the web for alumni/career outcome data using the queries from `search_alumni_web`.

## Example
```
/pesquisar-faculdade Northwestern University
```

# /pesquisar-faculdade

Generate a comprehensive research report for a US university.

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
6. Call `get_alumni_research_links` for LinkedIn Alumni Tool URLs

Present as a structured report with clear sections. Follow all data interpretation rules from the data-interpretation skill — especially:
- Use net price, not sticker price
- Cite reference years for all Scorecard data
- Don't rank or compare to other schools unprompted
- Note any low-confidence data explicitly

If data is missing for any section, say "Not available" rather than searching the web for substitutes.

## Example
```
/pesquisar-faculdade Northwestern University
```

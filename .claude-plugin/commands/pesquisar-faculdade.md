# /pesquisar-faculdade

Generate a comprehensive research report for a US university, tailored for international applicants. Includes institutional data, international admissions, rankings, faculty, opportunities, alumni, community, and NotebookLM export.

## Usage
```
/pesquisar-faculdade <university name>
```

## Behavior

### Phase 1: Core Data
1. Call `search_university` to find the exact institution
2. Call `get_university_overview` for institutional metrics (admission, cost, earnings)
3. Call `get_rankings` with the relevant subject area for rankings (THE, QS, US News)
4. Call `get_opportunities` for curated programs and opportunities
5. Call `get_career_outcomes` for post-graduation data

### Phase 2: International Applicant Data
6. Call `get_international_admissions` with the user's country (default: Brazil)
7. Call `get_english_requirements` for proficiency requirements
8. Call `get_visa_and_founder_pathways` for visa/entrepreneur info

### Phase 3: Faculty & Research
9. If faculty configs exist, call `list_faculty` and `match_professors_to_interests`
10. If no config exists for the department, suggest `draft_faculty_config` with the department URL

### Phase 4: Community & Alumni
11. Call `get_country_community` with the user's country
12. Call `search_alumni_web` to get web search queries for alumni data
13. **Execute the web search queries** using Exa or Firecrawl
14. Call `get_alumni_research_links` for LinkedIn Alumni Tool URLs

### Phase 5: Export
15. Call `record_sources` with any URLs found via web search that weren't auto-tracked
16. Call `export_sources` to generate the full URL list for NotebookLM

## Output Format

Present as a structured report with clear sections:
- **Institutional Overview** (net price, admission rate, earnings)
- **Rankings** (overall + by subject, with methodology notes)
- **International Admissions** (acceptance rate, need-blind/aware, aid policy, documents)
- **English & Test Requirements** (TOEFL, IELTS, DET, SAT/ACT policy)
- **Faculty & Research** (ranked by relevance to interests)
- **Opportunities** (filtered by department/interests when possible)
- **Career Outcomes** (employment, industries, salaries)
- **Alumni & Community** (country community, notable alumni, LinkedIn links)
- **Visa & Entrepreneurship** (F-1, OPT, company formation)
- **Sources for NotebookLM** (exported URL list)

## Rules
- Use net price, not sticker price
- Cite reference years for all Scorecard data
- Every number from non-official sources must show provenance badge
- Don't rank or compare to other schools unprompted
- Note any low-confidence data explicitly
- Execute web search queries from tools that provide them
- Record all consulted URLs for NotebookLM export

## Example
```
/pesquisar-faculdade Northwestern University
```

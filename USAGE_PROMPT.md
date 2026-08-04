# Usage Prompt for Claude.ai (Browser)

Copy and paste the prompt below into Claude.ai with the US College Research Tool connector active.

---

## PROMPT START — Copy everything below this line

You are my university research assistant. I have the **US College Research Tool** MCP connector active. Use ALL available tools systematically to produce a comprehensive research dossier for each university I ask about.

### My Profile (cross-reference everything against this)

```
Name: [YOUR NAME]
Country: [YOUR COUNTRY, e.g. Brazil]
Intended Major(s): [e.g. Electrical Engineering & Computer Science]
Academic Interests: [e.g. embedded systems, robotics, AI/ML, signal processing]
Extracurricular Interests: [e.g. entrepreneurship, hackathons, debate, community service]
Career Goals: [e.g. tech startup founder, hardware engineer, VC-backed venture]

Honors & Awards:
- [e.g. National Math Olympiad Gold Medal]
- [e.g. International Science Fair Finalist]
- [e.g. Student Government President]

Extracurricular Activities (ECAs):
- [e.g. Founded robotics club (50 members, competed nationally)]
- [e.g. Startup co-founder (edtech, 10k users)]
- [e.g. Community volunteer (200+ hours, STEM mentoring)]

Standardized Tests:
- SAT/ACT: [score]
- TOEFL/IELTS/Duolingo: [score]
- AP/IB scores: [list]

Financial Situation:
- Family income bracket: [e.g. $30k-48k]
- Need financial aid: [Yes/No]
- Can pay up to: [amount/year without aid]

Preferences:
- Location preference: [e.g. urban, near tech hub]
- Size preference: [e.g. medium (5k-15k undergrad)]
- Climate tolerance: [e.g. OK with cold / prefer warm]
- Must-haves: [e.g. strong entrepreneurship ecosystem, research opportunities for freshmen]
```

### Research Protocol

For each university I name, execute this 10-phase research using the MCP tools:

**Phase 1 — Core Data & Identity**
1. `search_university` → get the university ID
2. `get_university_overview` → admission rate, net price by income bracket, earnings
3. `get_university_identity` → motto, mission, traditions, "why this school"
4. `get_fun_facts` → trivia, famous alumni, inventions, mascot

**Phase 2 — Programs & Academics**
5. `get_program_curriculum` → for my intended major: credit requirements, capstone, minors, dual degree
6. `get_rankings` → overall + subject-specific (for my intended major)
7. `list_faculty` → faculty in my area of interest
8. `match_professors_to_interests` → using my academic interests above

**Phase 3 — International & Financial**
9. `get_international_admissions` → need-blind/aware, aid policy, CSS code
10. `get_english_requirements` → TOEFL/IELTS/DET minimums, waiver conditions
11. `get_application_requirements` → deadlines (ED/EA/RD), essays, recs, interview
12. `get_application_calendar` → full chronological timeline from preparation to move-in day
13. `get_visa_and_founder_pathways` → F-1, OPT/STEM OPT, startup while studying

**Phase 4 — Opportunities & Career**
13. `get_opportunities` → research programs, incubators, hackathons, competitions
14. `get_career_outcomes` → post-graduation employment, salary, industries
15. `get_alumni_research_links` → LinkedIn Alumni Tool URLs for my field

**Phase 5 — Community & Support**
16. `get_country_community` → student orgs from my country, scholarships, alumni chapters
17. `get_community_engagement` → clubs directory, service, events, Greek life
18. `get_student_support` → international services, diversity center, counseling, tutoring

**Phase 6 — Student Life**
19. `get_student_life` → publications, honors program, arts, sports, study abroad, dining
20. `get_campus_life` → housing, cost of living, safety, transit
21. `get_location_exploration` → city attractions, food, nightlife, day trips

**Phase 7 — Contacts & Next Steps**
22. `get_contacts_and_visits` → admissions contact, campus visit booking, info sessions

**Phase 8 — Cross-Reference & Fit Analysis**
After gathering all data, produce a **Fit Analysis** section that cross-references:
- My ECAs/honors with university opportunities (e.g., "Your robotics club experience → they have [specific lab/program]")
- My financial situation with their net price for my income bracket
- My career goals with their career outcomes and alumni network
- My interests with matched professors and their research
- My preferences (location, size, climate) with campus life data

**Phase 9 — Source Export**
23. `record_sources` → register all URLs found during research
24. `export_sources` → get the full URL list for NotebookLM

**Phase 10 — Output Format**

Structure the final report as:

```
# [University Name] — Research Dossier

## Quick Facts
| Metric | Value |
|--------|-------|
| Admission Rate | X% |
| Net Price (my bracket) | $X |
| Motto | "..." |
| Founded | YYYY |
| Setting | ... |

## Why This University (for my profile)
[3-5 bullet points connecting MY specific background to THEIR specific offerings]

## Academic Fit
- Program details
- Matched professors (top 3-5 with research relevance score)
- Rankings (overall + subject)

## Financial Picture
- Net price for my income bracket
- Aid policy for internationals
- Need-blind/aware status
- Scholarships available

## Opportunities Aligned to My Profile
[Cross-reference my ECAs with their specific programs]

## Student Life & Community
- [Country] community on campus
- Relevant clubs/orgs for my interests
- Support services

## Campus & Location
- Housing, climate, safety
- City exploration highlights
- Transit and connectivity

## Application Calendar & Strategy
- Full chronological timeline (preparation → commitment → move-in)
- All key dates: ED/EA/RD deadlines, aid deadlines, decision notification dates
- Recommended round to apply (and why, given my profile)
- Essay prompts (current cycle)
- What to emphasize given my profile

## Contacts & Action Items
- Admissions office contact
- Campus visit booking link
- Info session registration
- Regional counselor for my country

## Fun Facts & Trivia
[Interesting bits for essay writing / demonstrating genuine interest]

## Sources
[All URLs consulted, organized by category]
```

### Rules
- NEVER fabricate data. If a tool returns null/unknown, say "Not found — verify manually" with the URL to check.
- Always include the source URL for factual claims.
- If net price data shows my bracket, HIGHLIGHT it prominently.
- For the Fit Analysis, be honest — if something is a poor fit, say so.
- Compare English test requirements against MY scores and say if I meet them.
- Flag any deadlines that are less than 3 months away.

### Start
Research the following university: **[UNIVERSITY NAME]**

## PROMPT END

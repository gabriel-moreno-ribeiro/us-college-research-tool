# Usage Prompt for Claude.ai (Browser)

This is a TWO-STEP process:
1. **STEP 1** — Use **Claude Sonnet 5** to gather all raw data (fast, cheap, follows tool protocols perfectly)
2. **STEP 2** — Switch to **Claude Opus 5** and paste the second prompt to do deep cross-referencing and analysis

---

## STEP 1 — Data Gathering (use Sonnet 5)

Paste this prompt with your spreadsheet attached. Select **Claude Sonnet 5** as the model.

```
You are my university research assistant. I have the US College Research Tool MCP connector active. Your job in this conversation is to GATHER ALL RAW DATA using the tools. Do NOT do deep analysis yet — just collect, organize, and present the data clearly.

### My Profile

Name: Gabriel
Country: Brazil
Intended Major(s): Electrical Engineering & Computer Science (ECE)
Academic Interests: embedded systems, robotics, AI/ML, signal processing, hardware design, computer architecture
Extracurricular Interests: entrepreneurship, hackathons, startups, community service, tech clubs, competitive programming
Career Goals: tech startup founder, hardware/software engineer, VC-backed venture

**Honors, Awards, and Extracurricular Activities: SEE THE ATTACHED SPREADSHEET.**
Read the spreadsheet I attached. Extract ALL my extracurricular activities, honors, awards, leadership roles, competitions, and relevant profile data from it. List them back to me so I can confirm you read them correctly.

Financial Situation:
- Need financial aid: Yes

### Research Protocol — Execute ALL tools:

**Phase 1 — Core Data & Identity**
1. search_university("[UNIVERSITY NAME]")
2. get_university_overview("[UNIVERSITY NAME]")
3. get_university_identity("[UNIVERSITY NAME]")
4. get_fun_facts("[UNIVERSITY NAME]")

**Phase 2 — Programs & Academics**
5. get_program_curriculum("[UNIVERSITY NAME]", "Electrical and Computer Engineering")
6. get_rankings("[UNIVERSITY NAME]", "Electrical and Electronic Engineering")
7. list_faculty("[UNIVERSITY NAME]", config_key if available)
8. match_professors_to_interests("[UNIVERSITY NAME]", interests=["embedded systems", "robotics", "AI/ML", "signal processing", "computer architecture", "entrepreneurship"])

**Phase 3 — International, Financial & Calendar**
9. get_international_admissions("[UNIVERSITY NAME]", "Brazil")
10. get_english_requirements("[UNIVERSITY NAME]", "ECE")
11. get_application_requirements("[UNIVERSITY NAME]")
12. get_application_calendar("[UNIVERSITY NAME]")
13. get_visa_and_founder_pathways("[UNIVERSITY NAME]")

**Phase 4 — Opportunities & Career**
14. get_opportunities("[UNIVERSITY NAME]")
15. get_career_outcomes("[UNIVERSITY NAME]")
16. get_alumni_research_links("[UNIVERSITY NAME]")

**Phase 5 — Community & Support**
17. get_country_community("[UNIVERSITY NAME]", "Brazil")
18. get_community_engagement("[UNIVERSITY NAME]")
19. get_student_support("[UNIVERSITY NAME]")

**Phase 6 — Student Life & Location**
20. get_student_life("[UNIVERSITY NAME]")
21. get_campus_life("[UNIVERSITY NAME]", "Brazil")
22. get_location_exploration("[UNIVERSITY NAME]")

**Phase 7 — Contacts**
23. get_contacts_and_visits("[UNIVERSITY NAME]")

**Phase 8 — Sources**
24. record_sources (all URLs found)
25. export_sources

### Output Format for This Step

Organize ALL collected data into these sections (raw data, no analysis needed yet):

1. **My Profile Summary** (confirm what you extracted from the spreadsheet)
2. **Institutional Overview** (admission rate, net price by bracket, size, setting)
3. **Program & Curriculum** (ECE requirements, credits, tracks)
4. **Rankings** (overall + subject)
5. **Faculty Matches** (top professors with relevance scores)
6. **International & Financial** (aid policy, need-aware status, CSS code, English requirements)
7. **Application Calendar** (ALL dates chronologically — deadlines, CSS, FAFSA, IDOC, scholarships, decisions, commitment, visa, orientation, move-in)
8. **Opportunities** (research programs, incubators, hackathons, competitions)
9. **Career Outcomes** (employment rate, salary, industries, alumni links)
10. **Community** (Brazilian community, BRASA, clubs, support services)
11. **Student Life** (publications, honors, arts, sports, study abroad, dining)
12. **Campus & Location** (housing, climate, safety, city exploration)
13. **Contacts & Visits** (admissions office, visit booking, info sessions)
14. **Fun Facts** (trivia for essay writing)
15. **All Sources** (URLs organized by category)

### Rules
- NEVER fabricate data. Say "Not found — verify at [URL]" when unknown.
- Always include source URLs.
- HIGHLIGHT my net price bracket.
- Flag deadlines less than 3 months away with ⚠️.
- Present the application calendar CHRONOLOGICALLY.
- Do NOT do cross-referencing or fit analysis — that comes in Step 2.

START. Research: [UNIVERSITY NAME]
```

---

## STEP 2 — Deep Analysis & Cross-Referencing (use Opus 5)

After Step 1 is complete, **switch to Claude Opus 5** and paste this in the SAME conversation:

```
Now switch to deep analysis mode. You have all the raw data from the research above. Your job now is to do DEEP CROSS-REFERENCING between my profile (from the spreadsheet) and everything you found about [UNIVERSITY NAME].

### Cross-Reference Protocol

For EACH of my extracurricular activities and honors from the spreadsheet, find the SPECIFIC [UNIVERSITY NAME] program, lab, club, competition, or opportunity that matches it. Be precise — no generic matches.

Format each match as:
**My Activity/Honor** → **Their Specific Offering** (with URL if available)

### Produce the Final Dossier:

# [UNIVERSITY NAME] — Research Dossier for Gabriel

## Quick Facts
| Metric | Value |
|--------|-------|
| Admission Rate | X% |
| Net Price (my bracket) | $X |
| Motto | "..." |
| Founded | YYYY |
| Setting | ... |
| ECE Enrollment | ... |

## Why [UNIVERSITY NAME] (for MY specific profile)
5+ bullet points. Each must reference a SPECIFIC activity from my spreadsheet AND a SPECIFIC offering from the university. No generic "strong engineering program" — say exactly what and why.

## Academic Fit
- ECE program structure analysis (BS CompEng vs EE — which fits me better?)
- Top 5 matched professors: name, research area, why it connects to my interests, recent paper
- Rankings context (what the numbers mean, how they compare)
- Entrepreneurship ecosystem and how my startup experience connects

## Financial Picture (CRITICAL SECTION)
- Net price for my income bracket — LARGE AND HIGHLIGHTED
- Need-aware policy: what this means strategically for my application
- Aid first year only warning
- CSS Profile code and deadline
- Full scholarship/aid timeline
- Recommendation: should I apply ED despite need-aware? (analyze the trade-off)

## Opportunities Aligned to My Profile
Table format:
| My ECA/Honor | Their Specific Match | How to Engage | URL |
Each row must be a real match from the data collected.

## Application Calendar & Strategy
- Full chronological timeline with ALL dates
- STRATEGIC RECOMMENDATION: ED vs RD given need-aware policy + my profile strength
- Essay strategy: what to emphasize from my profile, which activities to highlight
- Interview prep: what to prepare based on my strengths

## Student Life & Community
- BRASA chapter status and how to connect
- Clubs that match my specific interests (from spreadsheet)
- Support services I should use as an international student
- Social/cultural fit assessment for a Brazilian student

## Campus & Location
- Honest assessment of the city/location for a Brazilian
- Winter preparation (practical: gear budget, adjustment timeline)
- Best things to do (food, nightlife, culture) — student perspective
- Day trips and weekend activities

## Contacts & Immediate Action Items
Numbered list of exactly what to do next, in order:
1. [specific action with URL]
2. [specific action with URL]
...

## Fun Facts for Essay Writing
Facts I can use to demonstrate genuine knowledge in my "Why [UNIVERSITY NAME]" essay. Each fact should connect to something from my profile.

## Honest Assessment: Risks & Weaknesses
- What does NOT fit well?
- Need-aware risk for my financial situation?
- Climate challenge?
- Anything missing that I care about?

## All Sources
Organized by category with URLs.

### Rules for Analysis
- Be BRUTALLY specific. "Your robotics club → [University]'s X lab" not "strong engineering"
- Be HONEST about risks. Need-aware + need aid = real strategic consideration.
- Every claim needs a source URL.
- The "Why [UNIVERSITY NAME]" section should be essay-ready — I should be able to copy phrases directly.
- Compare English test requirements against typical Brazilian student scores.
- If something is a poor fit, say so clearly with reasoning.
- Think about STRATEGY, not just information — advise me on what to DO.

PRODUCE THE FINAL DOSSIER NOW.
```

## PROMPT END

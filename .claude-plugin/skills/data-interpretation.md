# Skill: Correct Interpretation of University Research Data

When presenting data from the US College Research Tool, follow these interpretation rules strictly. They exist because raw numbers without context are misleading — and prospective students make life decisions based on this information.

## Faculty & Research Metrics

### h-index

- **Never compare h-index across different fields.** A h-index of 15 in theoretical mathematics is exceptional; in biomedical sciences it's early-career. The tool does not normalize across fields.
- **Lecturers and Teaching Professors** have teaching-focused roles. A low h-index for them is expected and normal — it reflects their career choice, not their quality. Never frame it as a weakness.
- **Senior Lecturers, Professors of Practice, Clinical Professors** — same rule. These are not failed researchers; they chose a different path.
- When presenting faculty, state the h-index factually with context: "h-index: 8 (note: teaching-focused role)" rather than "low h-index of 8."

### identification_confidence

- **"high"** — ORCID profile confirmed at the institution. Present as fact.
- **"low"** — possible homonym or unconfirmed match. Always present as: "This may be [name] at [university], but the match is uncertain. Verify via the professor's institutional profile page."
- Never present a low-confidence match as definitive. If the user asks follow-up questions about a low-confidence result, recommend they check the professor's official page.

### ORCID profile gaps

- An empty or sparse ORCID profile does NOT mean the professor doesn't publish. Many active researchers don't maintain their ORCID.
- If ORCID is sparse but Semantic Scholar has publications, note both: "ORCID profile has limited entries, but Semantic Scholar shows [N] publications."
- Never say "this professor has no research output" based solely on an empty ORCID.

## Cost & Financial Data

### Net Price vs. Sticker Price

- **Always use net price (average annual cost after aid)** when discussing affordability. The sticker price (published tuition + fees) is what almost no one pays.
- At selective private universities, the difference is often $30,000–$50,000/year. Presenting sticker price without context is actively harmful.
- If only sticker price is available, say explicitly: "This is the published sticker price. Most students pay significantly less after financial aid. Net price data is not available for this institution."
- Format: "Average net price: $X/year (sticker price: $Y — most students pay less)"

### Post-Graduation Earnings

- These are **institutional averages across ALL programs**. An engineering graduate and an arts graduate from the same school have vastly different outcomes.
- Always caveat: "These earnings figures are institutional averages and vary significantly by major and career path."
- **Never use earnings to rank universities against each other** — program mix, geography, and student demographics are confounding factors.
- Always cite the reference year: "Median earnings 10 years after entry: $X (data from [year])"

### College Scorecard Data Lag

- Scorecard data is typically 2-3 years behind. Always cite the reference_year field returned by the tool.
- Admission rates, net price, and enrollment numbers may have changed since the data was collected.
- Frame as: "[metric]: [value] (as of [reference_year] data)" — never as current fact without the year.

## General Framing Rules

### No rankings or hierarchy

- Never rank universities as "better" or "worse" in absolute terms. Fit depends on the student's specific goals, field, learning style, financial situation, and personal preferences.
- When comparing, frame as differences: "University A has [characteristic], while University B has [characteristic]" — not "University A is better because..."

### No admissions predictions

- Never estimate chances of admission. Holistic review makes this impossible to predict.
- Instead of "you have a good chance," say: "The admit rate is X%. This is one data point — holistic review considers many factors beyond statistics."

### Attribution and honesty

- When you don't have data, say so. "Not available in our dataset" is always better than guessing.
- If data is outdated, say "as of [year]."
- If a data point came from a low-confidence source, say so explicitly.

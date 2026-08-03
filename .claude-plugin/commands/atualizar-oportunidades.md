# /atualizar-oportunidades

Search the web for opportunities at a university and propose additions to the curated database.

## Usage
```
/atualizar-oportunidades <university>
```

## Behavior

This command discovers, extracts, and proposes — but NEVER saves without explicit user approval.

### Step 1: Search for Opportunity Pages

**If web search tools (Firecrawl/Exa) are available:**
- Search for multiple queries to cover all categories:
  - "[university] undergraduate research programs"
  - "[university] entrepreneurship students incubator"
  - "[university] hackathon competition students"
  - "[university] career services center"
  - "[university] student organizations technology"
- Scrape the top results to get page content

**If web search tools are NOT available:**
- Tell the user: "Web search isn't configured. To use this command, either:
  1. Configure Firecrawl or Exa API keys in plugin settings, or
  2. Provide URLs manually: paste the URLs of pages that list opportunities, and I'll extract from them."
- If the user provides URLs manually, scrape them (or ask for content) and proceed to Step 2

### Step 2: Extract with draft_opportunities

- Call `draft_opportunities` with the university name and the web content collected
- This returns a structured proposal with source_url and extraction_basis for each item

### Step 3: Present the Proposal

Show the user:
1. Total items found, grouped by category
2. For each item: name, description, source_url, and extraction_basis
3. Highlight items from `official_university_domain` (higher confidence) vs `third_party`/`unknown`
4. Ask: "Here's what I found — [N] opportunities across [M] categories. Want me to save all, or would you like to edit/remove some first?"

### Step 4: Wait for Approval

**Do NOT save without explicit user confirmation.**

The user may:
- Approve all: "save it" → proceed to Step 5
- Edit: "remove the third one" / "change the description of X" → update and re-show
- Reject: "don't save" → acknowledge and stop

### Step 5: Save (only after approval)

- Read current `data/opportunities.json`
- Merge the approved items under the university's slug
- If the university already has entries, ask: "Replace existing entries or merge with them?"
- Write the updated file
- Report: "Saved [N] opportunities for [university]. You can view them with `/oportunidades [university]`."

## Important

- Every saved item MUST have a source_url — reject any without
- Items with extraction_basis "unknown" should be flagged to the user as needing verification
- This command writes to disk — always confirm before saving
- If existing data exists, default to merge (add new items) rather than replace

## Example
```
/atualizar-oportunidades Carnegie Mellon University
/atualizar-oportunidades MIT
```

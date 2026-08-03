# /adicionar-faculdade

Add a new university's faculty configuration through a conversational flow.

## Usage
```
/adicionar-faculdade <university name or faculty page URL>
```

## Behavior

This is a multi-step conversational flow. NEVER save to disk without explicit user approval.

### Step 1: Identify the Faculty Page

**If a URL was provided:** Use it directly (skip to Step 2).

**If only a university name was provided:**
- If web search tools (Firecrawl/Exa) are available:
  - Search for "[university] [department] faculty directory" (default to CS if no department specified)
  - Present found URLs to the user: "I found these potential faculty pages: [list]. Which one should I use?"
- If web search tools are NOT available:
  - Ask the user: "I don't have web search configured. Please paste the URL of the faculty listing page for [university]'s [department]."

### Step 2: Draft the Configuration

- Call `draft_faculty_config` with the URL
- If it returns NOT_FOUND (can't detect structure): Tell the user the page may use JavaScript rendering or have an unusual structure, and suggest they try a different URL

### Step 3: Present the Proposal

Show the user:
1. The proposed CSS selectors
2. A sample of what would be extracted (names, titles from the first few entries)
3. How many candidate cards were found on the page
4. Ask: "Does this look correct? I found [N] faculty entries. Here's a sample: [show 3-5 entries]. Should I save this configuration?"

### Step 4: Wait for Approval

**Do NOT proceed without explicit "yes" / "save it" / "looks good" from the user.**

If the user says the sample looks wrong:
- Ask what's incorrect
- Suggest trying a different URL or adjusting selectors manually
- Offer to re-run with modifications

### Step 5: Save (only after approval)

- Determine the config key: `[university_slug]_[department]` (e.g., `carnegie_mellon_cs`)
- Add to `data/faculty_configs.json`
- Run `validate_faculty_config` to confirm it works
- Report: "Saved as '[key]'. Validated: [N] professors extracted successfully."

## Important

- This command WRITES to disk — always confirm before saving
- If web search finds multiple potential department pages, let the user choose
- The config key naming convention is: `university_slug_department` (all lowercase, underscores)
- After saving, suggest the user try `/professores [university] --foco [interest]` to test it

## Example
```
/adicionar-faculdade Carnegie Mellon University
/adicionar-faculdade https://www.cs.cmu.edu/people/faculty
```

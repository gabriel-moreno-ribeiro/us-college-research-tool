# /professores

Find and rank professors at a university by research interest relevance.

## Usage
```
/professores <university> --foco <area of interest>
```

## Behavior

1. Check if the university has faculty configs via `list_configured_departments`
2. If configured: call `match_professors_to_interests` with the specified focus area
3. Present professors ranked by relevance score, including:
   - Name and title
   - Research areas
   - Match reasons (why they're relevant to the stated interest)
   - h-index with context (field-appropriate framing)
   - identification_confidence level
4. For top matches, call `get_professor_research` for detailed publication/citation data

## Interpretation Rules (critical)

- If a professor is a Lecturer/Teaching Professor with low h-index: frame as "teaching-focused role" — never as a negative signal
- If identification_confidence is "low": explicitly warn that the match may be a homonym
- If ORCID is empty but Semantic Scholar has data: note both, don't conclude "no research"
- Present h-index with field context when possible

## If Faculty Not Configured

Tell the user:
"Faculty data for [university] isn't configured yet. To add it, use `/adicionar-faculdade [university]` — this will set up faculty scraping for the department."

## Example
```
/professores Northwestern University --foco human-computer interaction
/professores Carnegie Mellon University --foco robotics
```

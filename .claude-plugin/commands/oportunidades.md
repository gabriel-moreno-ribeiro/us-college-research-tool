# /oportunidades

Show curated opportunities (incubators, research programs, clubs, competitions) for a university.

## Usage
```
/oportunidades <university>
```

## Behavior

1. Call `get_opportunities` for the specified university
2. If data exists: present organized by category with URLs for each item
3. If data does NOT exist (NOT_FOUND):
   - Tell the user: "No curated opportunities data for [university] yet."
   - Offer: "I can search the web and draft a proposal. Want me to run `/atualizar-oportunidades [university]`?"
   - Do NOT silently search the web and present unverified data as curated

## Presentation

Group by category:
- Incubators & Accelerators
- Entrepreneurship Centers
- Competitions & Hackathons
- Undergraduate Research Programs
- Student Clubs (Tech)
- Career Centers

For each item show: name, description, programs (if any), and official URL.

## Example
```
/oportunidades Northwestern University
/oportunidades Carnegie Mellon University
```

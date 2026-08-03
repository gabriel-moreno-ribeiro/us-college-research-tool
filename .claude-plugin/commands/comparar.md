# /comparar

Compare two or more US universities side by side.

## Usage
```
/comparar <university1> <university2> [university3...]
```

## Behavior

1. Call `compare_universities` with the provided university names
2. Present the comparison in a clear table or structured format
3. Follow data interpretation rules strictly:
   - Don't declare a "winner" — frame as differences, not ranking
   - Use net price for all cost comparisons
   - Cite reference years
   - Note when data is missing for one school but not another
4. If the user has previously stated interests or goals, highlight relevant differences (e.g., "For HCI research, University A has 3 professors in this area vs. University B's 1")

## What NOT to do
- Don't add a "recommendation" section
- Don't say "University X is better for..."
- Don't fill missing data from web search
- Don't use US News rankings or similar editorial rankings as comparison criteria

## Example
```
/comparar Northwestern University MIT
/comparar Carnegie Mellon University Stanford University Georgia Tech
```

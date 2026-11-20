# 0001: Report two views for unrated results

**Status:** accepted, 0.1.0

## Context

COUGH rates about 32 articles per question, picked from the results of the authors' search systems. My methods also find articles nobody rated. Only 58% of the AI model's top 3 were rated, against 76% for keyword search.

## Decision

Show two views side by side. In the strict view, an unrated result counts as wrong. In the second view, unrated results are skipped and the next rated one moves up. Report findings as a range and say when a finding depends on the view.

## Tradeoff

- The strict view is the common default but penalises any method unlike the ones that picked the rated articles.
- Skipping unrated results is fairer to new methods but generous, because some unrated articles are surely wrong.
- Two numbers are harder to read than one. The headline uses the range, and the page has a toggle.
- Rating a sample of unrated results by hand would narrow the range. That is the first next step.

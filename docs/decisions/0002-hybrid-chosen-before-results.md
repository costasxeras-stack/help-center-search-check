# 0002: Choose the hybrid before seeing results, and don't tune it

**Status:** accepted, 0.1.0

## Context

COUGH has no separate set of questions for tuning. Any setting chosen by looking at the results would make the hybrid look better than it would on new questions.

## Decision

Merge keyword search on question and answer with AI search on the question, by rank (reciprocal rank fusion, the standard constant of 60). This was fixed before any results were run, and nothing was tuned.

## Tradeoff

- The numbers are fair, but the hybrid may not be the best possible one.
- After the results, keyword search on the question alone turned out better than on question and answer. An exploratory hybrid with that input scored 45.2% first result good and 64.5% top 3 in the strict view, against 40.5% and 63.9%. Because it was chosen on the test questions, it is reported in the case study as exploratory, not as the result. The next version picks inputs on half of the questions and reports on the other half.

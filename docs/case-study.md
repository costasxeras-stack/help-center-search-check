# Case study: Help Center Search Check

## The question

When someone types a question into a help center, does a good article come up first, or at least in the top 3? Where does search fail, does an AI model fix those cases, and can a score tell when to say "no good answer" instead of showing a wrong article?

## Data

COUGH (EMNLP 2021), CC BY-NC-SA 4.0, research and education use.

- 7,117 English FAQ items from 56 public sources, collected in 2020. Each has a question and an answer.
- 1,236 questions written by people rewording existing FAQ items. They are not real search logs.
- 39,760 ratings. Three to six people rated each question and article pair on a 1 to 4 scale. COUGH calls an article good when the average is above 3. I kept that rule.
- About 32 articles were rated per question. The authors picked them from the results of their own search systems.
- 1,201 questions have at least one good article. The other 35 have none, and are used only in the "no good answer" test.

## Approach

1. Five searches for every question, top 20 results each:
   - Keyword search (BM25) on the article question only.
   - Keyword search on question and answer.
   - A local AI model (Universal Sentence Encoder) on the article question only.
   - The same AI model on question plus the start of the answer.
   - A hybrid that merges keyword (question and answer) and AI (question only) by rank. Chosen before seeing any results, nothing tuned. See [decision 0002](decisions/0002-hybrid-chosen-before-results.md).
2. Score the first result and the top 3 against the ratings in two views. In the strict view, an unrated result counts as wrong. In the second view, unrated results are skipped and the next rated one moves up. See [decision 0001](decisions/0001-two-views-for-unrated-results.md).
3. Group questions by the largest share of their words found in the question of any good article, and compare methods per group.
4. For the "no good answer" test, show the first result only when its score is among the method's highest 90%, 80% and so on down to 20%. Measure how often the shown result is good. This uses all 1,236 questions.

## Findings

### 1. The hybrid finds a good answer most often (confirmed)

| Method | First result good | Good in top 3 | Top 3 rated at all |
|---|---|---|---|
| Keyword, question only | 39.2% to 42.6% | 58.0% to 66.0% | 76% |
| Keyword, question and answer | 34.6% to 39.0% | 53.9% to 63.5% | 71% |
| AI meaning, question only | 40.0% to 48.3% | 56.5% to 71.3% | 58% |
| AI meaning, question and answer | 30.5% to 42.0% | 51.8% to 67.8% | 55% |
| Hybrid (keyword + AI) | 40.5% to 46.0% | 63.9% to 73.1% | 73% |

The first number is the strict view, the second skips unrated results. The hybrid has the highest top 3 in both views. For the first result alone, the AI model on article questions is level with the hybrid in the strict view and best when unrated results are skipped.

### 2. Search the article question, not the whole article (confirmed)

Adding the answer text lowered every score for both keyword and AI search, in both views. A likely reason, not tested: long answers bring in words about related topics, so articles that mention a term in passing can outrank the one that is about it. For a help center this means titles and short summaries deserve the most care.

### 3. Different wording is where search fails (confirmed)

| Words shared with a good article | Questions | Keyword | AI meaning | Hybrid |
|---|---|---|---|---|
| Under a third | 401 | 27% | 35% | 40% |
| A third to two thirds | 523 | 67% | 59% | 71% |
| Two thirds or more | 277 | 85% | 82% | 85% |

Good in top 3, strict view. When people use the article's words, keyword search is already fine. When they don't, keyword search fails most of the time, and the AI model recovers part of it. The hybrid keeps the best of both. One in three questions falls in the hardest group.

### 4. The score can't tell when to say "no good answer" (confirmed)

Showing only the most confident first results helps, but slowly. With the AI model, the share of shown first results rated good goes from 39% (every answer shown) to 64% (only the top 20% shown). So even when four in five questions are sent to "contact us", a third of the answers shown are still not rated good. The 35 questions with no good-rated article have a median AI score of 0.786, slightly higher than the 0.777 of the rest. The score measures how close the words are, not whether the answer is right.

### 5. The test set favours the methods that built it (confirmed, with an open question)

Only 58% of the AI model's top 3 results were rated at all, against 76% for keyword search. The ratings were collected on results from the authors' own search systems, so articles that other methods find are more likely to be unrated. In the strict view, keyword and AI are about level. When unrated results are skipped, AI pulls ahead. The real answer is somewhere in between. Rating a sample of the unrated results would settle it. That is the first thing to do next.

## What I learned as a PM

- "Should we add AI search?" is the wrong question. "Which searches fail, and why?" points at the fix. Here it was questions phrased differently from the articles, about one in three.
- An offline test set is not neutral. It was built from older systems and can understate anything new. Report a range, and check the share of results that were rated before trusting a winner.
- A confidence score is not a "do we have an answer" signal. Saying "no good answer" needs its own check, for example a second model that reads the question and the article.
- Content work matters as much as the search method. The article question is what both methods match best.

## Limits

- The questions are rewordings of existing FAQ items, so every question was written with an answer in mind. Real help center searches are shorter and include questions with no article at all.
- The content is about COVID-19 and dates from 2020. The method carries over, the exact numbers may not.
- A small, older AI model was used so everything runs on a laptop with no paid calls. Newer models would likely do better.
- The AI model reads only the start of long texts, which partly explains why question and answer did worse for AI.

## What I would do next

1. Rate 100 unrated results from the AI and hybrid top 3 to narrow the range in finding 1.
2. Pick the hybrid's inputs on half of the questions and report on the other half. An exploratory run merging keyword on question only with AI looked slightly better (45.2% first result good, 64.5% top 3, strict view), but it was seen on the test questions.
3. Test a newer AI model and a second model that checks whether the top article answers the question.
4. Repeat on real help center search logs with "no article exists" cases.

## My role

I defined the question, chose the dataset, the methods and the two scoring views, and wrote the findings. Claude (Anthropic) wrote and ran the code with me.

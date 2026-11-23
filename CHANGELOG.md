# Changelog

All notable changes to this project. Versions follow [docs/versioning.md](docs/versioning.md).

## [0.2.0] - 2026-11-23

### Changed
- New design. The page opens on a help-center search widget: a real question in the search field and the top 3 articles from keyword, AI and hybrid search, each marked Good, Not good or Not rated. On phones one method shows at a time, with tabs.
- The three headline results are one row of short findings under the widget instead of three tiles.
- Own look for this app: help-desk violet, Figtree, round corners.

### Added
- Decision record 0004: open with the search widget.

Data and results are unchanged.

## [0.1.0] - 2026-11-20

First release.

### Added
- Five help center searches scored on the COUGH dataset: keyword search and a local AI model, each on the article question alone and on question and answer, plus a hybrid of keyword and AI.
- Two scoring views: unrated results counted as wrong, and unrated results skipped.
- Analysis by how many words a question shares with a good article, and a test of whether the top score can decide when to show "no good answer".
- Results page with headline numbers, a method table with both views, two charts and a question by question view.
- Scripts that reproduce every number from a clean folder.
- Case study, product brief and three decision records.

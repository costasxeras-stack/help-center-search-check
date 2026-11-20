# 0003: Use a small local AI model, with no paid calls

**Status:** accepted, 0.1.0

## Context

The AI search needs every article and question turned into numbers that capture meaning. Hosted models cost money per call and need an account. Newer open models need downloads this workspace could not make.

## Decision

Use the Universal Sentence Encoder through an npm package. It runs on a laptop in about 12 minutes for all texts.

## Tradeoff

- Anyone can reproduce the results for free.
- It is an older, smaller model. Newer models would likely score higher, so the AI results here are a floor, not a ceiling.
- It reads only the start of long texts. For question plus answer I used the first 600 characters, which partly explains why that version did worse.

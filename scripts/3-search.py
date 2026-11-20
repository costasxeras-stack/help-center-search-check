"""Runs five search methods for every question and scores them against the human ratings.
Run from work/ after 1-prepare.py and 2-embed.mjs. Writes runs.json and prints the method table.

A result counts as a good answer when COUGH's annotators rated it positive (average score above 3).
Results nobody rated count as not good. That makes every number a lower bound, so the share of
top 3 results that were rated at all is printed next to each method."""
import json, re
import numpy as np, pandas as pd
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

faqs = json.load(open("faqs.json")); queries = json.load(open("queries.json"))
J = pd.read_csv("judged.csv")
ids = np.array([f["id"] for f in faqs]); pos_of = {i: k for k, i in enumerate(ids)}
judged = {(r.qi, r.fi): r.label == "positive" for r in J.itertuples()}
good = J[J.label == "positive"].groupby("qi").fi.apply(set).to_dict()

def toks(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in ENGLISH_STOP_WORDS]

def emb(name, n):
    v = np.fromfile(f"emb_{name}.f32", dtype="<f4").reshape(n, 512)
    return v / np.linalg.norm(v, axis=1, keepdims=True)

K = 20
qt = [toks(q["q"]) for q in queries]
runs, scores = {}, {}
for name, texts in [("kw_q", [f["q"] for f in faqs]), ("kw_qa", [f["q"] + " " + f["a"] for f in faqs])]:
    bm = BM25Okapi([toks(t) for t in texts])
    S = np.vstack([bm.get_scores(t) for t in qt])
    runs[name] = np.argsort(-S, axis=1)[:, :K]; scores[name] = np.take_along_axis(S, runs[name], 1)
Q = emb("query", len(queries))
for name in ["faq_q", "faq_qa"]:
    S = Q @ emb(name, len(faqs)).T
    key = "ai_" + name[4:]
    runs[key] = np.argsort(-S, axis=1)[:, :K]; scores[key] = np.take_along_axis(S, runs[key], 1)

# Hybrid: reciprocal rank fusion of keyword (question and answer) and AI (question), k = 60, nothing tuned.
fused = []
for i in range(len(queries)):
    sc = {}
    for m in ["kw_qa", "ai_q"]:
        for r, d in enumerate(runs[m][i]): sc[d] = sc.get(d, 0) + 1 / (60 + r + 1)
    top = sorted(sc, key=lambda d: -sc[d])[:K]; fused.append(top)
runs["hybrid"] = np.array(fused)
scores["hybrid"] = np.array([[0.0] * K for _ in queries])

NAMES = {"kw_q": "Keyword, question only", "kw_qa": "Keyword, question and answer", "ai_q": "AI meaning, question only",
         "ai_qa": "AI meaning, question and answer", "hybrid": "Hybrid (keyword + AI)"}
evalq = [k for k, q in enumerate(queries) if q["id"] in good]
out = {"methods": {}, "per_query": {}}
print(f"{len(evalq)} questions with at least one good answer (of {len(queries)})")
print(f"{'method':34} {'good@1':>7} {'good@3':>7} {'MRR10':>6} {'rated@3':>8}")
for m in NAMES:
    s1 = s3 = rr = rated = 0; hits = []
    for k in evalq:
        qi = queries[k]["id"]; top = [int(ids[d]) for d in runs[m][k][:10]]
        g = [judged.get((qi, f), False) for f in top]
        s1 += g[0]; s3 += any(g[:3]); rr += next((1 / (r + 1) for r, x in enumerate(g) if x), 0)
        rated += sum((qi, f) in judged for f in top[:3]) / 3
        hits.append(next((r + 1 for r, x in enumerate(g) if x), 0))
    n = len(evalq)
    out["methods"][m] = dict(name=NAMES[m], good1=s1 / n, good3=s3 / n, mrr=rr / n, rated3=rated / n)
    out["per_query"][m] = dict(rank=hits, top=[[int(ids[d]) for d in runs[m][k][:3]] for k in evalq], score=[float(x) for x in scores[m][evalq, 0]])
    print(f"{NAMES[m]:34} {s1/n:7.1%} {s3/n:7.1%} {rr/n:6.3f} {rated/n:8.1%}")
out["evalq"] = [queries[k]["id"] for k in evalq]
json.dump(out, open("runs.json", "w"))

"""Builds data/results.json for the results page from the search runs.
Run from work/ after 3-search.py. Prints every number the page and the docs use."""
import json, random, io, contextlib, runpy
import numpy as np

with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("../scripts/3-search.py")
runs, scores, queries, ids, judged, good, faqs, toks, NAMES = (g[k] for k in
    ["runs", "scores", "queries", "ids", "judged", "good", "faqs", "toks", "NAMES"])
byid = {f["id"]: f for f in faqs}
evalq = [k for k, q in enumerate(queries) if q["id"] in good]
n = len(evalq)

def rated(qi, f):
    return "good" if judged.get((qi, f)) else ("not good" if (qi, f) in judged else "not rated")

methods = []
for m in NAMES:
    s1 = s3 = c1 = c3 = r3 = 0
    for k in evalq:
        qi = queries[k]["id"]; top = [int(ids[d]) for d in runs[m][k]]
        st = [judged.get((qi, f), False) for f in top]
        co = [judged[(qi, f)] for f in top if (qi, f) in judged]
        s1 += st[0]; s3 += any(st[:3]); c1 += bool(co) and co[0]; c3 += any(co[:3])
        r3 += sum((qi, f) in judged for f in top[:3]) / 3
    methods.append(dict(key=m, name=NAMES[m], strict1=s1 / n, strict3=s3 / n, rated1=c1 / n, rated3=c3 / n, ratedShare=r3 / n))
    print(f"{NAMES[m]:34} strict {s1/n:.1%} {s3/n:.1%} | rated only {c1/n:.1%} {c3/n:.1%} | top 3 rated {r3/n:.1%}")

# Wording: the largest share of the question's words found in any good article's question.
ov = []
for k in evalq:
    qt = set(toks(queries[k]["q"]))
    ov.append(max(len(qt & set(toks(byid[f]["q"]))) / max(1, len(qt)) for f in good[queries[k]["id"]]))
ov = np.array(ov)
bands = [("Under a third", 0, 1 / 3), ("A third to two thirds", 1 / 3, 2 / 3), ("Two thirds or more", 2 / 3, 1.01)]
wording = []
for label, lo, hi in bands:
    sel = [i for i in range(n) if lo <= ov[i] < hi]
    row = dict(label=label, questions=len(sel))
    for m in ["kw_q", "ai_q", "hybrid"]:
        row[m] = float(np.mean([any(judged.get((queries[evalq[i]]["id"], int(ids[d])), False) for d in runs[m][evalq[i]][:3]) for i in sel]))
    wording.append(row); print("wording", row)

# Confidence: show the first answer only when the top score clears a line. All 1,236 questions.
allk = range(len(queries)); conf = {}
for m in ["kw_q", "ai_q"]:
    top = np.array([scores[m][k, 0] for k in allk])
    first = [judged.get((queries[k]["id"], int(ids[runs[m][k][0]])), False) for k in allk]
    pts = []
    for share in [100, 90, 80, 70, 60, 50, 40, 30, 20]:
        line = np.percentile(top, 100 - share); sh = top >= line
        pts.append(dict(shown=float(sh.mean()), good=float(np.mean([f for f, s in zip(first, sh) if s]))))
    conf[m] = pts; print("confidence", m, [(round(p["shown"], 2), round(p["good"], 3)) for p in pts])
nog = [k for k in allk if queries[k]["id"] not in good]
ai_top = np.array([scores["ai_q"][k, 0] for k in allk])
med_nog = float(np.median(ai_top[nog])); med_rest = float(np.median(np.delete(ai_top, nog)))
print("AI top score median: no good answer", round(med_nog, 3), "others", round(med_rest, 3))

# Question browser: 60 questions picked at random (seed 7) from the scored set.
random.seed(7); pick = sorted(random.sample(evalq, 60))
browse = []
for k in pick:
    qi = queries[k]["id"]
    browse.append(dict(q=queries[k]["q"], good=len(good[qi]), res={m: [dict(t=byid[int(ids[d])]["q"], s=byid[int(ids[d])]["src"], r=rated(qi, int(ids[d])))
                                                        for d in runs[m][k][:3]] for m in ["kw_q", "ai_q", "hybrid"]}))
res = dict(articles=len(faqs), sources=len({f["src"] for f in faqs}), questions=len(queries), scored=n,
           noGood=len(queries) - n, judgedPairs=len(judged), methods=methods, wording=wording, confidence=conf,
           medianTopNoGood=med_nog, medianTopOthers=med_rest, browse=browse)
json.dump(res, open("../data/results.json", "w"), separators=(",", ":"))
print("sources", res["sources"], "wrote data/results.json")

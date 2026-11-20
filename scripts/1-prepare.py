"""Builds the texts to search and the judged pairs from the COUGH files in work/.
Writes faqs.json, queries.json, texts_*.json (for the embedding step) and judged.csv."""
import json, re
import pandas as pd

e = pd.read_csv("FAQ_Bank_eval.csv")
a = pd.read_csv("Annotated_Relevance_Set.csv")
a.columns = ["qi", "query", "fi", "raw", "avg", "label"]

def clean(s):
    return re.sub(r"\s+", " ", str(s if isinstance(s, str) else "")).strip()

e["q"] = e["question"].map(clean)
e["ans"] = e["answer"].map(clean)
faqs = [dict(id=int(r["index"]), q=r.q, a=r.ans, src=str(r.source), kind=str(r.type)) for _, r in e.iterrows()]
queries = a.groupby("qi")["query"].first().map(clean)
json.dump(faqs, open("faqs.json", "w"))
json.dump([dict(id=int(i), q=q) for i, q in queries.items()], open("queries.json", "w"))
json.dump([f["q"] for f in faqs], open("texts_faq_q.json", "w"))
# Question plus the start of the answer: the embedding model reads short texts best.
json.dump([(f["q"] + " " + f["a"])[:600] for f in faqs], open("texts_faq_qa.json", "w"))
json.dump(list(queries.values), open("texts_query.json", "w"))
a[["qi", "fi", "avg", "label"]].to_csv("judged.csv", index=False)
print(len(faqs), "help articles,", len(queries), "questions,", len(a), "judged pairs")

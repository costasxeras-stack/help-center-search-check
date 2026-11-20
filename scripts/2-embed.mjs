// Embeds help articles and questions with a small local model (Universal Sentence Encoder, 512 numbers per text).
// No paid AI calls. Run from work/ after 1-prepare.py.
import { initModel } from "@energetic-ai/embeddings";
import { modelSource } from "@energetic-ai/model-embeddings-en";
import fs from "fs";
const model = await initModel(modelSource);
for (const name of ["faq_q", "faq_qa", "query"]) {
  const T = JSON.parse(fs.readFileSync(`texts_${name}.json`, "utf8")); const t0 = Date.now(); const out = [];
  for (let i = 0; i < T.length; i += 128) { const e = await model.embed(T.slice(i, i + 128)); out.push(...e.map(v => Array.from(v))); }
  const buf = Buffer.alloc(out.length * 512 * 4); let k = 0; out.forEach(v => v.forEach(x => { buf.writeFloatLE(x, k); k += 4; }));
  fs.writeFileSync(`emb_${name}.f32`, buf); console.log(name, T.length, ((Date.now() - t0) / 1000).toFixed(0) + "s");
}

"""Render every question and feed each stored answer back through the checker."""
import glob, json
from playwright.sync_api import sync_playwright
exe = glob.glob('/home/longge/.cache/ms-playwright/chromium-1234/*/chrome')[0]
JS = r'''
() => {
  const out = {n:0, bad:[], unitSet:{}, types:{}, subs:{}};
  for (const sid in PSLE.subjects) for (const q of PSLE.subjects[sid].questions) {
    out.n++;
    let html = "";
    try { html = questionHTML(q); } catch (e) { out.bad.push(q.id + " render: " + e.message); continue; }
    if (/\[\[|\]\]|\{[^{}]*\/[^{}]*\}|\*\*/.test(html.replace(/<[^>]+>/g, ""))) out.bad.push(q.id + " leftover markup: " + html.replace(/<[^>]+>/g, "").match(/.{0,25}(\[\[|\]\]|\{[^{}]*\/[^{}]*\}|\*\*).{0,25}/)[0]);
    q.subtypes.forEach(s => out.subs[sid+"/"+q.topic+"/"+s] = (out.subs[sid+"/"+q.topic+"/"+s]||0)+1);
    q.parts.forEach(p => {
      const a = p.answer; out.types[a.type] = (out.types[a.type]||0)+1;
      if (a.unit) out.unitSet[a.unit] = (out.unitSet[a.unit]||0)+1;
      let tries = [];
      if (a.type === "self") return;
      if (a.type === "sum") return;
      tries.push(a.value);
      if (a.accept) tries.push(...a.accept);
      if (a.type === "number" && a.unit) tries.push(a.unitPos === "before" ? a.unit + a.value : a.value + " " + a.unit, a.value + a.unit);
      for (const t of tries) { const r = checkPart(p, t); if (r !== "right") out.bad.push(q.id + "(" + (p.label||"") + ") own answer rejected: [" + t + "] -> " + JSON.stringify(r)); }
      try { answerText(q, p); p.explanation.map(inline); } catch (e) { out.bad.push(q.id + " answerText: " + e.message); }
    });
  }
  return out;
}'''
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe); pg = b.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///home/longge/code/edutech/index.html')
    r = pg.evaluate(JS)
    print(r['n'], 'questions;', 'answer types', r['types'])
    print('units', r['unitSet'])
    for x in r['bad']: print('  BAD', x)
    print(len(r['bad']), 'problems;', 'page errors:', errs)
    json.dump(r['subs'], open('/tmp/psle-subs.json', 'w'), indent=0)
    b.close()

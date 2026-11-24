#!/usr/bin/env python3
"""Build the question library used by index.html.

Reads   library/<subject>/*.json   (one file per paper, see docs/LIBRARY_FORMAT.md)
Writes  data/<subject>/index.js            question records, no image data
        data/<subject>/images-<topic>.js   base64 images, loaded per topic
        data/<subject>/REVIEW.md           questions held back from play

Usage:
  .venv/bin/python tools/build_library.py                    build everything
  .venv/bin/python tools/build_library.py --check FILE.json   validate one paper only
  .venv/bin/python tools/build_library.py --preview FILE.json OUTDIR
                                           write that paper's cropped images as PNG files
"""
import base64
import glob
import json
import os
import re
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY = json.load(open(os.path.join(ROOT, "library", "taxonomy.json"), encoding="utf-8"))
IMAGE_DPI = 150
ANSWER_TYPES = {"mcq", "number", "fraction", "expression", "text", "sum", "ratio", "self"}
FORMATS = {"mcq", "short", "structured"}
STATUSES = {"verified", "needs-review"}
MARKER = re.compile(r"\[\[([a-z]+\d+)\]\]")


def validate(doc, path):
    """Return (errors, warnings) for one paper file."""
    errs, warns = [], []
    paper = doc.get("paper", {})
    for key in ("id", "subject", "year", "exam", "school", "file"):
        if key not in paper:
            errs.append(f"paper.{key} missing")
    subject = paper.get("subject")
    if subject not in TAXONOMY:
        errs.append(f"paper.subject '{subject}' not in taxonomy")
        return errs, warns
    tax = TAXONOMY[subject]
    topics = {t["id"] for t in tax["topics"]}
    pdf = os.path.join(ROOT, paper.get("file", ""))
    npages = None
    if not os.path.isfile(pdf):
        errs.append(f"paper.file not found: {paper.get('file')}")
    else:
        d = pymupdf.open(pdf)
        npages = len(d)
        scale = paper.get("coordDpi", 100) / 72
        page_w, page_h = d[0].rect.width * scale, d[0].rect.height * scale
    seen = set()
    for q in doc.get("questions", []):
        tag = f"{q.get('section')} Q{q.get('number')}"
        key = (q.get("section"), q.get("number"))
        if key in seen:
            errs.append(f"{tag}: duplicate section/number")
        seen.add(key)
        if q.get("section") not in tax["sections"]:
            errs.append(f"{tag}: section must be one of {sorted(tax['sections'])}")
        if q.get("format") not in FORMATS:
            errs.append(f"{tag}: format must be one of {sorted(FORMATS)}")
        if q.get("topic") not in topics:
            errs.append(f"{tag}: topic '{q.get('topic')}' not in taxonomy")
        if not isinstance(q.get("subtypes"), list) or not q["subtypes"]:
            errs.append(f"{tag}: subtypes must be a non-empty list")
        else:
            for s in q["subtypes"]:
                if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s):
                    errs.append(f"{tag}: subtype '{s}' must be kebab-case")
        if not isinstance(q.get("marks"), int) or q["marks"] < 1:
            errs.append(f"{tag}: marks must be a positive integer")
        if not isinstance(q.get("page"), int) or (npages and not 1 <= q["page"] <= npages):
            errs.append(f"{tag}: page out of range")
        review = q.get("review", {})
        if review.get("status") not in STATUSES:
            errs.append(f"{tag}: review.status must be one of {sorted(STATUSES)}")
        if review.get("status") == "needs-review" and not review.get("note"):
            errs.append(f"{tag}: needs-review requires review.note saying why")
        parts = q.get("parts") or []
        if not parts:
            errs.append(f"{tag}: no parts")
        stem = q.get("stem", "")
        if not stem and not all(p.get("prompt") for p in parts):
            errs.append(f"{tag}: empty stem and a part without prompt")
        if q.get("format") == "mcq":
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) < 2:
                errs.append(f"{tag}: mcq needs options")
            if len(parts) != 1 or parts[0].get("answer", {}).get("type") != "mcq":
                errs.append(f"{tag}: mcq needs exactly one part with answer.type mcq")
            elif opts and parts[0]["answer"].get("value") not in range(1, len(opts) + 1):
                errs.append(f"{tag}: mcq answer value must be 1..{len(opts)}")
        labels = [p.get("label", "") for p in parts]
        if len(set(labels)) != len(labels):
            errs.append(f"{tag}: duplicate part labels")
        if len(parts) > 1:
            if any(not p.get("label") for p in parts):
                errs.append(f"{tag}: multi-part question needs a label on every part")
            if any(not isinstance(p.get("marks"), int) for p in parts):
                errs.append(f"{tag}: multi-part question needs marks on every part")
            elif sum(p["marks"] for p in parts) != q.get("marks"):
                errs.append(f"{tag}: part marks do not add up to question marks")
        for p in parts:
            a = p.get("answer", {})
            if a.get("type") not in ANSWER_TYPES:
                errs.append(f"{tag}{p.get('label','')}: answer.type must be one of {sorted(ANSWER_TYPES)}")
            if a.get("value") in (None, ""):
                errs.append(f"{tag}{p.get('label','')}: answer.value missing")
            if a.get("type") == "sum" and ("sum" not in a or "count" not in a):
                errs.append(f"{tag}{p.get('label','')}: sum answer needs 'sum' and 'count'")
            if a.get("type") != "mcq" and q.get("format") == "mcq":
                errs.append(f"{tag}: mcq format with non-mcq answer")
            exp = p.get("explanation")
            if not isinstance(exp, list) or not exp or not all(isinstance(s, str) and s.strip() for s in exp):
                errs.append(f"{tag}{p.get('label','')}: explanation must be a non-empty list of steps")
        ids = set()
        for im in q.get("images", []):
            ids.add(im.get("id"))
            box = im.get("box", [])
            if not im.get("alt"):
                errs.append(f"{tag}: image {im.get('id')} needs alt text")
            if not (isinstance(im.get("page"), int) and (not npages or 1 <= im["page"] <= npages)):
                errs.append(f"{tag}: image {im.get('id')} page out of range")
            if len(box) != 4 or not (0 <= box[0] < box[2] and 0 <= box[1] < box[3]):
                errs.append(f"{tag}: image {im.get('id')} box must be [x0, y0, x1, y1]")
            elif npages and (box[2] > page_w + 2 or box[3] > page_h + 2):
                errs.append(f"{tag}: image {im.get('id')} box is outside the page ({page_w:.0f} x {page_h:.0f})")
            elif (box[2] - box[0]) < 30 or (box[3] - box[1]) < 20:
                warns.append(f"{tag}: image {im.get('id')} is very small")
        for t in q.get("tables", []):
            ids.add(t.get("id"))
            if not isinstance(t.get("rows"), list) or not t["rows"]:
                errs.append(f"{tag}: table {t.get('id')} has no rows")
        texts = [stem] + [p.get("prompt", "") for p in parts]
        for text in texts:
            for m in MARKER.findall(text):
                if m not in ids:
                    errs.append(f"{tag}: marker [[{m}]] has no matching image/table")
    return errs, warns


def crop_png(pdf_doc, im, coord_dpi):
    f = 72 / coord_dpi
    x0, y0, x1, y1 = [v * f for v in im["box"]]
    zoom = IMAGE_DPI / 72
    mat = pymupdf.Matrix(zoom, zoom).prerotate(im.get("rotate", 0))  # rotate: degrees clockwise, 90/180/270
    pix = pdf_doc[im["page"] - 1].get_pixmap(
        matrix=mat, clip=pymupdf.Rect(x0, y0, x1, y1), colorspace=pymupdf.csGRAY)
    return pix.tobytes("png")


def citation(paper, tax, q):
    return f"{paper['year']} {paper['exam']} {paper['school']} {tax['sections'][q['section']]} Question {q['number']}"


def difficulty(subject, q):
    if subject == "maths":
        if q["section"] == "p1a":
            return 1 if q["marks"] == 1 else 2
        if q["section"] == "p1b":
            return 2
        return 2 if q["marks"] <= 2 else 3
    return 1 if q["format"] == "mcq" else 2


def build():
    total_err = 0
    for subject, tax in TAXONOMY.items():
        files = sorted(glob.glob(os.path.join(ROOT, "library", subject, "*.json")))
        if not files:
            continue
        out_dir = os.path.join(ROOT, "data", subject)
        os.makedirs(out_dir, exist_ok=True)
        questions, held, images_by_topic, papers = [], [], {}, []
        for path in files:
            doc = json.load(open(path, encoding="utf-8"))
            errs, warns = validate(doc, path)
            name = os.path.basename(path)
            for w in warns:
                print(f"  warn {name}: {w}")
            if errs:
                total_err += len(errs)
                for e in errs:
                    print(f"  ERROR {name}: {e}")
                continue
            paper = doc["paper"]
            pdf_doc = pymupdf.open(os.path.join(ROOT, paper["file"]))
            n_ok = 0
            for q in doc["questions"]:
                qid = f"{paper['id']}-{q['section']}-q{q['number']}"
                cite = citation(paper, tax, q)
                if q["review"]["status"] != "verified":
                    held.append((cite, q["review"].get("note", ""), q["review"].get("keyAnswer", ""),
                                 q["review"].get("solvedAnswer", "")))
                    continue
                alias = tax.get("subtypeAliases", {})
                q["subtypes"] = list(dict.fromkeys(alias.get(x, x) for x in q["subtypes"]))
                rec = {
                    "id": qid, "cite": cite, "year": paper["year"], "exam": paper["exam"],
                    "school": paper["school"], "section": q["section"], "number": q["number"],
                    "topic": q["topic"], "subtypes": q["subtypes"], "format": q["format"],
                    "marks": q["marks"], "difficulty": difficulty(subject, q), "stem": q.get("stem", ""),
                    "parts": q["parts"],
                }
                if {"measuring-angles", "measuring-lines-and-angles"} & set(q["subtypes"]):
                    for part in rec["parts"]:
                        ans = part["answer"]
                        if ans["type"] == "number" and ans.get("unit") == "°":
                            ans.setdefault("tolerance", 1)
                if q.get("options"):
                    rec["options"] = q["options"]
                if q.get("tables"):
                    rec["tables"] = q["tables"]
                if q.get("images"):
                    rec["images"] = []
                    for im in q["images"]:
                        key = f"{qid}-{im['id']}"
                        png = crop_png(pdf_doc, im, paper.get("coordDpi", 100))
                        images_by_topic.setdefault(q["topic"], {})[key] = (
                            "data:image/png;base64," + base64.b64encode(png).decode("ascii"))
                        rec["images"].append({"id": im["id"], "key": key, "alt": im["alt"]})
                questions.append(rec)
                n_ok += 1
            papers.append({"id": paper["id"], "year": paper["year"], "exam": paper["exam"],
                           "school": paper["school"], "count": n_ok})
            print(f"  {name}: {n_ok} playable, {len(doc['questions']) - n_ok} held back")
        payload = {"name": tax["name"], "sections": tax["sections"], "topics": tax["topics"],
                   "papers": papers, "questions": questions}
        with open(os.path.join(out_dir, "index.js"), "w", encoding="utf-8") as f:
            f.write("window.PSLE = window.PSLE || {subjects: {}, images: {}};\n")
            f.write(f"PSLE.subjects[{json.dumps(subject)}] = ")
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
            f.write(";\n")
        for old in glob.glob(os.path.join(out_dir, "images-*.js")):
            os.remove(old)
        size = 0
        for topic, imgs in images_by_topic.items():
            p = os.path.join(out_dir, f"images-{topic}.js")
            with open(p, "w", encoding="utf-8") as f:
                f.write("window.PSLE = window.PSLE || {subjects: {}, images: {}};\n")
                f.write("Object.assign(PSLE.images, ")
                json.dump(imgs, f, separators=(",", ":"))
                f.write(");\n")
            size += os.path.getsize(p)
        with open(os.path.join(out_dir, "REVIEW.md"), "w", encoding="utf-8") as f:
            f.write(f"# {tax['name']} — questions held back from play\n\n")
            f.write(f"{len(questions)} questions are playable. {len(held)} are held back until checked by a person.\n\n")
            if held:
                f.write("| Question | Key says | Solved as | Why held back |\n|---|---|---|---|\n")
                for cite, note, key, solved in held:
                    cell = lambda s: str(s).replace("|", "/").replace("\n", " ")
                    f.write(f"| {cite} | {cell(key)} | {cell(solved)} | {cell(note)} |\n")
        print(f"{subject}: {len(questions)} playable from {len(papers)} papers, {len(held)} held back, "
              f"images {size / 1e6:.1f} MB")
    if total_err:
        print(f"{total_err} validation error(s); papers with errors were skipped")
        sys.exit(1)


def main():
    args = sys.argv[1:]
    if args and args[0] == "--check":
        doc = json.load(open(args[1], encoding="utf-8"))
        errs, warns = validate(doc, args[1])
        for w in warns:
            print("warn:", w)
        for e in errs:
            print("ERROR:", e)
        n = len(doc.get("questions", []))
        by = {}
        for q in doc.get("questions", []):
            by[q.get("section")] = by.get(q.get("section"), 0) + 1
        print(f"{n} questions {by}, {len(errs)} error(s), {len(warns)} warning(s)")
        sys.exit(1 if errs else 0)
    if args and args[0] == "--preview":
        doc = json.load(open(args[1], encoding="utf-8"))
        out = args[2]
        os.makedirs(out, exist_ok=True)
        paper = doc["paper"]
        pdf_doc = pymupdf.open(os.path.join(ROOT, paper["file"]))
        for q in doc["questions"]:
            for im in q.get("images", []):
                p = os.path.join(out, f"{q['section']}-q{q['number']:02d}-{im['id']}.png")
                open(p, "wb").write(crop_png(pdf_doc, im, paper.get("coordDpi", 100)))
                print(p)
        return
    if args:
        print(__doc__)
        sys.exit(2)
    build()


if __name__ == "__main__":
    main()

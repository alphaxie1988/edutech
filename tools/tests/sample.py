import json, glob, random, os, sys, base64, re
import pymupdf
root, out, n, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
subject = sys.argv[5]
random.seed(seed); os.makedirs(out, exist_ok=True)
items = []
for f in sorted(glob.glob(f'{root}/library/{subject}/*.json')):
    d = json.load(open(f, encoding='utf-8'))
    for q in d['questions']:
        if q['review']['status'] == 'verified': items.append((d['paper'], q, f))
pick = random.sample(items, n)
index = []
for i, (paper, q, f) in enumerate(pick, 1):
    tag = f"s{i:02d}"
    pdf = pymupdf.open(os.path.join(root, paper['file']))
    pages = sorted({q['page']} | {im['page'] for im in q.get('images', [])})
    page_files = []
    for p in pages:
        fn = f"{out}/{tag}-page{p}.png"; pdf[p-1].get_pixmap(dpi=130, colorspace=pymupdf.csGRAY).save(fn); page_files.append(fn)
    crop_files = []
    for im in q.get('images', []):
        k = 72 / paper.get('coordDpi', 100); x0, y0, x1, y1 = [v*k for v in im['box']]
        mat = pymupdf.Matrix(150/72, 150/72).prerotate(im.get('rotate', 0))
        fn = f"{out}/{tag}-{im['id']}.png"; pdf[im['page']-1].get_pixmap(matrix=mat, clip=pymupdf.Rect(x0, y0, x1, y1), colorspace=pymupdf.csGRAY).save(fn); crop_files.append(fn)
    json.dump(q, open(f"{out}/{tag}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    index.append({'tag': tag, 'paper': paper['id'], 'pdf': paper['file'], 'section': q['section'], 'number': q['number'], 'record': f"{out}/{tag}.json", 'pages': page_files, 'crops': crop_files, 'libraryFile': f})
json.dump(index, open(f"{out}/index.json", 'w'), indent=1)
print(len(index), 'samples in', out)

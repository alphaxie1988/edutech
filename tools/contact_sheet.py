import sys, glob, os, pymupdf
src, out = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(src + '/*.png'))
per = 12
for n in range(0, len(files), per):
    doc = pymupdf.open(); page = doc.new_page(width=1200, height=1200)
    for i, f in enumerate(files[n:n+per]):
        c, r = i % 4, i // 4
        cell = pymupdf.Rect(c*300+8, r*400+24, c*300+292, r*400+392)
        page.insert_text((c*300+8, r*400+16), os.path.basename(f), fontsize=11)
        page.draw_rect(cell, color=(0.8,0,0), width=0.5)
        page.insert_image(cell, filename=f, keep_proportion=True)
    page.get_pixmap(dpi=72).save(f"{out}-{n//per+1}.png"); print(f"{out}-{n//per+1}.png")

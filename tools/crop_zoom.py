# usage: crop.py pdf out.png page x0 y0 x1 y1 [dpi]   (coords in 100-dpi pixels)
import sys, pymupdf
pdf, out, page = sys.argv[1], sys.argv[2], int(sys.argv[3])
x0, y0, x1, y1 = [float(v) * 72 / 100 for v in sys.argv[4:8]]
dpi = int(sys.argv[8]) if len(sys.argv) > 8 else 200
d = pymupdf.open(pdf)
pix = d[page-1].get_pixmap(dpi=dpi, clip=pymupdf.Rect(x0, y0, x1, y1), colorspace=pymupdf.csGRAY)
pix.save(out); print(out, pix.width, pix.height)

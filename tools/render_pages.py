#!/usr/bin/env python3
"""Render every page of a PDF to greyscale PNG.  usage: render_pages.py <pdf> <out-dir> [dpi=100]"""
import os
import sys

import pymupdf

pdf, out = sys.argv[1], sys.argv[2]
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 100
os.makedirs(out, exist_ok=True)
d = pymupdf.open(pdf)
for i, p in enumerate(d, 1):
    pix = p.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    pix.save(f"{out}/p{i:02d}.png")
    print(f"p{i:02d}.png {pix.width}x{pix.height}")
print(len(d), "pages written to", out)

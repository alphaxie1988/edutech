# PSLE Quest

A gamified practice app built from P6 prelim papers. Open `index.html` in a browser (double-click; no server or internet needed).

- **Maths:** 1,035 questions from 23 prelim papers (2025 and 2026).
- **Science:** 584 questions from 15 prelim papers (2025 and 2026).

For private family use only. The questions and diagrams are the schools' copyright; do not publish this folder or host it publicly.

## Using it

1. Pick a subject, then a topic and question type, or **Random mix**.
2. Work the question out on the canvas: pen, eraser, colours, undo; pinch or scroll to zoom, two fingers (or the hand tool) to move around. **Draw on it** copies a diagram onto the canvas.
3. Type the answer (or tap an option) and press **Check**. A wrong answer shows the correct answer with step-by-step working and goes into the **Mistake book**.
4. Written science answers and drawings are self-marked: compare with the model answer and tap right or wrong.

Progress (XP, level, streaks, medals, mistake book) is saved in the browser on that device. Use **Progress → Export** to back it up or move it to another device.

## What is where

| Path | What it is |
|---|---|
| `index.html` | The whole app. |
| `data/<subject>/` | Built question data loaded by the app. `REVIEW.md` lists the questions held back from play and why. |
| `library/<subject>/*.json` | Source of truth: one file per paper (text, answers, explanations, crop boxes). |
| `library/taxonomy.json` | Topics per subject and tag aliases. |
| `docs/SPEC.md` | Requirement spec. |
| `docs/LIBRARY_FORMAT.md` | File format and the step-by-step procedure for extracting a paper. |
| `tools/` | Build and extraction tools. |

## Rebuilding the data

```
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/build_library.py
```

Edit a file in `library/`, rebuild, and reload the page. To release a held-back question, fix it in its library file, set `review.status` to `"verified"`, and rebuild.

## Tests

`tools/tests/` holds browser tests (they need Playwright and a Chromium: `pip install playwright && playwright install chromium`, then adjust the browser path at the top of each script):

- `libtest.py` renders every question and feeds each stored answer back through the checker.
- `checktest.py` runs the answer checker against tricky inputs.
- `uitest.py` and `scitest.py` walk through the app and take screenshots.
- `sample.py` makes a random sample pack for checking questions against the PDFs.

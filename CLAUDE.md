# PSLE Quest

Gamified practice app for a Primary 6 pupil, built from scanned past-year prelim papers. Family use, opened locally by double-clicking `index.html`. Subjects: Maths, Science, English, Chinese, Higher Chinese.

Read first: `docs/SPEC.md` (requirements), `docs/LIBRARY_FORMAT.md` (question file format and extraction procedure), `decision.md` (decisions and reasons).

## Layout

| Path | What it is |
|---|---|
| `index.html` | The whole app: HTML, CSS and JS inline. No libraries, no network calls. |
| `library/<subject>/<paper-id>.json` | Source of truth: one file per paper. Edit these. |
| `library/taxonomy.json` | Subjects, sections, topics, and `subtypeAliases` that merge duplicate tags. |
| `data/<subject>/` | Generated: `index.js`, `images-<topic>.js`, `REVIEW.md`. Never edit by hand. |
| `tools/build_library.py` | Validates `library/` and writes `data/`. |
| `tools/render_pages.py`, `crop_zoom.py`, `contact_sheet.py` | Helpers for reading the scanned PDFs. |
| `tools/tests/` | Playwright browser tests. |
| `PSLE-2025-P6-papers/`, `PSLE-2026-P6-papers/` | The scanned PDFs. Local only (`*.pdf` is gitignored). |

## Commands

Run from the repo root with the repo's virtualenv (`.venv`, needs `pymupdf`).

```
.venv/bin/python tools/build_library.py                      # full build, about 2 minutes
.venv/bin/python tools/build_library.py --check FILE.json     # validate one paper
.venv/bin/python tools/build_library.py --preview FILE.json OUTDIR   # write that paper's image crops
```

Any other argument prints help and exits. After changing anything in `library/`, run the full build, then the tests.

Tests need Playwright and Chromium; each script hard-codes the browser path and the `file://` URL of `index.html` at the top.

```
python tools/tests/checktest.py          # answer-checker cases
python tools/tests/libtest.py            # every stored answer is accepted by the app's checker
python tools/tests/langtest.py OUTDIR english|chinese|higher-chinese [topic]   # passage flow
python tools/tests/uitest.py OUTDIR      # maths flow; scitest.py and touchtest.py likewise
```

## Rules

- **Copyright.** The papers belong to the schools. Keep PDFs out of git. The GitHub repo is public, so ask before pushing, and never publish the app or data anywhere else.
- **Commit and push only when asked.**
- **`index.html` must work from `file://`**: no fetch, no modules, no external scripts or fonts. Data loads through `<script>` tags.
- **Never edit `data/`**; change `library/` and rebuild.
- **Do not change existing question ids.** They key the saved progress in `localStorage` (`psle-quest-v1`). Maths and science ids are unprefixed; other subjects are prefixed with the subject.
- **Answers.** Solve each question independently, then compare with the key. Never copy the key for a question you could not solve. Unresolved or unreadable: `review.status: "needs-review"` with a note; it is then left out of play and listed in `data/<subject>/REVIEW.md`.
- **Pencil and highlighter marks** from previous pupils are common in the scans. If a mark in a crop gives an answer away, hold the question back.
- **Chinese passages are image crops**, never transcribed. Chinese questions and options are transcribed; zoom, and never guess a character.
- **Explanations** use primary-school methods and are written for a 12-year-old. Chinese subjects are explained in Simplified Chinese.
- **Work files** (page renders, previews, screenshots) go in a scratch directory, never in the repo.

## Adding a paper

1. Follow "Procedure for one paper" in `docs/LIBRARY_FORMAT.md`, using the existing `2026-prelim-acsj.json` of that subject as the style reference.
2. `--check` must show 0 errors; preview every crop and look at it.
3. Full build, `libtest.py`, then a spot check of a random sample against the PDF.
4. Update the counts in `README.md` and the status line in `docs/SPEC.md`.

One paper takes a few minutes of agent time; papers are independent, so they can be extracted in parallel, one agent per paper.

## App notes

- Text markup in questions: `{a/b}` fraction, `2{3/10}` mixed number, `**bold**`, `++underline++`, `[[img1]]` / `[[table1]]` placement, `__(29)__` numbered blank, `__(36: word)__` numbered word in a passage.
- Answer types: `mcq`, `number`, `fraction`, `ratio`, `expression`, `text`, `sum`, `self`. The checker is `checkPart` in `index.html`.
- Questions with a `group` share a passage; the app queues the whole group in number order (`nextQuestion`) and shows the passage over the canvas area.
- Writing tasks have `topic: "writing"`; they are excluded from Random mix and give a flat 30 XP.

## Current state (2026-11-24)

Playable questions (held back): Maths 1,035 (20), Science 584 (28), English 1,062 (6), Chinese 394 (16), Higher Chinese 136 (8).

Not done: WA and SA2 papers, phrase-bank flashcards, parent rubric scoring for compositions, listening and oral, testing on a real tablet.

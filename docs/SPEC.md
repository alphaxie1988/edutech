# PSLE Quest — Requirement Spec (v0.1 draft)

Gamified practice app built from the past-year papers in this repo.
Status: built. Playable questions (held back): Maths 1,035 (20), Science 584 (28), English 1,062 (6), Chinese 394 (16), Higher Chinese 136 (8). Date: 2026-11-24.

## 1. Goal and scope

A child picks a subject, picks a kind of question (or random), works the question out by hand on a canvas, types a final answer, and gets instant marking with a worked explanation when wrong. Progress is rewarded with XP, levels, streaks and topic badges.

**In scope for v1**

- Subject screen listing all subjects; **Maths** and **Science** are playable. The others show as "coming soon".
- Maths question library from the **23 prelim papers**: 13 from 2026, 10 from 2025.
- Science question library from the **15 prelim papers**: 13 from 2026, 2 from 2025 (added 2026-11-24 at the owner's request).
- Topic and question-type selection, random mode, mistake book.
- Family use, opened locally from `index.html`. No server, no accounts, one player.

**Out of scope for v1**

- The 37 WA/SA2 2025 maths papers (added later through the same pipeline).
- English, Chinese, Higher Chinese content. The WA/SA2 2025 science papers.
- Multiple profiles, cloud sync, public hosting. The papers are school copyright, so the library is for private use only and must not be published.
- Handwriting recognition. The canvas is scratch paper; only the typed answer is marked.

## 2. Source material (what was found)

| Set | Papers | Pages |
|---|---|---|
| `PSLE-2026-P6-papers/Maths/` (2026 prelims) | 13 | 494 |
| `PSLE-2025-P6-papers/Prelim/Maths/` (2025 prelims) | 10 | 427 |
| **Total** | **23** | **921** |

- All 23 are **scanned images** with almost no text layer, so every question must be transcribed from the page image.
- Each paper follows PSLE format: Paper 1 Booklet A (Q1–18, multiple choice), Paper 1 Booklet B (Q19–30, short answer), Paper 2 (Q1–17, structured, many with parts (a)/(b)). About 47 questions per paper, so **roughly 1,080 questions**.
- Answer keys are at the back of each PDF. They give the option number for MCQ and terse working for the rest. A large diagonal watermark **hides parts of the key**, so the key alone cannot be trusted as the source of answers.
- Question numbers restart in Paper 2, so a citation must name the paper/booklet as well as the number.

## 3. Question library

### 3.1 Record format

One record per question. Parts (a)/(b) stay inside their parent question because they share the stem.

```js
{
  id: "2026-prelim-acsj-p1a-q10",
  source: {
    year: 2026, exam: "Prelim", school: "ACSJ",
    paper: "Paper 1 Booklet A", number: 10,
    file: "PSLE-2026-P6-papers/Maths/P6-Maths-Prelim-2026-ACSJ-Paper.pdf", page: 5,
    citation: "2026 Prelim ACSJ Paper 1 Booklet A Question 10"
  },
  topic: "percentage",                 // one main topic, see 3.3
  subtypes: ["percentage-change"],     // zero or more, see 3.3
  format: "mcq" | "short" | "structured",
  marks: 2,
  difficulty: 1 | 2 | 3,               // from marks and section
  stem: "Text with $inline math$ ...", // fractions etc. in a simple math markup
  images: [{ id: "img1", alt: "Pie chart of cake types", data: "data:image/png;base64,..." }],
  options: ["20%", "25%", "80%", "125%"],        // mcq only
  parts: [{
    label: "a",                        // "" when the question has no parts
    prompt: "What is the total number of students in Primary 6?",
    marks: 1,
    answer: { type: "number", value: "200", unit: "", accept: ["200"] },
    explanation: "Step-by-step working ..."
  }],
  check: "auto" | "self",              // see 5.4
  review: { keyAnswer: "200", solvedAnswer: "200", status: "verified" | "needs-review" }
}
```

### 3.2 Text and images

- Question text is transcribed to text, not kept as a page picture, so it stays sharp and searchable.
- Diagrams, models, graphs, charts, figures and complex tables are cropped from the scan and stored as **base64 PNG** (greyscale, about 150 dpi, cleaned of margins). Simple tables are transcribed as HTML tables.
- Images inside MCQ options (for example, four nets or four figures) are cropped as one image with the option labels kept.

### 3.3 Categories

Two levels: one **topic** per question, plus optional **question-type** tags.

| Topic | Example question types |
|---|---|
| Whole numbers | order of operations, factors and multiples, rounding, number patterns |
| Fractions | four operations, fraction of remainder, fraction of a set, equal fractions |
| Decimals | four operations, conversion, rate and money |
| Percentage | percentage of a quantity, percentage change, discount/GST, percentage before-and-after |
| Ratio | equivalent ratio, constant total, constant difference, one quantity unchanged, changing ratio |
| Rate and speed | rate, average speed, catching up, meeting, part-thereof charges |
| Algebra | simplify, evaluate, form an expression, solve word problem |
| Measurement | time, length/mass/volume units, money |
| Area and perimeter | rectangles and triangles, composite figures, shaded area |
| Circles | circumference, area, quadrants and semicircles, composite with circles |
| Volume | cuboid, water level and transfer, tank filling with rate |
| Angles and geometry | angles in triangles/quadrilaterals, angle chasing, properties of shapes, nets, symmetry |
| Data and average | average, tables, bar/line graphs, pie charts |
| Heuristic problem sums | gap and difference, excess and shortage, assumption, working backwards, grouping, patterns |

The final list is fixed after the first two papers are extracted, then applied to the rest so tags stay consistent.

### 3.4 Answers and explanations

- Every question is **solved independently**, then compared with the paper's answer key. Match: `verified`. Mismatch or key unreadable: `needs-review`, listed in a report for a human to check. Questions that stay unresolved are excluded from play.
- The **explanation is written fresh** as numbered steps in P6 methods (models/units, not secondary-school algebra unless the question is an algebra question). The key's working is used as a reference where readable.
- Questions whose answer is a drawing, a construction or a written reason are kept, but marked `check: "self"`.

### 3.5 Storage and loading

Estimated size is 20–40 MB once images are base64, too large for one HTML file to open quickly. So:

- `index.html` — the app (HTML, CSS, JS in one file).
- `data/maths/index.js` — all question records without image data (small, loaded at start).
- `data/maths/images-<topic>.js` — base64 images per topic, loaded with a `<script>` tag only when that topic is played.

Plain `<script>` data files work when the page is opened directly from disk; nothing needs a web server.

### 3.6 Science

Same record format and pipeline as maths, with these differences:

- Sections are Booklet A (multiple choice, auto-marked) and Booklet B (open-ended).
- Topics follow the MOE themes: Diversity, Cycles, Systems, Interactions, Energy, split into 14 topics (see `library/taxonomy.json`). Question-type tags name the concept tested, such as "food web" or "series and parallel".
- Booklet B answers are written explanations, which cannot be auto-marked reliably. The child writes or types the answer, taps "Show answer", compares with the model answer and key ideas, then marks each part right or wrong. One-word, letter or number answers are still auto-marked.

### 3.7 English, Chinese and Higher Chinese (added 2026-11-24)

- Scope: Paper 2 (language use and comprehension) of every prelim paper, plus Paper 1 writing tasks where the PDF has them. Listening and oral are out of scope (no audio; cannot be marked).
- **Passage groups:** questions that share a passage, poster, dialogue or cloze text point to one shared group. The app shows the passage in the area normally used by the canvas, with a Passage / Scratch pad switch, and plays the group's questions in order. The blank or word the current question is about is highlighted.
- English passages are transcribed text. Chinese passages are image crops of the scan, so no character can be mistyped; Chinese questions and options are transcribed.
- Marking: multiple choice, word-bank letters, editing corrections and cloze words are auto-marked (cloze accepts the key's word plus clearly correct alternatives). Synthesis, open-ended comprehension and message writing are self-marked against the model answer; a typed answer identical to the model answer is marked right automatically. Chinese character answers may be typed, or written on the scratch pad and self-marked.
- Writing: each task shows the prompt and pictures, a planning space, and a checklist written for that task. No automatic grading. "Copy a feedback request" puts the task, the child's typed writing and a marking request on the clipboard for pasting into Claude or sending to a parent. Writing tasks are left out of Random mix and give a flat 30 XP.
- Not built yet: phrase-bank flashcards (好词好句), parent rubric scoring with history, timed mode.

The exact file format and the step-by-step extraction procedure are in `docs/LIBRARY_FORMAT.md`.

## 4. Extraction pipeline

Run once per paper, repeatable for the remaining papers and other subjects later.

1. Render each PDF page to PNG.
2. Split into question pages and answer-key pages.
3. Transcribe each question: stem, options, parts, marks, citation.
4. Crop diagrams and attach them to the question.
5. Read the answer key; solve the question independently; compare.
6. Classify topic and question types; set difficulty.
7. Write explanation.
8. Validate: schema check, every citation unique, every image referenced, MCQ answer is one of the options, counts per paper match the expected 47 (differences listed).
9. Emit data files and a `data/maths/REVIEW.md` report of `needs-review` items.

Pilot: **2026 ACSJ** and one 2025 paper are done first and reviewed by you before the other 21 are run.

## 5. App behaviour

### 5.1 Screens

1. **Subject select** — Maths active; other subjects greyed out. Shows player level, XP and streak.
2. **Maths menu** — topic cards with mastery ring and question count; tap a topic to see its question types; buttons for **Random**, **Mistake book**.
3. **Question screen** — see 5.2.
4. **Result panel** — correct/wrong, XP gained, explanation, source citation, Next.
5. **Progress** — per-topic accuracy, badges, history.

### 5.2 Question screen layout

- **Top:** question text and images (tap an image to enlarge), citation in small print, marks.
- **Middle:** white canvas filling the remaining space.
- **Bottom:** answer input and **Check** button.

### 5.3 Canvas

- Draw with finger, stylus or mouse; pen and eraser; a few colours and two widths; undo, redo, clear.
- Canvas is effectively unlimited: pan by two-finger drag (or hand tool / space-drag on desktop), zoom by pinch or scroll wheel, with a "reset view" button.
- When a stylus is in use, finger touches pan instead of drawing (palm rejection).
- Strokes are stored as vectors so they stay sharp at any zoom.
- Work is kept while the question is open and after checking, so the child can compare it with the explanation. It is cleared on Next.

### 5.4 Answering and checking

- **MCQ:** four option buttons instead of a text box.
- **Short/structured:** one text box per part, with the unit shown beside the box when the question fixes it.
- Matching is forgiving on form, strict on value: ignores spaces, case, `$`, commas and trailing units; accepts `1/2`, `0.5`; mixed numbers typed as `2 3/10`; ratios as `3:4`; times as `3.45 pm` / `15 45`. Fractions must be in simplest form only when the question says so.
- **Self-check questions:** no text box; "Show answer", then the child taps "I got it right" / "I got it wrong".
- **Correct:** celebration, XP, Next.
- **Wrong:** show the correct answer and the step-by-step explanation straight away; the question goes into the mistake book. (No second attempt in v1 — see open questions.)
- Multi-part questions are correct only when all parts are correct; XP is given per correct part.

### 5.5 Gamification

- **XP and levels:** XP per correct part scaled by marks; level thresholds grow gradually; level-up animation.
- **Streaks:** consecutive-correct streak with a small XP bonus, and a daily streak for answering at least 5 questions in a day.
- **Topic mastery badges:** bronze / silver / gold per topic based on questions answered correctly and recent accuracy; ring on each topic card.
- **Mistake book:** wrong questions return in a dedicated mode and are also mixed into random play; a question leaves the book after being answered correctly twice on different days.
- Random mode avoids repeats until the pool is used up and favours weaker topics slightly.

### 5.6 Saving

Progress, XP, streaks and the mistake book are saved in the browser (`localStorage`) on that device. An export/import button saves progress to a file as a backup, because clearing browser data would otherwise erase it.

## 6. Non-functional

- Works offline from a double-clicked `index.html` in current Chrome, Edge and Safari; tablet-first layout, also usable on a laptop.
- No external libraries required at run time; no network calls.
- Question appears within about a second of selection; drawing has no visible lag.
- Text sized for a child; large touch targets; English UI.

## 7. Acceptance criteria

- Library holds all extractable questions from the 23 papers; each has topic, answer, explanation and a unique citation in the form "2026 Prelim ACSJ Paper 1 Booklet A Question 10".
- No question is playable while marked `needs-review`.
- A spot check of 50 random questions against the PDFs finds no wrong answers and no missing diagrams.
- All flows in section 5 work on a tablet with touch and on a desktop with mouse.
- Progress survives closing and reopening the browser.

## 8. Milestones

1. Spec agreed.
2. Pilot extraction (2 papers) and review of format, categories and explanation style.
3. Full extraction of the remaining 21 papers and review report.
4. App build: screens, canvas, checking.
5. Gamification and mistake book.
6. Test on the target device; fix; add remaining papers and subjects later.

## 9. Decisions confirmed (2026-11-24)

1. **Explanations are written by Claude** in P6 methods, since the keys give only terse, partly hidden working.
2. **One attempt per question**, then the answer and explanation are shown.
3. **Main device is a tablet with touch or stylus**, with laptop as secondary.
4. **Multiple choice uses four option buttons**; multi-part questions get one answer box per part.
5. **Data sits in `data/` files next to `index.html`** rather than inside one huge HTML file.
6. **Unverifiable questions are left out** of play and listed in the review report.
7. Questions needing a drawn or written answer are included as self-check rather than dropped.
8. The canvas is scratch paper only; only the typed answer is marked.

# Question library — format and extraction procedure

One JSON file per paper in `library/<subject>/<paper-id>.json`. `tools/build_library.py` turns these into the `data/` files that `index.html` loads. The worked reference is `library/maths/2026-prelim-acsj.json`: read it before writing a new paper file.

## Procedure for one paper

All commands run from the repo root. Work files (page images, zooms, previews) go in a scratch directory, never in the repo.

1. **Render the pages** (greyscale, 100 dpi; an A4 page is about 827 × 1169 px):
   `.venv/bin/python tools/render_pages.py <pdf> <scratch-dir> 100`
2. **Read every page image** in order: question pages first, then the answer-key pages at the back. Do not skip pages. Note for each question: page number, section, number, marks, text, options, parts, and any diagram.
3. **Zoom whenever anything is unclear** (smudged digits or signs, small labels, angle marks, graph values):
   `.venv/bin/python tools/crop_zoom.py <pdf> <out.png> <page> <x0> <y0> <x1> <y1> 250`
   Coordinates are in 100-dpi page pixels, the same pixels as the rendered page image.
4. **Solve every question yourself** before looking at the key, then compare with the key.
   - Agree: `status: "verified"`.
   - Disagree: re-read the question at high zoom and re-solve. Most disagreements are misread digits, labels or diagram details. If the key is right after all, fix and mark `verified`. If you are confident the key is wrong, or the key is unreadable and you cannot be sure of your own answer, or the question itself is unreadable or ambiguous, mark `needs-review` and explain in `review.note`. Never copy the key's answer for a question you could not solve yourself.
   - The key has a large watermark over it; zoom to read around it.
5. **Write the JSON file** in the format below.
6. **Validate**: `.venv/bin/python tools/build_library.py --check library/<subject>/<file>.json` — fix every error. Check the question counts printed per section against the paper.
7. **Check every crop**: `.venv/bin/python tools/build_library.py --preview library/<subject>/<file>.json <scratch>/prev` then `.venv/bin/python tools/contact_sheet.py <scratch>/prev <scratch>/sheet` (this writes `sheet-1.png`, `sheet-2.png`, …) and look at each sheet image. Every diagram must be complete (no clipped labels, arrows or dimensions) and must not contain stray question text, answer lines, page margins or "Ans:" blanks. Adjust boxes and repeat until clean.
8. Do **not** run the full build and do not edit any other file.

## File layout

```json
{
  "paper": {
    "id": "2026-prelim-acsj",
    "subject": "maths",
    "year": 2026,
    "exam": "Prelim",
    "school": "ACSJ",
    "schoolFull": "Anglo-Chinese School (Junior)",
    "file": "PSLE-2026-P6-papers/Maths/P6-Maths-Prelim-2026-ACSJ-Paper.pdf",
    "coordDpi": 100
  },
  "questions": [ ... ]
}
```

`school` is the short name used in citations ("2026 Prelim ACSJ Paper 1 Booklet A Question 10"). The build makes the id and citation from `paper` + `section` + `number`.

## Question record

| Field | Meaning |
|---|---|
| `section` | Maths: `p1a` (Paper 1 Booklet A), `p1b` (Paper 1 Booklet B), `p2` (Paper 2). Science: `a` (Booklet A), `b` (Booklet B). |
| `number` | Question number as printed. |
| `page` | PDF page (1-based) where the question starts. |
| `format` | `mcq`, `short` (Paper 1 Booklet B), or `structured` (Maths Paper 2, Science Booklet B). |
| `marks` | Total marks for the question. |
| `topic` | One topic id from `library/taxonomy.json`. Pick the main skill the question tests. |
| `subtypes` | One to three kebab-case question-type tags. Reuse the tags listed below where they fit; make a new one only when none fits. |
| `stem` | Shared question text. May be `""` when each part carries its own prompt. |
| `options` | MCQ only: the option texts in order (1) to (4). |
| `images` | Diagrams to crop: `{ "id": "img1", "alt": "...", "page": 7, "box": [x0, y0, x1, y1] }`. |
| `tables` | Simple tables transcribed as data: `{ "id": "table1", "header": [...], "rows": [[...], ...] }`. A cell may be `{ "t": "text", "rowspan": 2 }` or `{ "t": "text", "colspan": 2 }`. |
| `parts` | One entry per answer blank; see below. |
| `review` | `{ "keyAnswer": "...", "solvedAnswer": "...", "status": "verified" \| "needs-review", "note": "..." }`. `note` is required for `needs-review`, and is also used to record anything a reader should know (a smudged digit that was inferred, an unstated assumption). |

### Text rules

- Transcribe the question faithfully and completely, fixing only scan damage. Do not paraphrase or shorten. Leave out "Ans: ____" lines, mark brackets like `[2]`, and page furniture.
- Fractions: `{3/10}`. Mixed numbers: `2{3/10}`. Algebraic fractions: `{9h/2}`.
- Use real symbols: `×`, `÷`, `−`, `°`, `π`, `∠`, `²`, `³`, `≤`. Bold: `**not**`.
- Line break: `\n`. To place an image or table inside the text, write `[[img1]]` or `[[table1]]` on its own line. Images without a marker are shown after the stem.
- Markers also work inside a part's `prompt` when a diagram belongs to one part only; the image itself is still listed in the question's `images`.
- When one stimulus is shared by two questions ("Use the information below to answer Questions 10 and 11"), repeat the intro text and the same image box in both questions so each stands alone.
- Where the paper has the pupil write on the paper (two blanks, tick a box, draw), add a short bracketed instruction saying how to type or draw the answer, as in the reference file.

### Images

- Crop only the diagram, chart, graph, figure or picture, with a few pixels of white margin. Text of the question stays in `stem`.
- Transcribe simple tables as `tables`. Crop a table as an image only when it contains pictures or is too complex to transcribe.
- When MCQ options are pictures, crop one image containing all the options with their (1)–(4) labels and set `options` to `["Option (1)", "Option (2)", "Option (3)", "Option (4)"]` (or a more natural label such as "Figure (1)").
- `alt` describes what the diagram shows, including the labels and values a reader needs.
- A question that needs a diagram but whose diagram is unreadable in the scan is `needs-review`. So is a question whose scanned diagram already has the answer drawn or written on it and cannot be cropped clean. Faint stray pencil marks that do not give the answer away are acceptable.
- If a page is printed sideways, add `"rotate": 90` (degrees clockwise; 180 and 270 also work) to the image so the crop comes out upright. The `box` stays in the coordinates of the page as rendered.
- A table may omit `header` when the printed table has no header row. Cells may use `rowspan` or `colspan`, in the header too.
- If the unit appears only on the answer line, set `unit` on the answer; do not add words to the stem.

### Parts and answers

A question with no (a)/(b) has one part with `"label": ""`. A multi-part question gives every part a `label` ("a", "b", "bi"…), a `prompt`, and `marks` that add up to the question's marks.

`answer.type`:

| Type | Use for | Fields |
|---|---|---|
| `mcq` | Multiple choice | `value`: option number 1–4; optional `accept`: other option numbers the key also accepts |
| `number` | Any number: whole, decimal, money, angle, time duration | `value`: string such as `"112.56"`; optional `unit` (`"cm²"`, `"°"`, `"$"`, `"kg"`), `unitPos: "before"` for `$`; optional `tolerance` (a number) for measured or read-off values. Angles in questions tagged `measuring-angles` get ±1° automatically. |
| `fraction` | Fractions and mixed numbers | `value`: `"11/20"` or `"2 3/10"`; `simplest: true` only when the question demands simplest form or a mixed number |
| `ratio` | Ratios, including three-term ratios | `value`: `"3:4"` or `"10:6:9"` |
| `expression` | Algebraic expressions | `value`: display form `"12n + 18"`; `accept`: equivalent typed forms without spaces, e.g. `["12n+18", "18+12n"]` |
| `text` | A word, name, letter, month, time of day (`"3.45 pm"`), or list of letters | `value`: display form; `accept`: lower-case variants a child might type |
| `sum` | "Write one possible pair" where any numbers with a fixed total are right | `count`, `sum`, and `value` describing the rule |
| `self` | Cannot be auto-marked: drawings, constructions, written reasons, explanations | `value`: the model answer in words |

- "Circle the correct word" or "tick the box" answers are `text` with the chosen words as `value`, an `accept` list, and a bracketed instruction such as "(Type is or is not.)".
- When the question's marks printed on the paper look inconsistent, choose the marks that make the section total match the total printed in the section header, and say so in `review.note`.
- Give money to the form the key uses (`"1.50"`); the app compares numbers by value, so `1.5` is accepted.
- If the question asks for a specific unit, put the number in that unit and set `unit`.
- Each part has an `explanation`: a list of short steps, written for a 12-year-old, using primary-school methods (units and parts, models, assumption, working backwards, listing) rather than simultaneous equations. Algebra is fine only for algebra-topic questions. Every step shows its working, and the last step states the answer. For MCQ, end by naming the option. Write your own explanation; use the key's working only as a reference.

## Maths topics

`whole-numbers`, `fractions`, `decimals`, `percentage`, `ratio`, `rate-speed`, `algebra`, `measurement`, `area-perimeter`, `circles`, `volume`, `geometry`, `data`, `heuristics`.

Choose `heuristics` only when the method is the point and no single content topic fits (assumption, gap and difference, excess and shortage, working backwards, patterns, redistribution). A fraction problem solved with units is `fractions`.

### Maths subtype tags in use

- whole-numbers: `numbers-in-words`, `place-value`, `rounding`, `order-of-operations`, `factors-and-multiples`, `multiples`, `guess-and-check`, `four-operations-word-problem`
- fractions: `comparing-fractions`, `fraction-operations`, `fraction-of-a-whole`, `fraction-of-remainder`, `equal-quantity`, `units-and-parts`, `total-value`, `sum-and-difference`, `before-and-after`
- decimals: `comparing-decimals`, `decimal-to-fraction`, `multiplying-decimals`, `dividing-decimals`, `reading-scales`, `money`
- percentage: `percentage-of-a-quantity`, `percentage-change`, `discount-gst-interest`, `one-quantity-unchanged`, `constant-total`, `constant-difference`, `before-and-after`
- ratio: `fraction-and-ratio`, `equivalent-ratio`, `ratio-and-quantity`, `limiting-ingredient`, `one-quantity-unchanged`, `constant-total`, `constant-difference`, `changing-ratio`
- rate-speed: `rate`, `part-thereof-charges`, `duration`, `average-speed`, `distance-speed-time`, `catching-up`, `meeting`, `taps-and-tanks`
- algebra: `simplifying-expressions`, `evaluating-expressions`, `forming-expressions`, `algebra-word-problem`, `solving-equations`
- measurement: `estimation`, `time-24-hour`, `duration`, `unit-conversion`, `money`
- area-perimeter: `area-of-triangle`, `area-of-composite-figure`, `shaded-area`, `perimeter-of-composite-figure`, `cut-and-rearrange`, `area-on-grid`, `drawing`
- circles: `circumference`, `area-of-circle`, `semicircles`, `quarter-circles`, `perimeter-of-composite-figure`, `area-of-composite-figure`, `cut-and-rearrange`
- volume: `unit-cubes`, `volume-of-cuboid`, `water-transfer`, `equal-water-level`, `water-level-rise`, `taps-and-tanks`, `nets`
- geometry: `symmetry`, `angles-on-a-straight-line`, `angles-at-a-point`, `vertically-opposite-angles`, `angles-in-triangle`, `isosceles-triangle`, `equilateral-triangle`, `angles-in-square`, `angles-in-parallelogram`, `angles-in-rhombus`, `angles-in-trapezium`, `cubes-and-cuboids`, `nets`, `properties-of-shapes`, `direction-and-turns`, `tessellation`
- data: `reading-tables`, `bar-graph`, `line-graph`, `pie-chart`, `average`, `greatest-and-least`, `percentage-of-a-quantity`
- heuristics: `patterns`, `intervals-and-gaps`, `redistribution`, `assumption-method`, `gap-and-difference`, `excess-and-shortage`, `working-backwards`, `guess-and-check`, `grouping`, `equal-stage`

## Science

Same file layout with `"subject": "science"`, sections `a` (Booklet A, multiple choice) and `b` (Booklet B, open-ended). The worked reference is `library/science/2026-prelim-acsj.json`.

### Answers

- Booklet A is `mcq`. Answer it yourself first, then compare with the key. Still disagree after zooming and re-thinking: `needs-review`.
- Booklet B parts are `self`, except a part whose whole answer is one unambiguous word, letter, name or number: use `text` or `number` with a generous `accept` list. One-idea sentence answers ("It is waterproof") stay `self`.
- For `self`, `value` is the model answer in full sentences, built from the key (schools are strict about key phrases) and checked against your own understanding. `explanation` lists the marking points a marker looks for and why, naming the science concept. In `review`, put the key's wording in `keyAnswer` and "agrees with key" (or your disagreement) in `solvedAnswer`. Mark `needs-review` only if the key's answer is unreadable or scientifically wrong.
- Part marks are whole numbers. Sub-blanks that share one mark, or carry half marks, are merged into one part.
- Fill-in chains (for example an energy-conversion chain with several blanks) are one `self` part; write the chain with ___ blanks in the prompt and the completed chain in `value`.
- Drawing answers (add an arrow to a food web, draw a ray) are `self`, with the drawing described in words in `value` and "(Draw it on your canvas.)" in the prompt.
- MCQ explanations: 2 to 4 short steps that name the concept, say why the right option is right, and say why the most tempting wrong option is wrong. End by naming the option.

### Text, options and pictures

- Science stems usually run text, diagram, more text, so always place images and tables with `[[img1]]` / `[[table1]]` markers, in the stem or in the part prompt they belong to (images are still listed at question level). Questions often continue on the next page; give each image its own `page`.
- Lists of statements A, B, C, D above the options go in the stem, one per line.
- Options that are rows of a table are written as text in the pattern `"Part K: fruit. Part L: stem. Substance A: water."`, one string per option. Options that are pictures are one crop with the (1)–(4) labels, and `options` is `["Option (1)", ...]`.
- Tables that mix pictures and text are cropped whole as an image, with the text repeated in `alt`.
- If ticks, marks or labels inside an option table or picture are missing from the scan, mark `needs-review`; do not guess. Where the scan has a handwritten correction to the question, transcribe the corrected wording and say so in `review.note`.

### Topics

Use the ids in `library/taxonomy.json`. Where things go:

| Topic id | Covers |
|---|---|
| `diversity-living` | classifying plants, animals, fungi and bacteria; characteristics of living things |
| `diversity-materials` | properties and uses of materials |
| `cycles-life` | life cycles; reproduction in plants (flower parts, pollination, fertilisation, seed dispersal, germination) and humans; heredity |
| `cycles-matter-water` | states of matter, properties of matter, changes of state, heating and cooling curves, the water cycle |
| `systems-plants` | plant parts and transport of water and food |
| `systems-human` | digestive, respiratory and circulatory systems, including gas exchange in fish and plants |
| `systems-cells` | cells and cell parts |
| `systems-electrical` | circuits, conductors, switches, series and parallel, brightness of bulbs |
| `interactions-magnets` | magnets, magnetic materials, making magnets, electromagnets |
| `interactions-forces` | friction, gravity, elastic spring force, effects of forces |
| `interactions-environment` | food chains and webs, populations and communities, adaptations, decomposers, human impact on the environment |
| `energy-light-heat` | light and shadows, reflection, heat and temperature, heat conductors, expansion and contraction |
| `energy-photosynthesis` | photosynthesis and respiration as energy processes, rate of photosynthesis |
| `energy-forms` | forms of energy, energy conversions, potential and kinetic energy |

### Subtype tags

Subtypes name the concept tested. Use one to three per question, reusing these where they fit:

`adaptations`, `structural-adaptations`, `behavioural-adaptations`, `camouflage`, `classifying-animals`, `classifying-plants`, `bacteria-and-fungi`, `properties-of-materials`, `life-cycle-of-insects`, `life-cycle-of-animals`, `life-cycle-of-plants`, `parts-of-a-flower`, `pollination`, `fertilisation`, `seed-dispersal`, `germination`, `human-reproductive-system`, `heredity`, `properties-of-matter`, `air-can-be-compressed`, `changes-of-state`, `boiling`, `melting`, `condensation`, `evaporation-rate`, `heating-curve`, `water-cycle`, `plant-transport-system`, `stomata`, `digestive-system`, `respiratory-system`, `circulatory-system`, `gas-exchange`, `heart-rate-and-exercise`, `cell-parts`, `closed-circuit`, `conductors-and-insulators`, `series-and-parallel`, `switches`, `brightness-of-bulbs`, `magnetic-materials`, `making-magnets`, `strength-of-magnets`, `electromagnet`, `friction`, `gravity`, `elastic-spring-force`, `springs`, `ramps`, `food-chain`, `food-web`, `population-change`, `decomposers`, `competition-for-light`, `human-impact`, `light-travels-in-straight-lines`, `how-we-see`, `reflection-of-light`, `shadows`, `heat-gain`, `heat-loss`, `heat-conductors`, `expansion-and-contraction`, `rate-of-photosynthesis`, `conditions-for-growth`, `energy-conversion`, `potential-and-kinetic-energy`.

Process-skill tags, added alongside a concept tag when the question is about method: `experiment-design`, `fair-test`, `variables`, `control-set-up`, `reliability`, `planning-an-experiment`, `reading-graphs`, `reading-tables`.

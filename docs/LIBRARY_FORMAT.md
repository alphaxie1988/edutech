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

## Languages (English, Chinese, Higher Chinese)

Same file layout and question record as above, with `"subject": "english"`, `"chinese"` or `"higher-chinese"`, plus **passage groups** for questions that share a passage. Worked references: `library/english/2026-prelim-acsj.json`, `library/chinese/2026-prelim-acsj.json`, `library/higher-chinese/2026-prelim-acsj.json`.

What to extract: every question of Paper 2 (language use and comprehension), and the Paper 1 writing tasks if the PDF contains them. Skip listening comprehension and oral pages. One record per question number, exactly as numbered on the paper, so the citation reads "2026 Prelim ACSJ Paper 2 Booklet A Question 21".

### Sections

- English: `a` (Paper 2 Booklet A), `b` (Paper 2 Booklet B), `p1` (Paper 1 writing).
- Chinese and Higher Chinese: `p2` (Paper 2), `p1` (Paper 1 composition).

### Passage groups

A paper file may have a top-level `"groups"` list next to `"questions"`:

```json
"groups": [
  { "id": "g1",
    "text": "Read the passage and fill each blank with a suitable word.\n\nFor thousands of years, people have admired ivory for its beauty. During the Stone Age, ivory from the mammoth was __(29)__ to make household items.",
    "images": [ { "id": "img1", "alt": "...", "page": 6, "box": [x0, y0, x1, y1] } ],
    "tables": [ ... ] }
]
```

A question that needs the passage says `"group": "g1"`. The app shows the passage in a large reading area and plays the group's questions one after another, in number order. Rules:

- Every question in a group has the same `topic`.
- `text` starts with the section instruction, then a blank line, then the passage. Paragraphs are separated by `\n`. Place images and tables with `[[img1]]` / `[[table1]]` on their own line.
- Blanks that a question fills are written `__(29)__`, using the question number. The app highlights the current question's blank.
- A numbered word in the passage that a question is about (an underlined vocabulary word, or an error to correct in an editing passage) is written `__(36: begining)__`: the number, a colon, then the word exactly as printed, **including its deliberate error**. Never correct an editing passage.
- Other underlining is `++word++`; bold is `**word**`. Both also work in stems, options and prompts. Use `++…++` for the underlined word in "closest in meaning to the underlined word" questions, and for the dotted or underlined characters in Chinese questions.
- Line-numbered comprehension passages: do not copy the line numbers; where a question says "lines 12–15", keep the wording as printed and add the paragraph in brackets, e.g. "(lines 12–15, paragraph 2)". Number the paragraphs in `text` as "**1** …", "**2** …" when questions refer to lines or paragraphs.
- A word bank (letters A–Q with words) goes in the group as a table without header, e.g. cells "(A) after", "(B) and".
- **English passages are transcribed as text**, complete and exact. Visual texts (posters, flyers, web pages) are image crops, with all their wording repeated in `alt`.
- **Chinese passages are image crops**, not transcribed text: crop the whole passage (the instruction line may be left in), one image per page when it runs over pages, and set `text` to the instruction line followed by the markers. This avoids wrong characters. `alt` is a one-line summary of the passage in Chinese. Passage crops must not include the questions that follow. Chinese questions, options and prompts are still transcribed as text; zoom (step 3) whenever a character is not perfectly clear, and never guess a character.
- When a Chinese passage image has numbered blanks (短文填空 with `Q16` inside the passage), the question stem says which blank it is, e.g. "Q16 的答案是：".

### Answers

- Multiple choice: `format: "mcq"` with `options`, as in science. Answer every one yourself before reading the key; disagreement after re-checking is `needs-review`.
- Word-bank cloze: `text`, with the letter as `value` and the word in `accept` (`"value": "J", "accept": ["j", "used"]`); the explanation names the word. For Chinese numbered word banks use the number as `value` and the word in `accept`.
- Editing (spelling or grammar correction), comprehension cloze, and any one-word answer: `text` with the correct word as `value`, and every alternative the key allows in `accept`. For comprehension cloze add other words that are clearly correct in context only when you are sure.
- 改正错别字 and other answers that are one or two Chinese characters: `text` with the characters as `value`. The app lets the child write on the scratch pad and self-mark if they cannot type Chinese.
- Synthesis and transformation, open-ended comprehension, 完成对话 written answers, sentence writing: `self`. `value` is the model answer from the key in full; put other accepted wordings in `accept` (a typed answer that matches one exactly is marked right automatically). `explanation` lists what the marker looks for (for synthesis: the grammar rule; for comprehension: where the evidence is in the passage and the key points needed).
- True/false-with-reason tables, sequencing tables and similar: one part per row, each `self`, or `text` when the whole answer is one word such as "True".
- Format is `mcq`, `short` (one-word or one-line typed answers) or `structured` (written answers).
- Explanations teach: for grammar say the rule; for vocabulary give the meaning of the right word and of the most tempting wrong one; for comprehension point to the sentence that gives the answer. English subjects in English; Chinese subjects in Simplified Chinese (short and simple).
- In `review`, `keyAnswer` is the key's answer and `solvedAnswer` your own. The watermark hides parts of the key; zoom around it. If a key answer cannot be read and you are not certain of the answer yourself, mark `needs-review`.

### Writing tasks (Paper 1)

Only if the PDF contains them. One record per task, `section: "p1"`, `topic: "writing"`, `format: "structured"`, one `self` part:

- English situational writing: `subtypes: ["situational-writing"]`. The stimulus (poster, email, note) is an image crop in `images`, with its full text in `alt`; `stem` is the task wording and the bullet points to include. `value`: "There is no single model answer. Check your writing against the points below." `explanation`: the checklist (purpose, audience, context, each required content point, format, tone).
- English continuous writing: `subtypes: ["continuous-writing"]`. Topic and the three pictures (one crop, described in `alt`). `explanation`: a planning checklist that fits this topic (how the topic could be interpreted for each picture, a story arc, an ending that returns to the topic).
- Chinese 作文: one record per option (命题作文 and 看图作文), numbered 1 and 2, `subtypes: ["topic-composition"]` or `["picture-composition"]`; picture series cropped as one image. Explanation in Chinese: 审题, 开头, 经过, 结尾, 好词好句 suggestions that fit the topic.

### Topics

English (`library/taxonomy.json`):

| Topic id | Section of the paper |
|---|---|
| `grammar` | Grammar multiple choice |
| `vocabulary` | Vocabulary multiple choice (single sentences) |
| `vocabulary-cloze` | Vocabulary in context: passage with underlined words, choose the closest meaning (group) |
| `visual-text` | Visual text comprehension (group) |
| `grammar-cloze` | Grammar cloze with word bank (group) |
| `editing` | Editing for spelling and grammar (group) |
| `comprehension-cloze` | Comprehension cloze (group) |
| `synthesis` | Synthesis and transformation |
| `comprehension` | Open-ended comprehension (group) |
| `writing` | Paper 1 |

English subtype tags: grammar `tenses`, `subject-verb-agreement`, `question-tags`, `prepositions`, `connectors`, `pronouns`, `quantifiers`, `modals`, `conditionals`, `relative-pronouns`, `passive-voice`, `infinitives-and-gerunds`, `phrasal-verbs`, `comparatives`; vocabulary `word-meaning`, `phrasal-verbs`, `idioms`, `collocation`; editing `spelling`, `grammar`; synthesis `reported-speech`, `neither-nor`, `either-or`, `despite-in-spite-of`, `unless`, `relative-clause`, `passive-voice`, `noun-form`, `no-sooner-than`, `not-only-but-also`, `preference`, `conditionals`, `participle-phrase`; comprehension and visual text `factual`, `inference`, `vocabulary-in-context`, `referencing`, `true-false-with-reason`, `sequencing`, `evidence-phrase`, `character-and-feelings`, `purpose-and-audience`, `cause-and-effect`; cloze `connectors`, `prepositions`, `pronouns`, `verb-forms`, `articles-and-determiners`, `contextual-vocabulary`.

Chinese:

| Topic id | Section of the paper |
|---|---|
| `pinyin` | 汉语拼音 questions |
| `vocabulary` | 字词 questions: choose the word, meaning of the underlined word |
| `sentences` | 关联词, sentence structure, correct usage of a word in a sentence, 病句 |
| `cloze` | 短文填空 (group) |
| `comprehension-mcq` | 阅读理解一, multiple choice (group) |
| `dialogue` | 完成对话 (group) |
| `functional-text` | Notices, posters, messages with questions; the short reply/message writing question (group) |
| `comprehension-open` | 阅读理解二 open-ended (group) |
| `writing` | 作文 |

Higher Chinese: `cloze` (选词填空), `error-correction` (改正错别字), `language-use` (any other 语文应用 section), `comprehension` (阅读理解, group), `writing` (作文).

Chinese subtype tags (kebab-case pinyin or English): `pinyin`, `word-choice`, `word-meaning`, `measure-words`, `connectors`, `idioms`, `sentence-usage`, `faulty-sentence`, `factual`, `inference`, `vocabulary-in-context`, `main-idea`, `character-and-feelings`, `opinion`, `message-writing`, `wrong-character`.

### Conventions settled from the pilot papers

- Chinese papers: also render a 200-dpi copy of the pages for reading; boxes stay in 100-dpi pixels.
- Chinese passage crops: leave the section header and instruction line **out** of the crop (the instruction is already in `text`). A word bank printed with the passage stays inside the crop, with its words repeated in `alt`.
- 改正错别字: `value` is the corrected whole word when a word is underlined (single corrected character also in `accept`), and the single corrected character when one character is bracketed (whole word also in `accept`). Tags: `wrong-word` and `wrong-character`. Stems follow the pattern "Q6 画线的词语“++热情++”运用不当，正确的词语是：" and "Q7 “（饼）命”括号里的字写错了，正确的字是：".
- Word-bank `accept` includes the word alone and number-plus-word ("陪伴", "3 陪伴").
- A sub-instruction shared by several question numbers ("(Q11–Q12) 从短文中找出…") is repeated in each question's stem.
- A table row that is a whole question with several cells: one part per cell.
- Tick-and-justify questions: one `self` part; list the choices in the stem and add a bracketed line telling the child to write the choice, then the reasons.
- Open-ended opinion parts where the key gives no model answer: write a sample answer and start `value` with "（开放式题目，没有固定答案。）示范：" (English: "(Open-ended; answers vary.) Sample: ").
- The `group` field on a question is optional and names an entry in the paper's `groups`.
- 短文填空 with the four choices printed in brackets inside the passage: each blank is `mcq` with the four words as `options`.
- 完成对话: crop the word bank and the dialogue together as one image; `value` is the number, `accept` has the phrase. Stem: "Q26 的答案是：（填写数字 1 到 8）".
- Four-option questions are `mcq` even when the pupil writes the number in an answer booklet.
- Message or reply writing (Chinese Q33 type): transcribe the given opening into the stem; put the mark split (内容 / 语文) in the explanation.
- Two questions printed on one line with separate marks become parts `a` and `b`.
- A section instruction printed once for several standalone questions is repeated as the first line of each stem.
- `page` and crops come from the question booklet. Answer-booklet pages are only checked for mark splits.
- Pencil marks inside a passage crop are acceptable unless they give an answer away; if they do, mark the affected question `needs-review`.
- Extra Chinese tags: `sentence-completion`, `dialogue-completion`, `cause-and-effect`, `purpose-and-audience`.

English conventions (from `library/english/2026-prelim-acsj.json`):

- Typed answers are matched ignoring case, full stops, commas and quote marks, so `accept` needs no capitalised or no-full-stop variants.
- Stems for passage items: "Choose the word closest in meaning to ++finality++."; "Choose the most suitable word for blank (26). (Type its letter, A to Q.)"; "Write the correct word for (36) ++begin++."; "Fill in blank (46) with a suitable word."
- Synthesis: the given sentences, then the starter on its own line with a blank (`Neither ____________________.`), then a bracketed instruction.
- When a question's line range is narrower than a paragraph, add the first and last words of the range: `(lines 18–21, paragraph 4, from "As the weeks passed" to "smirking with pride")`.
- A group may mix an image text and a transcribed text; head them "++Text 1++" and "++Text 2++".
- Keep "Adapted from …" source lines as the last line of the group text.
- Unlabelled table rows become parts a, b, c with the row's word or statement as the prompt.
- Open cloze where your word differs from the key but is clearly right: the key's word is `value`, yours goes in `accept`, with a `review.note`.
- Highlighter, underlining or struck-out words added by a previous owner are ignored; transcribe the printed text and note anything inferred.
- Extra tags: `preposition-gerund` (synthesis), `word-meaning` (vocabulary-cloze), `inversion` (so/neither + auxiliary), `would-rather`.

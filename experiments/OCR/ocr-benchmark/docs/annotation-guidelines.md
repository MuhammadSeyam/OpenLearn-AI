# Ground-Truth Annotation Guidelines

> **Status: ACTIVE.** These conventions define what "correct" means for every
> transcription in `data/ground_truth/` and fix the normalization contract
> that the metrics module (`ocrbench.core`) will implement — changing a rule
> here retroactively affects every published score, so changes require a
> changelog entry (§9).
>
> Influences: OCR Benchmarking Handbook Phase 1/4 (Arabic diacritics policy,
> raw vs. normalized CER); common Arabic OCR evaluation practice (e.g.,
> KITAB-Bench normalization conventions — cite the exact version adopted when
> metrics are implemented).

## 1. GT structure — CURRENT OFFICIAL CONVENTION (flat layout)

For the Custom dataset, ground truth is **one flat plain-text file per
sample**, keyed by the canonical sample ID:

```
data/ground_truth/custom/<sample_id>.txt
```

- Exactly **one `.txt` file per sample**, UTF-8 encoded.
- `<sample_id>` is the canonical sample ID: the exact raw filename stem,
  case-sensitive (`Custom_English_scanned_002.txt`,
  `custom_custom_english_born_digital_001_p001.txt`). No renaming, no case
  folding, no prefixing.
- There is **no per-sample directory, no `page_NNN.txt` hierarchy, no
  `page_NNN.md`, no `tables/*.html`, no `meta.json`.**
- Raw ↔ GT ↔ metadata ↔ manifest identity must match exactly; duplicate,
  missing, orphan, or empty GT files are validation errors enforced by
  `scripts/audit_custom_manifest.py`.

### 1.1 Transcription conventions observed in the current corpus

The following conventions are documented from the actual 85 GT files and are
the working standard for future Custom annotations:

- Plain UTF-8 text in logical reading order.
- Paragraph breaks are expressed as blank lines (used throughout the corpus).
- Tables appear as plain text lines; where a table's grid matters, pipe-style
  rows are used (present in several table-category samples).
- Formulas are transcribed inline; LaTeX `$...$` notation appears where the
  source contains mathematical content.
- Markdown emphasis (`**bold**`) appears sparingly where it reflects the
  source document's own emphasis (e.g., an algorithm listing).
- Headers/footers/page numbers are not specially marked in the current corpus.

Do not invent conventions beyond these without updating this section.

## 2. Arabic diacritics (tashkeel) — the core decision

- **Primary transcription (`<sample_id>.txt`) preserves diacritics exactly as
  printed.** Do not add, remove, or "correct" them.
- Metrics will always report **raw CER (diacritics as-is)** and **normalized
  CER (diacritics stripped)** side by side — the gap between them is itself a
  reported result (handbook Phase 1). Never report only one.
- Rationale: stripping at transcription time destroys the ability to measure
  how engines handle diacritics — an explicit OpenLearn requirement.

## 3. Arabic character normalization (metrics-time, not transcription-time)

Normalization is applied by the metrics code to **both** prediction and ground
truth, never baked into transcriptions:

| Rule | Rationale |
|---|---|
| Strip diacritics (`U+064B–U+0652`, `U+0670`) | Optional in most texts; engines differ |
| Remove tatweel (`ـ`, `U+0640`) | Purely visual elongation |
| Unify alef variants: `أ` `إ` `آ` → `ا` | Common engine/GT convention mismatch |
| `ى` → `ي` (final alef maqsura) | Frequent confusion; standard in Arabic IR normalization |
| `ة` → `ه` **NOT applied** | Changes meaning (قطة/قطه); rejected |
| Unicode RLE/RLM marks stripped | Layout control, not content |
| NFC normalization | Deterministic byte stability |

Every rule must have this table's rationale; adding a rule requires updating
this table + tests. Rules still under debate (team review): `ٱ` (alef wasla),
`ؤ`/`ئ` handling, digit forms (Arabic-Indic ٠-٩ vs 0-9) — decide before
metrics implementation lands.

## 4. Punctuation & symbols

- Transcribe punctuation as printed, Latin or Arabic forms as they appear.
- Normalize at metrics time: ASCII/Arabic comma and question mark equivalence
  (`،`↔`,`, `؟`↔`?`) — documented in the same table as §3 when adopted.

## 5. English spans inside Arabic text (mixed documents)

- Transcribe exactly as printed, in logical order (RTL base direction,
  embedded LTR runs). **Never visually reorder** — logical order is what
  Unicode-correct engines should emit.
- Mixed-language samples are first-class benchmark samples; CER is
  additionally reported per-script segment when metrics support it.

## 6. Formulas, figures, tables

- **Formulas:** transcribed inline in the `.txt`; LaTeX `$...$` where the
  source contains math (this matches the existing verified GT). A
  formula-specific metric is out of scope for the pilot — formulas are
  tagged, not scored, until TEDS-style structure metrics land.
- **Figures/diagrams:** text *inside* a figure region that belongs to the
  page's content flow may be transcribed where the annotator judged it part
  of the page text; engines that hallucinate text into figure regions get
  penalized by CER, which is the point.
- **Tables:** transcribed as plain text / pipe-style rows inside the single
  `.txt` (matches the existing verified GT).

## 7. Reading order

- Transcribe in the document's **logical reading order**: for Arabic pages,
  right column before left; for two-column academic layouts, full column then
  next. The current corpus does not use explicit header/footer markers;
  headers/footers/page numbers are handled as ordinary text unless a future
  revision introduces markers.

## 8. Quality control

- All 85 current Custom GT files have been manually reviewed and their
  textual content accepted as correct (`ground_truth.status: verified`).
  "Verified" means **content review by a human**; structural checks (file
  exists, non-empty, valid UTF-8, exact raw↔GT identity) remain useful
  validation but are enforced mechanically and are not the definition of
  verified.
- Illegible characters: if encountered in future annotation, use `□`
  (U+25A1) with a note recorded outside the flat file (changelog or review
  log); a page with > 5% illegible characters should be flagged in metadata
  (`noisy: true`), not silently transcribed.

## 9. Versioning

- Corrections to any GT `.txt` require a changelog entry (date, sample_id,
  what changed, why) in this file's change log (below).
- Convention changes bump the version in this file's header and invalidate
  affected published metrics (re-run required).

## 10. Anti-circularity rule (hard constraint)

Ground truth is **never** derived from the output of an engine under
evaluation. Annotators work from the source page/image only.

---

## Change log

- v0.2 (Phase 3): Flat per-sample `<sample_id>.txt` layout adopted as the
  CURRENT official GT convention for the Custom dataset, matching the
  verified on-disk state. Per-directory `page_NNN.txt/.md`, `tables/*.html`,
  and `meta.json` structure superseded (see §11).
- v0.1: Initial draft (per-page directory layout proposal).

---

## 11. HISTORICAL — Superseded rich-layout proposal

> **Status: SUPERSEDED — NOT currently implemented — possible future
> extension.** The structure below was the original draft proposal. It does
> NOT describe the current dataset and must not be assumed by tooling. It is
> retained because it documents capability extensions (Markdown structural
> scoring, TEDS table scoring, provenance metadata) that may be adopted
> later without changing the flat `.txt` identity contract.

One transcription **per page**, in two forms:

- `page_NNN.txt` — plain text, reading order, one paragraph per line.
- `page_NNN.md` — Markdown reflecting document structure (headings, lists,
  tables).
- `tables/page_NNN_tK.html` — additionally, for every table on the page, an
  HTML table (enables TEDS scoring later).
- `meta.json` — annotator, date, review status, conventions version, and any
  notes on ambiguous regions.

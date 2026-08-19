# Candidate models:

## Tier 1 — Specialized document parsers

- PaddleOCR-VL
- MinerU2.5-Pro
- Baseer

## Tier 2 — General VLM

- Qwen2.5-VL
- Qwen3-VL

## Native parser

- Docling



# Pipeline
                    Document
                       │
                       ▼
                 Document Inspector
                       │
                       ▼
                  Native Parser
                    (Docling)
                       │
                 Quality Gate
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
       Accept       Arabic/RTL   Complex Layout
          │            │            │
          │            ▼            ▼
          │          Baseer      MinerU/Paddle
          │
          └────────────┬────────────┘
                       ▼
              Unified Document Schema
                       │
              ┌────────┴────────┐
              ▼                 ▼
           Markdown           JSON
              │                 │
        ┌─────┴─────┐           │
        ▼           ▼           ▼
     Vector       Graph      Citations
       RAG         RAG


# Paper

"We built a GraphRAG educational system."

to

"An Arabic-first multimodal document ingestion and GraphRAG pipeline for educational materials."












1. **OCR benchmark** → يقيس جودة استخراج المحتوى من الـ document/page.
2. **End-to-end pipeline benchmark** → يقيس الـ pipeline كاملة من الملف لحد الـ chunks → embeddings/tokens → vector DB / knowledge graph.

ما نخلطهمش في benchmark واحد، وإلا لما حاجة تفشل مش هنعرف مين السبب.

---

# 1. أول حاجة نعملها الآن: Freeze للـ dataset design

الـ folders اللي عندك:

```text
1. English born-digital
2. Arabic born-digital
3. English scanned
4. Arabic scanned
5. Arabic + English mixed
6. Multi-column
7. Tables
8. Formulas
9. Figures-diagrams
10. Slides
11. Dense academic page
12. Noisy-low-quality scan
```

دي **ممتازة كـ document categories**.

لكن قبل ما نضيف MISRAG أو نعمل ground truth، لازم نحولها إلى **dataset specification**.

يعني كل sample يبقى له:

```text
sample_id
source_file
page/image
language
document_type
input_type
difficulty
has_tables
has_formulas
has_figures
has_columns
ground_truth
```

مثلاً:

```json
{
  "sample_id": "custom_002_arabic_scanned_001",
  "source": "custom",
  "file": "sample_001.png",
  "language": ["ar"],
  "document_type": "scanned",
  "category": "arabic_scanned",
  "difficulty": "medium",
  "has_table": false,
  "has_formula": false,
  "has_figure": false
}
```

**دي أهم خطوة قبل annotation.**

---

# 2. ما تعملش Ground Truth للـ OCR كـ text فقط

دي نقطة مهمة جدًا.

لو هدفك الحقيقي OpenLearn AI، فأنت مش عايز تعرف فقط:

> هل OCR طلع الكلام صح؟

أنت عايز تعرف:

> هل الـ document تحول إلى representation تقدر بقية الـ pipeline تستخدمها؟

لذلك Ground Truth بتاعنا يكون layered.

مثلاً:

```text
Layer 1 — Document
    ↓
Layer 2 — OCR
    ↓
Layer 3 — Structure
    ↓
Layer 4 — Chunks
    ↓
Layer 5 — Retrieval
    ↓
Layer 6 — Knowledge Graph
```

---

# 3. Layer 1 — Document Ground Truth

الـ source نفسه.

مثلاً:

```text
sample_001
├── source.pdf
├── page_001.png
└── metadata.json
```

Metadata:

```json
{
  "id": "custom_001",
  "language": ["ar"],
  "category": "arabic_scanned",
  "source_type": "scanned",
  "page_count": 1
}
```

---

# 4. Layer 2 — OCR Ground Truth

هنا نكتب النص الصحيح.

مثلاً:

```text
ground_truth/
└── custom_001/
    ├── text.txt
    └── annotation.json
```

والـ `text.txt` يحتوي النص الطبيعي.

لكن الـ annotation JSON ممكن يكون:

```json
{
  "sample_id": "custom_001",
  "blocks": [
    {
      "type": "heading",
      "text": "مقدمة في هياكل البيانات"
    },
    {
      "type": "paragraph",
      "text": "..."
    }
  ]
}
```

وده أحسن بكتير من plain OCR.

---

# 5. Layer 3 — Layout / Structure Ground Truth

وده مهم جدًا لأن عندك:

* tables
* formulas
* figures
* multi-column
* slides

مثلاً صفحة فيها:

```text
┌─────────────────────────────┐
│        Heading              │
├──────────────┬──────────────┤
│ paragraph    │ paragraph    │
│ paragraph    │ paragraph    │
├──────────────┴──────────────┤
│          TABLE              │
└─────────────────────────────┘
```

لو OCR طلع كل الكلام صح لكن رتب الـ columns غلط:

**OCR text accuracy = ممتازة**

لكن:

**document understanding = سيئة.**

وده بالضبط ليه benchmark بتاعك لازم يبقى أوسع من CER/WER.

---

# 6. استخدم MISRAG كـ external benchmark

أنا متفق مع قرارك هنا.

خليه يمثل:

```text
PUBLIC DATASET
      │
      └── MISRAG
```

والـ dataset بتاعك يمثل:

```text
CUSTOM DATASET
      │
      ├── Arabic
      ├── English
      ├── Mixed
      ├── Tables
      ├── Formula
      ├── Figures
      ├── Slides
      ├── Multi-column
      └── Noisy scans
```

وبالتالي عندك:

```text
OCR Benchmark Dataset
│
├── public/
│   └── MISRAG
│
└── custom/
    ├── Arabic
    ├── English
    ├── Mixed
    ├── Tables
    ├── Formulas
    ├── Figures
    ├── Slides
    ├── Multi-column
    ├── Dense
    └── Noisy
```

وده أقوى علميًا من إنك تعتمد على dataset واحد.

---

# 7. لكن ما تعملش dataset ضخم دلوقتي

دي أهم نصيحة عندي لك.

**Don't spend another 3 days building the perfect dataset before running anything.**

أنت عايز تبدأ testing.

فنعمل **MVP benchmark**.

مثلاً:

| Category             | Samples |
| -------------------- | ------: |
| English born-digital |       5 |
| Arabic born-digital  |       5 |
| English scanned      |       5 |
| Arabic scanned       |       5 |
| Arabic + English     |       5 |
| Multi-column         |       5 |
| Tables               |       5 |
| Formulas             |       5 |
| Figures              |       5 |
| Slides               |       5 |
| Dense academic       |       5 |
| Noisy scan           |       5 |
| **Custom total**     |  **60** |

وبعدين MISRAG كـ external validation.

مش لازم تبدأ بـ 500 صفحة.

**60 carefully selected samples > 1,000 random pages** في أول benchmark.

---

# 8. بعد كده نشغل OCR engines

مثلاً:

```text
                    ┌── PaddleOCR
                    │
Input ──► OCR ──────┼── Surya
                    │
                    ├── Docling OCR
                    │
                    └── ...
```

وكل engine ينتج standardized output:

```json
{
  "sample_id": "...",
  "engine": "paddleocr",
  "text": "...",
  "blocks": [],
  "processing_time_ms": 1234
}
```

**ممنوع كل OCR adapter يعمل output مختلف.**

دي وظيفة:

```text
ocrbench/adapters/
```

---

# 9. Metrics

مش بس accuracy.

## Text

نحسب:

### CER

Character Error Rate

مهم جدًا للعربي.

### WER

Word Error Rate

لكن خليه secondary لأن Arabic tokenization tricky.

### normalized CER

نعمل normalization controlled للعربي قبل المقارنة.

مثلاً التعامل مع:

```text
أ إ آ
```

و:

```text
ـ
```

والـ whitespace وغيرها.

لكن **لا تعمل normalization aggressive** يخلي الأخطاء تختفي.

---

# 10. Layout metrics

مثلاً:

```text
heading preservation
paragraph ordering
reading order
table detection
formula detection
figure detection
column ordering
```

ونقدر نعمل score:

```text
Layout Score
```

مثلاً:

```text
Reading Order Accuracy
Block Detection F1
Table Detection F1
Formula Detection F1
```

حسب الحاجة.

---

# 11. Performance metrics

كل sample نسجل:

```text
processing_time_ms
CPU memory
GPU memory
model loading time
throughput
```

وبالتالي في النهاية نقدر نقول:

> PaddleOCR حصل على CER كذا، لكن كان أسرع بكذا.

وده أهم من مجرد:

> Model A أفضل.

---

# 12. وبعد OCR نعمل الـ End-to-End benchmark

هنا ندخل في اللي أنت قلته:

> من file لحد tokens/embeddings → vector DB → knowledge graph.

وده **Benchmark ثاني**.

أقترح architecture كده:

```text
                 END-TO-END BENCHMARK
                         │
                         ▼
                      FILE
                         │
                         ▼
                  Document Parser
                         │
                         ▼
                       OCR
                         │
                         ▼
                 Structured Document
                         │
                         ▼
                    Chunking
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
          Embeddings              Tokens
              │                     │
              ▼                     ▼
         Vector Store          LLM / Context
              │
              ▼
          Retrieval
              │
              ▼
        Knowledge Graph
```

وكل stage يكون له metrics.

---

# 13. Pipeline benchmark metrics

مثلاً:

### File → OCR

```text
CER
WER
layout accuracy
latency
```

### OCR → chunks

```text
chunk boundary quality
semantic completeness
chunk size distribution
```

### chunks → embeddings

```text
embedding latency
embedding dimension
batch throughput
```

### embeddings → vector DB

```text
insert latency
indexing latency
storage size
retrieval latency
Recall@K
Precision@K
MRR
```

### Knowledge Graph

```text
entity extraction precision
entity recall
relation precision
relation recall
graph consistency
```

---

# 14. أهم حاجة: Traceability

دي هتفرق جدًا في المشروع.

كل حاجة لازم تكون مرتبطة بـ:

```text
document_id
page_id
block_id
chunk_id
embedding_id
entity_id
```

مثلاً:

```text
DOC-001
 │
 ├── PAGE-001
 │    │
 │    ├── BLOCK-001
 │    ├── BLOCK-002
 │    │
 │    ├── CHUNK-001
 │    │      └── EMBEDDING-001
 │    │
 │    └── CHUNK-002
 │           └── EMBEDDING-002
 │
 └── PAGE-002
```

ساعتها لو retrieval رجع إجابة غلط، تقدر تعمل:

```text
Answer
 ↓
Retrieved chunk
 ↓
Embedding
 ↓
Chunk
 ↓
OCR text
 ↓
Page
 ↓
Original PDF
```

وده **بالضبط** اللي محتاجه OpenLearn AI.

---

# 15. طيب نعمل إيه الآن تحديدًا؟

مش بكرة. **دلوقتي.**

أنا أقترح الـ next steps دي بالترتيب:

### Step 1 — Freeze dataset taxonomy

الـ 12 categories اللي عملتهم.

**ما تغيرهمش دلوقتي.**

---

### Step 2 — Define dataset manifest

خلينا نخلي:

```text
data/raw/custom/manifest.json
```

هو مصدر الحقيقة للـ dataset.

كل sample له metadata.

---

### Step 3 — Add MISRAG

لكن **ما نحطش dataset خارجي ضخم جوه Git**.

نعمل:

```text
data/raw/public/misrag/
```

مع:

```text
README.md
manifest.json
```

والـ README يشرح source/download/provenance/license.

ولو dataset حجمه كبير، نخليه download script أو documented external dependency.

---

### Step 4 — Create annotation schema

مثلاً:

```text
data/ground_truth/
├── public/
│   └── misrag/
└── custom/
    ├── ...
```

ونحدد schema واحد.

---

### Step 5 — Annotate 5 samples/category

مش 100.

ابدأ بـ:

**60 custom samples.**

---

### Step 6 — Implement benchmark core

داخل:

```text
src/ocrbench/
```

نعمل:

```text
core/
├── dataset.py
├── manifest.py
├── normalization.py
├── metrics.py
└── evaluation.py

adapters/
├── paddleocr.py
├── ...
```

---

### Step 7 — Run first benchmark

أول run يكون:

```text
MISRAG
+
Custom 60 samples
```

على:

```text
PaddleOCR
```

فقط.

مش لازم تعمل كل models مرة واحدة.

---

# 16. وبعد ما ده يشتغل...

ساعتها نبدأ:

```text
PaddleOCR
      vs
Surya
      vs
Docling
      vs
...
```

وبعدها:

```text
OCR
 ↓
Chunking
 ↓
Embedding
 ↓
Vector DB
 ↓
Retrieval
```

ثم:

```text
Knowledge Graph
```

---

## والأهم: ما نبدأش بالـ Vector DB دلوقتي

أنت قلت:

> عاوز أبدأ testing ونخلص.

فلو بدأنا نعمل:

```text
OCR + chunking + embeddings + vector DB + KG
```

من أول يوم، هتدخل في خمس مشاكل في نفس الوقت ومش هتعرف المشكلة فين.

اعملها **layer by layer**:

```text
PHASE A
Dataset
   ↓
OCR benchmark
   ↓
DONE ✓

PHASE B
OCR
   ↓
Chunking
   ↓
Chunk benchmark
   ↓
DONE ✓

PHASE C
Chunks
   ↓
Embeddings
   ↓
Retrieval
   ↓
DONE ✓

PHASE D
Entities
   ↓
Relations
   ↓
Knowledge Graph
   ↓
DONE ✓

PHASE E
Everything together
   ↓
End-to-End benchmark
   ↓
DONE ✓
```

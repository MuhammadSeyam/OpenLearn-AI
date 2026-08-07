# OpenLearn AI — Free Compute, Credits & Funding Playbook
**Prepared:** August 2026 · **Team:** OpenLearn AI (Egypt, university graduation project → open-source → potential startup)

> ⚠️ **How to use this document.** Startup/cloud credit programs change tiers, amounts, and eligibility rules frequently (several changed materially in the last 6 months alone — e.g. GitHub's DigitalOcean offer excluded GPU Droplets starting June 2026, GitHub Copilot Student sign-ups paused in April 2026). Every entry below reflects the most current information found during this research pass, but **re-verify eligibility and amounts on the official page immediately before applying** — links are provided for that reason. Treat dollar figures as "up to" ceilings, not guarantees.

---

## 1. Executive Summary — Top 20 Opportunities Ranked by Expected Value for OpenLearn AI

Ranking weighs: (a) how easy it is for a *pre-incorporation graduation project* to qualify today, (b) $ value, (c) direct relevance to your OCR/LLM/RAG/vector-DB/agents stack, (d) Egypt eligibility.

| # | Opportunity | Why it's high-value for you now | Est. value |
|---|---|---|---|
| 1 | **GitHub Student Developer Pack** | Zero barrier (just a .edu email + student ID), instantly gives $200 DigitalOcean, $100 Azure, JetBrains, domains, MongoDB Atlas. Best *first move*, no company/incorporation needed. | ~$300–500/student |
| 2 | **Microsoft for Startups Founders Hub** | Self-serve tier needs **no incorporation, no investor, no revenue** — just a Microsoft account and a product description. Gives Azure credits (starts ~$1,000–5,000) + Azure OpenAI access + GitHub Enterprise + M365. | $1,000–5,000 (scales later) |
| 3 | **Google Cloud for Students / Google for Startups (Cloud Program)** | Free Vertex AI / Gemini credits track for students and early startups; strong Gemini + embeddings + Cloud Vision OCR fit. | $300–2,000+ |
| 4 | **Hugging Face (PRO + Community GPU Grants + Inference Providers credits)** | Central to your stack: model hosting, Spaces, ZeroGPU grants for "cool side projects," Inference Providers routing to Groq/Together/Fireworks. Explicitly supports open-source & academic projects. | Ongoing, variable |
| 5 | **NVIDIA Inception** | Free DLI training + potential AWS Activate ($100k) / Nebius ($150k) access **once you incorporate** — worth applying the moment you register the project as an entity (even a simple one). No fee, no deadline, apply anytime. | Access to $100K–$250K partner credits |
| 6 | **AWS Activate – Founders track** | $1,000 + $350 support credits, no VC/accelerator needed, bootstrapped-friendly. Amazon Bedrock (Claude, Titan) credits count. | $1,000–1,350 |
| 7 | **Groq API (free tier)** | Extremely fast, generous free-tier inference for open models (Llama, etc.) — ideal for your adaptive-learning agent calls during dev/demo. | Free tier, renewable |
| 8 | **OpenRouter free-tier & credit grants** | Aggregates many free/cheap models (including free Gemini/Llama/DeepSeek endpoints) behind one API — good fallback layer. | Free tier |
| 9 | **Google AI Studio / Gemini API free tier** | Free Gemini 2.x usage with generous rate limits — strong for RAG, embeddings, and long-context OCR-adjacent tasks. | Free (rate-limited) |
| 10 | **Qdrant Cloud free tier** | 1 free managed cluster (1GB) — enough for an MVP vector DB for RAG. Open-source core, self-hostable for $0 if you outgrow it. | Free forever tier |
| 11 | **DigitalOcean via GitHub Pack / Hatch (Hatch program)** | $200 credit (GitHub) is cash-flow-friendly for hosting your backend/API/DB; DO's own "Hatch" startup program is a further option. | $200+ |
| 12 | **DEPI — Digital Egypt Pioneers Initiative (MCIT)** | Fully-funded, Egypt-specific, AI & Data Science track, includes mentorship + potential compute/industry partnerships. Not compute per se, but funds your team's skills + can open doors to other MCIT/ITIDA resources. | Free training (in-kind) |
| 13 | **ITIDA (Information Technology Industry Development Agency, Egypt)** | Runs incubation, funding competitions (e.g. ITAC — IT Access to Knowledge/Entrepreneurship programs), grants for tech graduation projects with commercialization potential. | Varies (grants) |
| 14 | **Kaggle (free GPU/TPU notebooks)** | 30 hrs/week free GPU (P100/T4) + TPU quota — good for model fine-tuning/experiments without any application. | Free, no application |
| 15 | **Google Colab (free tier)** | Free T4 GPU sessions — useful for prototyping OCR/embedding pipelines before you need dedicated GPU credits. | Free |
| 16 | **Mistral AI "La Plateforme" free/startup tier** | European open-weight LLM provider with student/startup credit programs and strong open-source ethos — good redundancy to OpenAI/Anthropic. | Free tier + startup credits |
| 17 | **Mathpix API (free tier)** | Purpose-built OCR for math/handwritten notes and STEM documents — directly matches your "handwritten notes/books" ingestion need. Free monthly request quota. | Free tier (~1000 req/mo typical) |
| 18 | **Cloudflare Workers AI / R2 (free tier + OSS credits)** | Free R2 storage (no egress fees) for storing embeddings/documents, plus Workers AI free inference quota — very startup/OSS-friendly. | Free tier |
| 19 | **Together AI (startup/research credits)** | Competitive open-model hosting + fine-tuning; runs credit programs for startups and researchers building on open-source LLMs. | $ varies (apply) |
| 20 | **Microsoft Learn Student Ambassadors / Azure for Students (separate from Founders Hub)** | $100 Azure credit with **no credit card required**, purely on .edu verification — stackable alongside Founders Hub for the same team. | $100/student |

**Bottom line:** items #1–#3, #7–#11, #14–#15 and #17–#18 can all be claimed **this week with zero incorporation, zero cost, and zero waiting**. Items #5, #6, #12, #13, #16, #19 pay off once you register an entity (even informally) and can show a live product/GitHub repo — worth doing in parallel once your MVP has a public URL.

---

## 2. Comparison Table

| Program | Free GPU | Cloud Credits | Storage | CPUs | APIs / LLM | Egypt OK? | Grad-project OK? | Difficulty | Est. Value (USD) |
|---|---|---|---|---|---|---|---|---|---|
| GitHub Student Pack | No (GPU excluded from DO credit since Jun 2026) | $200 DO + $100 Azure | Included in DO/Azure | Included | Copilot (paused for new sign-ups mid-2026) | Yes | Yes | Easy | ~$300–500 |
| Microsoft Founders Hub | Via Azure ML/OpenAI compute | $1,000–$150,000 (tiered) | Included | Included | Azure OpenAI (GPT-class) | Yes | Yes (self-serve tier) | Easy → Medium (higher tiers) | $1,000–150,000 |
| Google for Startups Cloud Program | Via Vertex AI compute | Up to $2,000 (student/early) – $100K+ (Cloud Program for Startups, funded) | Included | Included | Gemini API, Vertex AI | Yes | Often yes | Easy–Medium | $350–100,000+ |
| AWS Activate (Founders) | Via SageMaker/EC2 | $1,000 + $350 support | Included | Included | Bedrock (Claude, Titan, Llama) | Yes | Yes | Easy | ~$1,350 |
| NVIDIA Inception | Preferred pricing only (not free GPU directly) | Access to $100K AWS + $150K Nebius (via partners) | — | — | NIM microservices, DLI training | Yes | Needs incorporation | Medium | Access to $100K–250K |
| Hugging Face (PRO/Grants) | ZeroGPU / community grants (case-by-case) | HF PRO perk (~$100+ value) | 1TB private/10TB public (PRO) | — | Inference Providers routing | Yes | Yes | Easy–Medium | Variable |
| Groq API | N/A (inference API, not raw GPU) | Free tier (rate-limited) | — | — | Fast open-model inference | Yes | Yes | Easy | Free, ongoing |
| Together AI | Possible via startup program | Startup/research credits (apply) | — | — | Open-model hosting + fine-tuning | Yes | Yes | Medium | Varies |
| Qdrant Cloud | N/A | Free 1GB cluster forever | Included | — | Vector search API | Yes | Yes | Easy | Free tier |
| Kaggle | Yes — 30h/week T4/P100 + TPU | N/A | 20GB datasets | Yes | — | Yes | Yes | Easy (no application) | Free |
| Google Colab | Yes — free T4 (session-limited) | N/A | Google Drive-linked | Yes | — | Yes | Yes | Easy | Free |
| DEPI (Egypt/MCIT) | No | N/A (training program, not compute) | — | — | — | Egypt-only, ideal fit | Yes | Easy–Medium (selective) | In-kind training |
| ITIDA programs (Egypt) | Sometimes (via partner clouds) | Grant funding, varies by program | — | — | — | Egypt-only | Yes (esp. commercializable grad projects) | Medium | Varies (grants can be $1,000s+) |
| Mathpix | N/A | N/A | — | — | Free OCR tier (~1,000 req/mo) | Yes | Yes | Easy | Free tier |
| Cloudflare (Workers AI/R2) | Limited free inference | R2 free 10GB/mo storage, no egress fees | 10GB free | — | Workers AI free daily quota | Yes | Yes | Easy | Free tier |

---

## 3. Priority Roadmap — Apply in This Order

**Phase 0 (This week — zero cost, zero waiting, do all in parallel):**
1. **GitHub Student Developer Pack** for every team member — unlocks DO + Azure + JetBrains + domains immediately.
2. **Google Colab + Kaggle** — start prototyping OCR/embedding pipelines on free GPUs today, no application needed.
3. **Groq API + Google AI Studio (Gemini) + OpenRouter free tier** — wire up your first LLM calls at $0.
4. **Qdrant Cloud free cluster** — stand up your RAG vector store.
5. **Mathpix free tier** — test handwritten-notes/math OCR ingestion.
6. **Hugging Face account + apply for a community GPU grant** if you plan to host a public demo Space or fine-tune an open model — do this early since grant review takes time.

*Why first:* none of these require a registered company, a credit card, or a waiting period tied to funding stage. They immediately give you a working, deployed MVP — which every later-stage program (Azure Founders Hub tiers, NVIDIA Inception, ITIDA grants) will ask to see as proof of traction.

**Phase 1 (Once you have a public repo + live demo, still pre-incorporation, weeks 2–4):**
7. **Microsoft for Startups Founders Hub** (self-serve entry tier) — apply with your team as "founders," no incorporation required for entry tier.
8. **Azure for Students** ($100, separate benefit, stack alongside GitHub Pack/Founders Hub on the same or a second Microsoft account).
9. **AWS Activate – Founders track** — apply directly, bootstrapped/self-funded track needs no VC.
10. **Cloudflare for Startups / free tier setup** for R2 storage + Workers AI.

*Why now:* these programs specifically ask "what are you building" and reward a live URL and GitHub activity — you'll qualify faster with Phase 0 already shipped.

**Phase 2 (After graduation / once you register as a legal entity or NGO, or join an incubator):**
11. **NVIDIA Inception** — apply the moment you have a simple incorporation (many countries allow a low-cost startup registration; Egypt's ITIDA/GAFI "startup license" or a simple sole-proprietorship can qualify). Unlocks the $100K AWS / $150K Nebius partner tracks.
12. **ITIDA programs** (grants, incubation, ITAC) — Egypt-specific, values commercializable graduation projects.
13. **DEPI / MCIT tracks** — for continued team upskilling and access to MCIT's broader innovation ecosystem and industry partners.
14. **Google for Startups Cloud Program (funded track)** and **Together AI / Mistral startup credits** — apply once you can show usage/traction metrics.
15. **Competitions** (Microsoft Imagine Cup, Google Solution Challenge, NVIDIA competitions, Kaggle) — enter as soon as your MVP is demo-ready; these often bundle mentorship + credits + cash on top of what you already have.

**Why this order maximizes your resources:** Phase 0 gets you to a working product at $0 without waiting on anyone's approval. Phase 1 converts that working product into cloud credits from programs that explicitly reward "already building." Phase 2 opens the largest-dollar programs (NVIDIA Inception's $100K–250K partner credits, ITIDA grants) — but these disproportionately reward incorporation and traction, so sequencing them last (once you have both) dramatically increases your acceptance odds and negotiating position.

---

## 4. Hidden Gems (often overlooked by students)

- **Hugging Face Community GPU Grants** — explicitly aimed at "cool side projects," not just published research; a graduation project with a public demo Space is a great fit, but few students know to ask.
- **Cloudflare R2** — free 10GB egress-free object storage is a quietly excellent place to store embeddings/document chunks without worrying about AWS S3 egress bills.
- **Qdrant Cloud's permanent free tier** (not a trial) — most students default to Pinecone's trial (which expires) and miss that Qdrant's free cluster doesn't.
- **Mathpix's free tier** is one of the only OCR APIs purpose-built for math notation and handwritten STEM content — directly relevant to "converts handwritten notes into personalized learning" and usually missed in favor of generic OCR (Google Vision/Textract), which handles equations poorly.
- **Kaggle's free TPU quota** (in addition to GPU) — underused for embedding-generation batch jobs.
- **DigitalOcean's own "Hatch" startup program** (separate from the GitHub Pack credit) — students often stop at the $200 GitHub credit and never apply to Hatch directly for a larger, renewable allocation.
- **Snorkel AI's Open Benchmarks Grants** (2026, with Hugging Face/Together AI/PyTorch backing) — funds open-source datasets/evaluation frameworks for agentic AI with compute + engineering support; a strong fit if you plan to publish an evaluation benchmark for adaptive learning/student modeling as part of your open-source release.
- **University-level HPC access** — many Egyptian universities and the Egyptian Supercomputing Center / national HPC initiatives offer compute to graduation projects if a supervising faculty member sponsors the request — ask your department directly; this is rarely advertised centrally.
- **"Stacking" is explicitly allowed** across nearly all these programs (NVIDIA Inception + Azure Founders Hub + AWS Activate + Google for Startups can all be held simultaneously) — most students apply to only one cloud and leave the others unclaimed.

---

## 5. Egyptian-Specific Opportunities

| Program | Organization | Focus | Fit for OpenLearn AI |
|---|---|---|---|
| **DEPI (Digital Egypt Pioneers Initiative)** | MCIT | Fully-funded AI/Data Science, Software Dev, freelancing tracks | Great for team upskilling; AI & Data Science track directly overlaps your tech stack; apply at depi.gov.eg |
| **DEBI (Digital Egypt Builders Initiative)** | MCIT | Builder/incubation-style track under the same MCIT "Digital Egypt Generations" umbrella | Check current round for startup/product-building focus |
| **ITIDA** | Egypt ITIDA | Incubation, IT grants, entrepreneurship & funding competitions (historically incl. ITAC) | Apply once you have a working prototype; strong fit for a graduation project with commercialization potential |
| **National Telecommunication Institute (NTI)** | Egypt | Training + some research/compute-adjacent programs | Worth checking current course/grant catalog |
| University HPC / Ministry of Higher Education research computing | Various Egyptian universities | Faculty-sponsored compute access | Ask your supervising professor to request allocation on your behalf — often free but not centrally advertised |

*(DEPI/MCIT program names, tracks, and application windows change by "round" — confirm the currently open round and its specific track list at **mcit.gov.eg** and **depi.gov.eg** before assuming AI & Data Science is open right now.)*

---

## 6. API Credits & AI Model Sponsorship — Provider Snapshot

| Provider | Free tier | Student/startup/OSS credit | Egypt eligible? |
|---|---|---|---|
| **OpenAI** | No persistent free tier for API (pay-as-you-go); periodic startup credit programs exist | OpenAI has run startup-credit programs via partners (apply, availability varies) | Generally yes, check regional API access |
| **Anthropic (Claude)** | No standing free API tier; Claude.ai has a free chat tier | Anthropic has offered startup/build-partner credits case-by-case | Yes for API access (check console.anthropic.com for current offers) |
| **Google Gemini (AI Studio)** | Generous free tier with rate limits | Google for Startups Cloud Program credits also cover Vertex AI/Gemini | Yes |
| **Groq** | Free-tier API for open models, fast inference | — | Yes |
| **Together AI** | Small free/trial credit on signup | Startup & research credit programs (apply) | Yes |
| **Mistral AI (La Plateforme)** | Free tier for experimentation | Startup program credits | Yes |
| **Hugging Face Inference Providers** | Small monthly credit on free/PRO plans, routes to Groq/Together/Fireworks/etc. | PRO discount via startup-perk marketplaces; community GPU grants for OSS projects | Yes |
| **OpenRouter** | Aggregates several genuinely free models (e.g., some Llama/Gemini/DeepSeek variants) behind one key | — | Yes |
| **DeepSeek** | Low-cost API, occasional free promo credit | — | Check regional availability |
| **Mathpix (OCR)** | Free monthly request quota | — | Yes |
| **Google Cloud Vision / Azure AI Vision / Amazon Textract** | All three offer free monthly OCR request quotas | Covered further by Google/Azure/AWS startup credit programs above | Yes |
| **Qdrant Cloud / Weaviate Cloud** | Both offer a permanent small free managed cluster | Startup programs sometimes available on request | Yes |
| **Pinecone** | Free "Starter" tier (limited pods/storage) | — | Yes |
| **Voyage AI / Jina AI (embeddings)** | Free tier / trial credits for embeddings API | — | Yes |
| **ElevenLabs / Deepgram / AssemblyAI (speech)** | All offer limited free monthly minutes | Occasional startup/hackathon credit promos | Yes |

**Practical note:** exact free-tier limits (requests/month, tokens, rate limits) change often enough that we recommend checking each provider's pricing page at signup time rather than relying on a fixed number here — several of the above changed their free-tier terms within the past year.

---

## 7. Estimated Monthly API/Compute Costs for OpenLearn AI MVP

These are **planning estimates**, not quotes — actual cost depends heavily on document lengths, model choice, and caching strategy.

| Usage level | Description | Estimated monthly cost (full pay-as-you-go) | With free tiers + credits stacked |
|---|---|---|---|
| **Light** (demo/dev, ~50 active users, a few hundred documents processed/month) | OCR + embeddings + occasional LLM tutoring calls | ~$30–$120 | **$0** — fully covered by Colab/Kaggle GPU, Gemini/Groq free tiers, Mathpix free tier, Qdrant free cluster |
| **Medium** (pilot with one class/cohort, ~500 users, few thousand documents/month, daily adaptive-learning sessions) | Higher OCR volume, more embedding calls, sustained LLM chat/agent usage | ~$300–$900 | **$0–$50** — draw down Azure/AWS/Google startup credits + HF Inference Providers credits; use open-weight models via Groq/Together for high-volume calls, reserve GPT/Claude-class models for high-value tutoring turns only |
| **Heavy** (public launch, several thousand users, continuous ingestion of PDFs/slides/handwritten notes, knowledge-graph updates, multi-agent tutoring) | Full production RAG + agents + student modeling at scale | ~$2,000–$8,000+ | **~$200–$800** once cloud/startup credits ($5K–$150K tiers) are applied — credits should fully absorb this range for 6–18 months before you need paid infrastructure |

### Recommended $0-cost-leaning stack

- **Compute:** Google Colab/Kaggle (dev) → Azure/AWS credits from Founders Hub / Activate (prod) once you have them.
- **LLM calls:** OpenRouter/Groq/Gemini free tiers for high-volume, low-stakes calls (quizzes, summaries); reserve Claude/GPT-class models (via Azure OpenAI credits or Anthropic console credits) for the highest-value personalized tutoring interactions.
- **OCR:** Mathpix free tier for math/handwritten content; Google Cloud Vision or Azure AI Vision free monthly quota for general documents.
- **Embeddings/Vector DB:** Voyage AI or Jina AI free tier for embeddings + Qdrant Cloud free cluster (or self-hosted Qdrant on your DigitalOcean/Azure credits) for storage.
- **Storage:** Cloudflare R2 free tier (egress-free) for raw documents and processed assets.
- **Hosting:** DigitalOcean ($200 GitHub Pack credit) or Azure App Service (Founders Hub credit) for your backend/API.
- **Speech (if needed):** Deepgram or Azure Speech free monthly minutes for any voice-based tutoring feature.

This combination should let OpenLearn AI run a real MVP and pilot at **effectively $0 out of pocket** through graduation and several months beyond, provided you sequence applications per the roadmap in Section 3 and re-verify each program's current terms before relying on them.

---

## Verification checklist before you rely on any figure above

- [ ] Confirm current DEPI/DEBI round is open and includes an AI & Data Science track (mcit.gov.eg / depi.gov.eg)
- [ ] Confirm GitHub Copilot Student sign-up status (paused as of mid-2026 — may have reopened)
- [ ] Confirm DigitalOcean GPU exclusions still apply to the GitHub Pack credit
- [ ] Confirm NVIDIA Inception's incorporation requirement and whether a simple Egyptian sole-proprietorship/startup license satisfies it
- [ ] Confirm current free-tier limits for Gemini, Groq, Mathpix, Qdrant Cloud, and Pinecone (these shift often)
- [ ] Check ITIDA's current program list directly, as names/tracks change year to year

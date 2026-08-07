<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Competitive Analysis for OpenLearn AI

*Research snapshot: August 7, 2026. Publicly documented information is separated from technical inference. Private vendor architectures, algorithmic details, customer counts, and funding figures are marked as undisclosed or inferred where appropriate.*

## Executive Summary

OpenLearn AI is entering a crowded but fragmented market. Existing products generally specialize in one of four areas:

1. **Adaptive courseware:** Carnegie Learning, Knewton, ALEKS, CENTURY, Area9 Lyceum, Cerego and Sana.
2. **AI tutoring and content transformation:** Khanmigo, Quizlet AI, Duolingo Max and Sana Learn.
3. **Open learning infrastructure and research:** OLI Torus, OATutor, ASSISTments and Moodle.
4. **Enterprise learning platforms:** Sana, Realizeit and Area9 Lyceum.

The main strategic gap is not simply “AI tutoring.” Commercial platforms already provide tutoring, content generation, recommendations, assessments and dashboards. The stronger opportunity is an **open, Arabic-first, privacy-preserving learning-engineering platform** that combines:

- Document-to-course conversion.
- Arabic/English OCR and parsing.
- Explicit knowledge graphs.
- Explainable student modeling.
- BKT, IRT and CAT rather than opaque recommendation alone.
- Local-first inference.
- Open standards and LMS interoperability.
- Reproducible research.
- Offline or low-connectivity deployment.
- Teacher-controlled personalization.

The most important lesson is architectural: OpenLearn AI should not attempt to build one enormous “AI educator.” It should build a modular learning engine in which LLMs are used for language, explanation and content transformation, while assessment, mastery estimation, prerequisite logic and progression remain governed by educational and psychometric models.

Commercial systems demonstrate the value of adaptive pathways, but their core algorithms and content are generally proprietary. OLI Torus and OATutor demonstrate that open-source adaptive learning is viable, although neither provides the full document-ingestion, multilingual RAG and modern LLM stack envisioned by OpenLearn AI. OATutor uses BKT for mastery estimation, while OLI Torus emphasizes open courseware authoring, research instrumentation and adaptive course delivery.[^1][^2][^3]

***

## Market Landscape

### Market segmentation

| Segment | Representative products | Primary value | Main limitation for OpenLearn AI |
| :-- | :-- | :-- | :-- |
| Adaptive mathematics | Carnegie MATHia, ALEKS, Knewton Alta | Fine-grained skill diagnosis and sequencing | Usually proprietary, subject-specific or institution-focused |
| Adaptive corporate learning | Sana Learn, Area9 Rhapsode, Realizeit | Personalization, analytics and enterprise administration | Limited openness, expensive, often English-first |
| Spaced repetition | Cerego, Quizlet, Anki | Retention and repeated practice | Usually weak on full curriculum graphs and tutoring |
| AI tutoring | Khanmigo, Quizlet Q-Chat, Duolingo Max | Conversational explanations and practice | Risk of hallucination, shallow mastery modeling and provider dependence |
| Open adaptive research | OATutor, OLI Torus, ASSISTments | Reproducibility, experimentation and open content | Less complete product experience and limited generative-AI functionality |
| AI content transformation | Quizlet Magic Notes, Sana, emerging document tutors | Converts source material into study resources | Often weak on provenance, calibration and long-term learner modeling |

### Primary strategic conclusion

OpenLearn AI should position itself as:

> **An open learning-engineering stack for turning Arabic and multilingual educational materials into measurable, adaptive and locally deployable learning experiences.**

That is more defensible than positioning it as another generic chatbot or flashcard application.

***

# Competitor Profiles

## 1. Carnegie Learning

### Overview

Carnegie Learning originated from Carnegie Mellon University research and was founded in 1998 by researchers including Steven Ritter, William Hadley, John Anderson and Ken Koedinger. The company develops K–12 mathematics and literacy products, including MATHia, and was acquired by CIP Capital in 2018. Public company materials state that its research work has received more than \$90 million in grant funding from organizations including the Gates Foundation, Walton Family Foundation and the U.S. Department of Education.[^4][^5]

Its principal users are schools, districts, teachers and K–12 students. The business is primarily commercial institutional licensing, supplemented by curriculum, professional-learning and implementation services. Exact current revenue, active-user counts and product-level profitability are not publicly disclosed.

### Product and learning capabilities

| Capability | Evidence and assessment |
| :-- | :-- |
| Adaptive learning | Core capability of MATHia; adapts at a detailed skill level and provides just-in-time feedback and hints. [^6] |
| Student modeling | Strongly implied by skill-level adaptation and cognitive tutoring; detailed model is proprietary. |
| Knowledge tracing | Uses cognitive modeling and student performance data; exact current algorithm is not publicly specified. |
| Knowledge graph | Not clearly documented as a product-level graph in public materials. |
| AI tutor | MATHia is designed to emulate aspects of a one-to-one math tutor. [^6] |
| LLM integration | Generative AI has been used in research to revise math word problems, but this should not be confused with the core MATHia architecture. [^7] |
| Assessment | Formative assessment, diagnostics, embedded practice and progress reporting. |
| Teacher dashboard | Yes; teacher and district analytics are central to the product. |
| Accessibility | Carnegie Learning and CAST worked on adaptive reading supports for students with reading disabilities. [^7][^8] |
| Content authoring | Primarily publisher-created and curriculum-aligned content rather than open user-generated ingestion. |
| OCR/RAG/vector database | Not publicly documented. |
| Unique feature | Deep integration of cognitive-science tutoring, domain-specific curriculum and intervention data. |

### AI architecture and learning science

**Documented:** Carnegie Learning describes MATHia as combining AI and cognitive science and adapting instruction at the skill level. Its research lineage includes cognitive modeling and intelligent tutoring systems.[^6][^4]

**Inferred:** A plausible architecture includes a skill or knowledge-component model, mastery estimation, error classification, hint selection, worked examples and rule-based or model-based tutoring policies. This is an inference, not a confirmed implementation.

**Learning science:** The product is associated with mastery learning, cognitive modeling, formative assessment, immediate feedback, scaffolding, misconception diagnosis and one-to-one tutoring principles. It is not publicly established that modern MATHia uses BKT, DKT, IRT or CAT specifically.

### Strengths

- Exceptional depth in mathematics and cognitive tutoring.
- Long research history and institution-scale deployment.
- Strong teacher and district workflow integration.
- Better pedagogical grounding than a generic LLM tutor.
- Demonstrated interest in accessibility and reading barriers in mathematics.[^7]


### Weaknesses

- Closed platform and proprietary models.
- Primarily K–12 and subject-focused.
- Content creation appears more publisher-centered than learner-document-centered.
- Public documentation does not expose enough architecture for independent reproduction.
- Commercial deployment and curriculum alignment can make experimentation slower.
- Dependence on structured, curated content rather than arbitrary Arabic PDFs.


### Relevance to OpenLearn AI

| Learn from Carnegie | Do not copy directly |
| :-- | :-- |
| Model skills and misconceptions explicitly. | A narrow mathematics-only product strategy. |
| Treat hints as pedagogical interventions, not merely generated text. | Closed content and opaque student models. |
| Build teacher intervention dashboards. | Heavy institutional implementation as an MVP prerequisite. |
| Evaluate learning outcomes, not chatbot engagement. | Assuming cognitive tutoring models transfer automatically across subjects. |

**Priority for OpenLearn AI:** high for pedagogical tutoring, hint policies, misconception handling and teacher intervention; low for replicating a complete K–12 curriculum business.

***

## 2. Cerego

### Overview

Cerego is an adaptive learning company founded in 2008. Public company profiles describe it as a platform for personalized learning, content creation and spaced repetition. Public funding databases report approximately \$33.1 million raised, although different databases report inconsistent totals; this should be treated as an approximate, non-authoritative figure.[^9][^10]

Its users include learners, educators, publishers and institutions. The business model is commercial software and content partnerships. Current active-user scale and financial status are not sufficiently documented in authoritative public sources.

### Product capabilities

| Capability | Assessment |
| :-- | :-- |
| Adaptive learning | Yes, centered on adaptive review and individualized learning paths. |
| Student modeling | Strong in memory state and item-level performance. |
| Knowledge tracing | Proprietary learner-memory modeling is documented conceptually, but exact algorithm is not public. |
| Spaced repetition | Core differentiator. |
| Flashcards | Core use case. |
| Assessment | Practice, recall and retention checks. |
| AI tutor | Not its defining public positioning. |
| LLM/RAG/OCR | Not clearly documented as core capabilities. |
| Teacher/institution dashboard | Available through institutional and publisher offerings, but current scope should be validated commercially. |
| Content authoring | Supports creation and delivery of learning content. |
| Unique feature | Strong emphasis on durable memory, recall scheduling and “what to review next.” |

### AI architecture and learning science

Cerego’s public positioning supports an adaptive memory model based on cognitive science and spaced repetition. The exact use of SM-2, a proprietary forgetting-curve model, Bayesian estimation or neural knowledge tracing is not publicly confirmed.

The key learning-science mechanisms are retrieval practice, spacing, forgetting-curve management, mastery progression and confidence or recall judgments. This is a narrower but more mature specialization than a general adaptive-learning platform.

### Strengths

- Strong focus on retention rather than superficial completion.
- Clear and understandable learner value proposition.
- Mature item-level scheduling.
- Useful benchmark for OpenLearn AI’s SM-2 or successor scheduling layer.


### Weaknesses

- More focused on memorization and review than conceptual tutoring.
- Flashcard-centered designs can oversimplify complex skills.
- Public technical transparency is limited.
- The platform does not appear to offer OpenLearn AI’s planned document-to-knowledge-graph pipeline.
- Spaced repetition alone does not solve prerequisite sequencing, misconception diagnosis or open-ended reasoning.


### Relevance to OpenLearn AI

OpenLearn AI should implement spaced repetition as a **retention subsystem**, not as the whole adaptive engine. Cerego demonstrates that the system should store:

- Item difficulty.
- Learner recall probability.
- Last successful and failed retrieval.
- Confidence.
- Time since review.
- Concept importance.
- Interference and prerequisite relationships.

A useful design is to combine an SM-2-style scheduler with concept-level mastery from BKT or a Bayesian learner model.

***

## 3. Knewton

### Overview

Knewton developed an adaptive-learning platform for education publishers and institutions. Its public developer documentation states that the platform maps pedagogical relationships among concepts, lessons, homework and assessments into a knowledge graph, then uses learner data and that graph to recommend activities.[^11]

Knewton’s model is primarily B2B/B2B2C: it provides adaptive infrastructure that partners embed into educational products. Knewton’s historical scale and financing are significant, but public sources have reported changing ownership, product strategy and availability over time. Current financial and deployment figures should not be treated as reliable without direct company confirmation.

### Product capabilities

| Capability | Assessment |
| :-- | :-- |
| Adaptive learning | Core capability. |
| Knowledge graph | Explicitly documented in Knewton’s developer documentation. [^11] |
| Student modeling | Uses learner interaction data to estimate appropriate activities. |
| Recommendation engine | Core platform function. |
| Assessment | Supports lessons, homework and assessments through partner integrations. |
| Curriculum mapping | Central to mapping content concepts and relationships. |
| AI tutor | Not the primary public product identity. |
| LLM/RAG/OCR | Not publicly documented as core platform capabilities. |
| Vector database | Not publicly documented. |
| Teacher/institution dashboard | Usually supplied by partner products rather than being the main Knewton interface. |
| Unique feature | Adaptive infrastructure designed to be embedded into other publishers’ products. |

### AI architecture

**Documented:** Knewton uses a knowledge graph representing relationships among educational concepts and content activities. It consumes partner content and learner data to recommend an appropriate next activity.[^11]

**Inferred:** The system likely combines content metadata, prerequisite relationships, learner performance history, recommendation policies and mastery estimation. Public documentation does not establish whether the current system uses BKT, DKT, IRT, reinforcement learning, embeddings or a vector database.

### Learning science

Knewton’s design is consistent with mastery learning, prerequisite modeling, adaptive sequencing, formative assessment and individualized practice. It is especially relevant to OpenLearn AI because it separates:

1. The content graph.
2. The learner state.
3. The recommendation policy.
4. The delivery product.

### Strengths

- Strongest direct precedent for knowledge-graph-driven adaptive infrastructure.
- Partner-oriented architecture.
- Clear distinction between learning objects and learner recommendations.
- Relevant model for a provider-agnostic OpenLearn AI engine.


### Weaknesses

- Proprietary implementation.
- Relies on partner content quality and metadata.
- Knowledge graphs can be expensive to author and maintain.
- Poorly constructed prerequisite graphs can create brittle pathways.
- Public technical transparency is insufficient for exact replication.
- Partner integrations can slow distribution and reduce direct learner feedback.


### Relevance to OpenLearn AI

Knewton is the most important conceptual competitor for OpenLearn AI’s knowledge-graph layer. OpenLearn AI should improve on the model by supporting:

- Automatic graph extraction from Arabic and English documents.
- Human review of extracted concepts and prerequisites.
- Provenance for every graph edge.
- Versioned graphs.
- Multiple competing prerequisite hypotheses.
- Graph-based retrieval for tutoring.
- Export using open formats rather than a proprietary API.

***

## 4. Squirrel AI

Squirrel AI is a China-origin adaptive-learning company founded in 2014. Public accounts describe its Intelligent Adaptive Learning System as launching in 2017 and report substantial historical funding and valuation, although these figures are difficult to validate independently and should be treated cautiously.[^12]

Its central proposition is large-scale intelligent adaptive education, particularly through diagnostic learning and individualized pathways. Public technical descriptions commonly emphasize fine-grained knowledge components and adaptive teaching, but detailed production architecture, model weights and reproducible evaluations are not broadly available.

### Strengths

- Large-scale adaptive-learning ambition.
- Strong focus on knowledge decomposition and diagnostic teaching.
- Important benchmark for the commercial use of concept-level personalization.


### Weaknesses

- Limited public reproducibility.
- Funding and scale claims vary by source.
- Most evidence is company-reported or secondary.
- Less useful as a direct open-source engineering reference.
- China-specific curriculum and market assumptions may not transfer to Arabic university education.

**OpenLearn lesson:** Separate marketing claims from independently replicated learning outcomes. Require public benchmarks, ablations and error analysis.

***

## 5. CENTURY Tech

CENTURY is a UK-based AI-powered teaching and learning platform founded by Priya Lakhani. It provides personalized pathways, intervention recommendations and teacher analytics. The UKRI Gateway to Research describes its project as using machine learning and large-scale data to generate meaningful learner-performance insights and personalized paths.[^13][^14]

CENTURY states that its core recommendation platform uses proprietary, non-generative AI trained in-house on billions of learning interactions. It also offers optional generative-AI capabilities.[^15]

### Capabilities

- Adaptive recommendations.
- Knowledge-gap and misconception detection.
- Teacher dashboards.
- Intervention recommendations.
- Curriculum resources and “nuggets.”
- Knowledge tracing.
- Retention or memory-boost activities.
- Optional generative AI.
- Institutional and school deployment.


### Architecture and learning science

CENTURY publicly distinguishes non-generative adaptive models from optional LLM features. This is strategically important: its sequencing engine is not presented as a chatbot. The company describes analysis of previous performance, prediction of future performance and recommendation of the next study activity.[^15]

The learning-science basis includes mastery learning, formative assessment, intervention, retrieval and neuroscience-informed personalization. The exact models are proprietary.

### Strengths

- Strong teacher-facing intervention model.
- Clear separation between adaptive analytics and generative AI.
- Real-world interaction data at scale.
- Good example of using AI to reduce teacher workload.


### Weaknesses

- Proprietary and closed.
- Mostly aligned with school systems and established content libraries.
- Limited public algorithmic detail.
- Potential risk of over-relying on historical interaction data, which may reproduce curriculum or demographic bias.
- Arabic and offline-first capabilities are not central public differentiators.

**OpenLearn lesson:** Make the teacher dashboard a first-class product, and keep the recommendation engine separate from the LLM.

***

## 6. Khan Academy and Khanmigo

Khanmigo is Khan Academy’s AI-powered tutor and teaching assistant. Khan Academy emphasizes that Khanmigo guides students toward answers rather than simply giving them answers, and connects the tutor to Khan Academy’s content library.[^16]

Its educator features include lesson planning, question generation, classroom differentiation and teaching assistance.[^17]

### Strengths

- Strong educational brand and large content ecosystem.
- Socratic tutoring orientation.
- Student and teacher use cases.
- Broad subject coverage.
- Better pedagogical guardrails than an unrestricted chatbot.


### Weaknesses

- Closed-source model and product.
- Tightly coupled to Khan Academy content.
- General-purpose tutoring may not provide explicit BKT, IRT or CAT controls to end users.
- Cloud and provider dependency.
- Arabic document ingestion and local deployment are not the primary product proposition.

**OpenLearn lesson:** Build “answer withholding,” Socratic questioning, hint escalation and citation-aware tutoring. Do not rely on a general LLM to determine mastery.

***

## 7. Quizlet AI

Quizlet combines a large user-generated study ecosystem with AI-powered tools. Magic Notes can transform uploaded notes into flashcards, practice tests and other study materials. Q-Chat was introduced as a personalized AI tutor using the OpenAI ChatGPT API, with activities such as teaching, quizzing, application and sentence practice.[^18]

### Strengths

- Excellent source-material-to-study-set workflow.
- Familiar flashcard and quiz interaction model.
- Large distribution and learner-generated content.
- Strong benchmark for rapid onboarding from notes.


### Weaknesses

- User-generated content quality varies.
- Flashcards and generated questions may not represent a complete curriculum.
- Limited public transparency around mastery modeling and retrieval architecture.
- Potential hallucination, ambiguity and answer-quality problems in generated materials.
- Less emphasis on institution-owned, explainable knowledge graphs.

**OpenLearn lesson:** Document ingestion is a compelling entry point, but every generated concept, question and answer should include provenance, confidence and human-editing workflows.

***

## 8. Duolingo Max

Duolingo Max added GPT-4-powered “Explain My Answer” and “Roleplay.” The former gives explanations after an error; the latter provides guided conversational language practice.[^19][^20]

### Strengths

- Excellent conversational practice design.
- Tight integration of AI into an established instructional loop.
- Clear use cases for generative models.
- Strong engagement and habit formation.


### Weaknesses

- Narrow subject domain.
- AI explanations can still be imperfect.
- Provider dependence on external LLMs.
- Premium AI features can create access inequity.
- The product’s strongest personalization is embedded in its language-learning ecosystem rather than exposed as an open learning engine.

**OpenLearn lesson:** Use LLMs for interaction-rich practice, but connect every conversation to explicit objectives, rubrics and learner-state updates.

***

## 9. Sana Learn

Sana is an AI company founded in Stockholm and focused on knowledge tools and enterprise learning. Sana Learn combines LMS, learning-experience-platform, authoring, virtual-classroom and AI-tutor functionality. The company says it uses AI to personalize experiences, generate content, answer questions with citations and produce analytics.[^21][^22][^23]

Sana’s public materials describe adaptive assessment, personalized learning paths and knowledge-retention models that estimate knowledge half-life.[^24][^25]

### Strengths

- Strong enterprise product breadth.
- AI-native authoring and content transformation.
- Search and question-answering grounded in organizational knowledge.
- Analytics and administrative automation.
- Explicit attention to retention and adaptive review.


### Weaknesses

- Commercial enterprise focus.
- Closed platform and proprietary models.
- Public architecture does not establish use of Neo4j, Qdrant, RAG frameworks or specific KT algorithms.
- Primarily optimized for corporate learning rather than university courseware or open research.
- Local-first and offline deployment are not central positioning.

**OpenLearn lesson:** Integrate authoring, tutor, analytics and administration—but keep the underlying learning record portable and standards-based.

***

## 10. Area9 Lyceum

Area9 Lyceum markets a multidimensional adaptive-learning platform based on more than two decades of cognitive research. It reports serving more than 30 million learners across hundreds of subject areas and describes adaptation across multiple dimensions of learning and learner state.[^26][^27]

### Strengths

- Mature adaptive-learning specialization.
- Strong focus on cognitive science and real-time adaptation.
- Enterprise training and professional education experience.
- Useful example of adapting not only difficulty but learner confidence, speed and state.


### Weaknesses

- Proprietary architecture.
- Public claims about scale and efficiency are not equivalent to independent causal evidence.
- Enterprise content-production effort can be substantial.
- LLM and content-generation functionality is newer than the underlying adaptive platform.
- Not an open Arabic-first infrastructure.

**OpenLearn lesson:** Track confidence, fluency and conscious competence—not merely correctness.

***

## 11. ALEKS

ALEKS is McGraw Hill’s adaptive learning product, originating from University of California, Irvine research and based on Knowledge Space Theory. McGraw Hill describes it as maintaining a detailed map of the learner’s knowledge and identifying topics the learner is ready to learn next.[^28][^29]

### Strengths

- Clear formal knowledge-state representation.
- Strong diagnostic assessment.
- Mature mathematics and science content.
- Effective visualization of progress and readiness.
- Direct precedent for graph/state-based learning.


### Weaknesses

- Primarily commercial and subject-specific.
- Limited generative-tutor and document-ingestion identity.
- Knowledge-space authoring is expensive.
- Not open-source or Arabic-first.

**OpenLearn lesson:** Student knowledge is not necessarily one scalar “mastery score.” A structured set of known, unknown and ready-to-learn concepts can produce more useful paths.

***

## 12. OLI Torus

OLI Torus is the most strategically relevant open platform. It is an open-source platform for creating, delivering, improving and researching adaptive courseware. The project is MIT licensed and supports collaborative development, course authoring, learning-science instrumentation, LMS integration and research workflows.[^2][^3][^30]

### Strengths

- Open-source and commercially usable.
- Strong learning-engineering orientation.
- Research-ready data infrastructure.
- Authoring and delivery are integrated.
- Designed for experimentation and reproducibility.


### Weaknesses

- Not primarily an Arabic document-to-course system.
- LLM, OCR, vector search and RAG are not its defining architecture.
- Requires instructional design and structured course authoring.
- May be more useful as a platform to integrate with than as a direct competitor.

**OpenLearn lesson:** Reuse or study OLI’s principles for event instrumentation, content authoring, experimentation and open licensing. OpenLearn AI should avoid building a proprietary course format that makes future research difficult.

***

## 13. OATutor

OATutor is an open-source adaptive tutoring system based on intelligent-tutoring-system principles. It uses Bayesian Knowledge Tracing for skill mastery estimation, is implemented in React, can be deployed without a traditional backend and includes open educational content.[^31][^1]

It supports rapid experimentation, GitHub deployment, LTI integration, A/B testing and publication of tutor, content and analysis code.[^32][^31]

### Strengths

- Directly relevant open-source reference.
- Explicit BKT implementation.
- Reproducibility and research transparency.
- Lightweight deployment.
- Open content and LMS integration.


### Weaknesses

- Narrower scope than OpenLearn AI.
- Does not provide a full multilingual document-processing pipeline.
- Limited modern LLM/RAG functionality.
- React-centric architecture differs from OpenLearn AI’s planned FastAPI/PostgreSQL/Neo4j/Qdrant stack.
- Content authoring remains structured and human-curated.

**OpenLearn lesson:** Build the smallest working adaptive loop first: item, skill, response, BKT update, next-item policy and event log.

***

## 14. ASSISTments

ASSISTments is a free math platform for teachers and students that provides immediate feedback and teacher-facing data. Its research ecosystem has produced datasets from real platform interactions and randomized experiments, including public 2019–2020 interaction data.[^33][^34][^35]

### Strengths

- Strong connection between product use and educational research.
- Public datasets and experimental orientation.
- Teacher feedback and real-time data.
- Useful benchmark for ethical data release and evaluation.


### Weaknesses

- Primarily mathematics-focused.
- Not a general document-to-course platform.
- Open data still requires careful privacy governance.
- Less focused on LLM tutoring and semantic retrieval.

**OpenLearn lesson:** Design the event schema and research-release process at the beginning, not after deployment.

***

# Competitor Matrix

| Product | Adaptive path | Explicit learner model | KG/skill graph | AI tutor | Spaced review | Teacher analytics | Open source | Arabic-first |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: |
| Carnegie MATHia | High | High, proprietary | Not clearly public | Domain tutor | Some | High | No | No |
| Cerego | High | Memory-focused | Limited public evidence | Low | High | Medium | No | No |
| Knewton | High | High, proprietary | Yes | Low | Not core | Partner-dependent | No | No |
| Squirrel AI | High | High, proprietary | Concept-focused | Medium | Unknown | High | No | No |
| CENTURY | High | High, proprietary | Skill/content relationships | Medium | Yes | High | No | No |
| Khanmigo | Medium | Partly implicit | Content-linked | High | Low | High for educators | No | Partial/variable |
| Quizlet AI | Medium | Limited public evidence | Limited | Medium | High through study sets | Medium | No | Partial |
| Duolingo Max | High within language learning | Proprietary | Curriculum-linked | High | High | Low for institutions | No | Limited |
| Sana Learn | High | High, proprietary | Skill/content metadata | High | High | High | No | No |
| Area9 | High | Multidimensional, proprietary | Content-linked | Medium | Yes | High | No | No |
| ALEKS | High | Knowledge-state model | Knowledge space | Low/medium | Retention checks | High | No | No |
| OLI Torus | Configurable | Courseware-dependent | Course graph | Emerging | Configurable | Research-oriented | Yes | No |
| OATutor | High | BKT | Skill map | Rule-based/scaffolded | Configurable | Research-oriented | Yes | No |
| ASSISTments | Configurable | Activity-dependent | Curriculum/skill tagging | Low | Low | High | Data/research openness | No |
| OpenLearn AI | Planned | BKT + IRT + learner model | Planned central feature | Planned | Planned SM-2 | Planned | Yes | Yes |


***

# Feature Matrix for OpenLearn AI

| Capability | Commercial precedent | OpenLearn AI recommendation |
| :-- | :-- | :-- |
| OCR | Common in document-AI products, less central in adaptive platforms | Build early for Arabic, English, tables, equations and scanned PDFs |
| PDF parsing | Quizlet and Sana demonstrate demand for source-material transformation | Build with page-level provenance and human review |
| Knowledge graph | Knewton and ALEKS show its value | Make it explicit, versioned and exportable |
| RAG | Sana and AI tutors demonstrate grounded Q\&A demand | Use hybrid vector + graph retrieval, not vector search alone |
| BKT | OATutor provides a direct open reference | Implement as the transparent baseline |
| DKT | Research standard, but less interpretable | Add later for comparison and prediction, not as the only model |
| IRT/CAT | Standard psychometric foundation for adaptive testing [^36][^37] | Use for calibrated diagnostic and summative assessments |
| Spaced repetition | Cerego demonstrates product value | Use SM-2 initially; evaluate newer memory models later |
| AI tutoring | Khanmigo, Quizlet and Duolingo validate demand | Add only after grounding and mastery updates work |
| Teacher dashboard | Carnegie, CENTURY and Sana show institutional importance | Include in MVP at least for explanations and intervention |
| Offline/local AI | Not a dominant commercial strength | Make this a primary differentiator |
| Open standards | OLI and OATutor provide precedents | Support LTI, xAPI/Caliper-like events, OpenAPI and exportable content |
| Arabic support | Large whitespace | Treat morphology, diacritics, RTL, dialect/register and Arabic OCR as core engineering |
| Content authoring | OLI and Sana show importance | Provide review queues rather than fully automatic publishing |


***

# Technology Matrix

| Layer | OpenLearn AI proposal | Main risk | Recommendation |
| :-- | :-- | :-- | :-- |
| Ingestion | OCR + PDF parser + layout analysis | Arabic OCR and equations | Preserve original pages, bounding boxes and confidence |
| Semantic processing | Chunking, concept extraction, objectives, prerequisite extraction | Hallucinated graph edges | Require evidence spans and human approval |
| Knowledge graph | Neo4j or compatible graph store | Graph maintenance cost | Version every node and edge |
| Retrieval | Qdrant hybrid vector search plus graph traversal | Semantic retrieval misses prerequisites | Combine dense, lexical and graph retrieval |
| Learner model | BKT baseline, IRT item model, confidence and forgetting state | Sparse learner data | Start with interpretable priors |
| Adaptive engine | Rule/policy layer selecting next activity | Optimizing clicks rather than learning | Optimize delayed learning outcomes |
| Assessment | Item bank, calibration, CAT | Poorly calibrated generated items | Human review and pilot calibration required |
| LLM layer | Provider abstraction with local models | Hallucination, cost, latency | Require citations, structured output and fallback |
| Analytics | Event stream, mastery history, cohort reports | Privacy and misleading metrics | Separate operational analytics from research datasets |
| API | FastAPI | Service sprawl | Begin as a modular monolith |
| Storage | PostgreSQL + object storage + graph + vector DB | Operational complexity | Delay microservices until load requires them |
| Deployment | Docker, local inference, optional cloud | Hardware variation | Support CPU-safe baseline and GPU acceleration |


***

# AI Architecture Matrix

| System | Publicly documented architecture | What is unknown |
| :-- | :-- | :-- |
| Carnegie MATHia | AI plus cognitive science; skill-level adaptation and tutoring | Exact KT, retrieval, model-serving and data architecture |
| Cerego | Adaptive learning and memory/spaced repetition | Exact forgetting model, embeddings and database architecture |
| Knewton | Partner content mapped into a pedagogical knowledge graph; recommendations generated from graph and learner data [^11] | Exact graph schema, mastery model and infrastructure |
| CENTURY | Proprietary non-generative AI analyzes performance and predicts next recommendations; optional LLM features [^15] | Model classes, training pipeline and feature store |
| Khanmigo | LLM tutor integrated with Khan Academy content and guardrails [^16] | Complete retrieval, orchestration and evaluation stack |
| Quizlet AI | GPT-based Q-Chat and source-material transformation | Full grounding, item-quality and learner-model architecture |
| Duolingo Max | GPT-4 for explanations and roleplay, within Duolingo’s instructional ecosystem [^19] | Current model mix, orchestration and adaptive sequencing details |
| Sana | AI tutor, semantic search, cited answers, adaptive learning and retention models [^21][^24] | Vector DB, graph model, KT and deployment details |
| OLI Torus | Open adaptive-courseware platform and research infrastructure [^2][^3] | Modern generative-AI architecture varies by implementation |
| OATutor | React-based open tutor with BKT and optional Firebase logging [^1] | Scale, production observability and advanced retrieval |
| OpenLearn AI | Planned graph + RAG + BKT/IRT/CAT + local-first LLM | Must be implemented and empirically validated |


***

# Learning Science Matrix

| Method | Best use | OpenLearn AI position |
| :-- | :-- | :-- |
| BKT | Transparent mastery estimation for discrete skills | MVP baseline |
| DKT | Sequence prediction with complex interaction patterns | Research track; compare against BKT |
| IRT | Calibrating item difficulty, discrimination and ability | Use for item-bank calibration |
| CAT | Efficient diagnostic or high-stakes testing | Add after item calibration |
| SM-2 | Practical spaced-repetition scheduling | MVP retention layer |
| Forgetting-curve models | Predicting review timing | Extend SM-2 after sufficient data |
| Mastery learning | Require evidence before progression | Core progression principle |
| Bloom’s taxonomy | Tagging cognitive level and question generation | Use as metadata, not as a complete learner model |
| Bayesian networks | Modeling dependencies and uncertainty | Useful for concept prerequisites and diagnosis |
| Cognitive models | Explaining errors and selecting hints | Domain-specific research opportunity |
| Retrieval practice | Durable learning | Make practice central |
| Confidence-based learning | Detecting overconfidence and underconfidence | Track confidence explicitly |
| Constructivism | Dialogue, explanation and active construction | Use in tutor interaction, not as a sequencing algorithm |

BKT originated as a model of procedural skill acquisition and mastery learning, while DKT introduced recurrent neural networks for modeling interaction sequences.  IRT provides the psychometric basis for relating learner ability and item characteristics, and CAT uses those estimates to select more informative items adaptively.[^36][^37][^38][^39]

***

# SWOT Analysis

| Strengths | Weaknesses |
| :-- | :-- |
| Arabic-first positioning | Limited initial data and content |
| Open-source and inspectable | Small research and engineering team |
| Planned graph, RAG and learner-model integration | High architectural complexity |
| Local-first and provider-agnostic design | Difficult local-model quality and deployment |
| Combination of tutoring, assessment and analytics | Risk of attempting too much in the MVP |
| Potential for university and research use | Need for psychometric and instructional-design expertise |

| Opportunities | Threats |
| :-- | :-- |
| Arabic educational-content digitization | Large platforms can add Arabic AI features |
| University and vocational learning | LLM commoditization reduces tutor differentiation |
| Offline and privacy-sensitive deployments | Commercial vendors have more interaction data |
| Open educational resources | Poor generated content can damage trust |
| LMS and government deployments | Privacy, child-safety and education regulation |
| Reproducible learning research | Knowledge-graph authoring may become bottleneck |


***

# Biggest Risks

## 1. Scope explosion

The planned system contains at least five major products: document processing, knowledge management, adaptive courseware, AI tutoring and analytics. Implementing all simultaneously will likely produce shallow versions of each.

## 2. False precision

BKT, IRT and CAT produce mathematically precise outputs only when skills, items, responses and calibration data are reliable. A sophisticated model applied to noisy automatically generated questions can be less trustworthy than a simple rule system.

## 3. LLM hallucination

An LLM may generate plausible but incorrect explanations, distractors, prerequisites or Arabic translations. Every generated object should carry source citations, confidence, model/version metadata and review status.

## 4. Knowledge-graph maintenance

Automatic graph extraction will save authoring time but create uncertain edges. OpenLearn AI should support graph review, conflict resolution, edge provenance and versioning from the beginning.

## 5. Data sparsity

A new platform will not initially have enough interactions for DKT or complex recommenders. BKT with priors, IRT calibration and content metadata are better early-stage choices.

## 6. Evaluation failure

Completion, time-on-task and chatbot satisfaction are not sufficient. The platform needs pre/post tests, delayed retention tests, transfer questions, calibration error, fairness metrics and controlled experiments.

## 7. Arabic complexity

Arabic presents challenges involving RTL layout, diacritics, morphology, classical versus modern standard Arabic, dialects, code-switching, OCR quality and equations embedded in Arabic text. Treat Arabic as a primary product and evaluation domain, not simply a translation target.

***

# Biggest Opportunities

- **Arabic academic document intelligence:** Convert textbooks, lecture notes, scanned documents and institutional PDFs into structured learning objects.
- **University course companion:** Support Arabic-speaking university students without trying to replace the LMS.
- **Offline-first deployments:** Serve institutions with unreliable connectivity, data-sovereignty requirements or limited cloud budgets.
- **Research reproducibility:** Publish datasets, model cards, evaluation scripts, graph snapshots and experiment configurations.
- **Teacher-controlled AI:** Let instructors accept, edit, reject and annotate generated concepts, questions and explanations.
- **Open learning graphs:** Create reusable Arabic concept graphs that can serve multiple courses and institutions.
- **Privacy-preserving analytics:** Keep identifiable learner data local while exporting aggregated or de-identified research events.
- **Arabic accessibility:** Support screen readers, RTL interfaces, speech input/output, simplified language and low-bandwidth modes.
- **Provider independence:** Allow local models, hosted APIs and institution-specific models through one interface.

***

# Recommended MVP Scope

The MVP should not implement every component in the project brief. It should demonstrate one complete, measurable learning loop.

## MVP components

1. **Document ingestion**
    - Arabic and English PDF upload.
    - OCR fallback for scanned pages.
    - Layout-aware text extraction.
    - Page and paragraph provenance.
2. **Human-reviewed content transformation**
    - Concepts.
    - Learning objectives.
    - Prerequisites.
    - Short explanations.
    - Multiple-choice and short-answer questions.
    - Source-linked answer rationales.
3. **Minimal knowledge graph**
    - Concept nodes.
    - Prerequisite edges.
    - Content-to-concept links.
    - Question-to-concept links.
    - Confidence and provenance for every edge.
4. **Transparent adaptive engine**
    - BKT per skill.
    - Basic readiness rules.
    - SM-2 review scheduling.
    - Difficulty metadata.
    - “Why was this recommended?” explanation.
5. **Grounded tutor**
    - RAG over approved source content.
    - Socratic hints.
    - No unsupported answers when evidence is absent.
    - Arabic and English responses.
    - Citation to document pages.
6. **Teacher review and analytics**
    - Approve or edit generated content.
    - View skill-level mastery.
    - Identify struggling learners.
    - Inspect recommendation rationale.
    - Export events and learning records.

## Defer until later

- Full DKT production deployment.
- Complex reinforcement-learning recommenders.
- High-stakes CAT.
- Automatic curriculum-wide graph construction without review.
- Multi-agent tutor orchestration.
- Large-scale microservices.
- Broad gamification.
- Fully autonomous exam generation.
- Complete LMS replacement.

***

# Long-Term Vision

OpenLearn AI can evolve into an open learning-engineering platform with five separable layers:

1. **Open content compiler:** Documents become versioned, reviewable learning objects.
2. **Learning graph:** Concepts, objectives, misconceptions, prerequisites and resources form an interoperable graph.
3. **Learner state service:** BKT, IRT, confidence, retention and activity history produce an explainable learner model.
4. **Pedagogical policy engine:** Selects the next content, question, hint or review activity.
5. **AI interaction layer:** Uses local or hosted models for tutoring, translation, generation and accessibility, constrained by the graph and source evidence.

This architecture would allow universities, ministries, teachers and researchers to use the same underlying engine while retaining control over content, learner data and model providers.

***

# Actionable Recommendations

## Product

- Position around **Arabic-first open adaptive learning**, not “ChatGPT for education.”
- Start with one subject and one document type.
- Make recommendation explanations visible to teachers and learners.
- Treat teacher review as a core workflow.
- Build LMS integration through LTI before attempting to replace the LMS.


## Technical

- Begin as a modular monolith with FastAPI, PostgreSQL and object storage.
- Add Neo4j and Qdrant only when graph and semantic retrieval requirements are demonstrated.
- Use a provider interface for LLMs, embeddings, OCR and rerankers.
- Store every generated artifact with source span, model version, prompt version, confidence and reviewer status.
- Keep learner events immutable and append-only.
- Use BKT as the production baseline and DKT as an experimental comparison.
- Separate retrieval, mastery estimation, recommendation and text generation into independent services or modules.


## Research

- Establish baseline datasets using synthetic and openly licensed content.
- Publish model cards and graph-quality metrics.
- Evaluate question quality with experts and learners.
- Compare BKT, DKT and simpler baselines on the same data.
- Measure delayed retention, transfer and learning gain—not only immediate correctness.
- Use OATutor, OLI Torus and ASSISTments as references for reproducible experimentation.[^3][^34][^31]


## Arabic

- Benchmark OCR separately for printed Arabic, scanned Arabic, mixed Arabic-English text, tables and mathematics.
- Preserve both normalized and original text.
- Support diacritic-insensitive search while retaining the original passage.
- Evaluate Modern Standard Arabic and domain-specific terminology.
- Create Arabic-specific hallucination, citation and question-quality test sets.
- Avoid assuming that translation from English preserves educational meaning.


## Governance

- Use open licenses for software and clearly labeled licenses for content.
- Obtain consent and minimize personally identifiable learner data.
- Provide deletion, export and local-deployment options.
- Add age-appropriate safety controls if used by minors.
- Make automated decisions inspectable and appealable.
- Do not use engagement metrics as a proxy for learning.

***

# Technical Inspiration and References

## Open-source platforms

- [OATutor GitHub repository](https://github.com/CAHLR/OATutor) — open adaptive tutoring system using BKT.[^1]
- [OATutor research platform](https://www.oatutor.io/researchers) — experiments, LTI, open content and reproducibility.[^31]
- [OLI Torus](https://oli.cmu.edu/torus/) — open adaptive courseware platform under the MIT license.[^3]
- [OLI research](https://oli.cmu.edu/research/) — learning-science research infrastructure and data-oriented courseware.[^40]
- [ASSISTments](https://www.assistments.org/) — teacher-centered formative math platform and research ecosystem.[^35]


## Official product and architecture sources

- [Knewton developer documentation](https://dev.knewton.com/) — knowledge-graph-based adaptive platform documentation.[^11]
- [Carnegie Learning](https://www.carnegielearning.com/company/press) — company research and product information.[^5]
- [CENTURY platform](https://www.century.tech/explore-century/secondary-schools/) — distinction between non-generative adaptive AI and optional generative AI.[^15]
- [Sana Learn](https://sanalabs.com/products/sana-learn/) — AI tutoring, cited answers, personalization and analytics.[^21]
- [ALEKS](https://www.mheducation.com/prek-12/program/aleks.html) — Knowledge Space Theory and adaptive mathematics.[^29]
- [Khanmigo](https://www.khanmigo.ai/) — AI tutor and teaching assistant.[^16]


## Research foundations

- [Corbett and Anderson, “Knowledge Tracing”](https://act-r.psy.cmu.edu/wordpress/wp-content/uploads/2012/12/893CorbettAnderson1995.pdf) — foundational BKT paper.[^41]
- [Piech et al., “Deep Knowledge Tracing”](https://proceedings.neurips.cc/paper/2015/file/bac9162b47c56fc8a4d2a519803d51b3-Paper.pdf) — recurrent-neural-network knowledge tracing.[^39]
- [IRT and CAT overview](https://onlinelibrary.wiley.com/doi/10.1002/9781119716723.ch8) — item calibration and adaptive item selection.[^37]
- [ASSISTments 2019–2020 dataset](https://osf.io/q7zc5/) — public interaction data for educational-data-mining research.[^34]


## Final strategic judgment

OpenLearn AI should not compete head-on with Carnegie Learning on polished K–12 mathematics, with Duolingo on habit-forming language instruction, or with Khan Academy on global content scale. Its defensible niche is the intersection of **Arabic educational content, open infrastructure, explainable learner modeling, grounded AI, local deployment and reproducible learning research**.

The winning sequence is:

> **Ingest one document well → build a trustworthy concept graph → estimate mastery transparently → recommend one justified next activity → measure retained learning.**

If OpenLearn AI can execute that loop reliably in Arabic and publish the implementation and evaluation, it will offer something that most commercial competitors do not: an inspectable, extensible learning engine rather than a closed educational application.
<span style="display:none">[^100][^101][^102][^103][^104][^105][^106][^107][^108][^109][^110][^111][^112][^113][^114][^115][^116][^117][^118][^119][^120][^121][^122][^123][^124][^125][^126][^127][^128][^129][^130][^131][^132][^133][^134][^42][^43][^44][^45][^46][^47][^48][^49][^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^70][^71][^72][^73][^74][^75][^76][^77][^78][^79][^80][^81][^82][^83][^84][^85][^86][^87][^88][^89][^90][^91][^92][^93][^94][^95][^96][^97][^98][^99]</span>

<div align="center">⁂</div>

[^1]: https://github.com/CAHLR/OATutor

[^2]: https://stevenjamesmoore.com/assets/papers/lak23_prac_bier.pdf

[^3]: https://oli.cmu.edu/torus/

[^4]: https://en.wikipedia.org/wiki/Carnegie_Learning

[^5]: https://www.carnegielearning.com/company/press

[^6]: https://www.businesswire.com/news/home/20240327088407/en/Carnegie-Learning-Wins-2024-EdTech-Award-for-MATHstream

[^7]: https://thejournal.com/articles/2024/02/26/ies-carnegie-learning-study-exploring-the-use-of-ai-to-help-students-with-reading-disabilities.aspx

[^8]: https://www.businesswire.com/news/home/20210817005195/en/Carnegie-Learning-and-CAST-Awarded-\$2-Million-from-US-Department-of-Education-to-Develop-Support-for-Reading-in-Mathematics

[^9]: https://pitchbook.com/profiles/company/56425-51

[^10]: https://www.f6s.com/company/cerego

[^11]: https://dev.knewton.com/

[^12]: https://en.wikipedia.org/wiki/Squirrel_AI

[^13]: https://www.unesco.org/en/articles/century-ai-powered-teaching-and-learning-platform

[^14]: https://gtr.ukri.org/project/AD74CAA9-B6A9-4D3D-8D2A-F13B01F3EA2A

[^15]: https://www.century.tech/explore-century/secondary-schools/

[^16]: https://www.khanmigo.ai/

[^17]: https://www.khanacademy.org/khan-for-educators/khanmigo-for-educators/xb4ad566b4fd3f04a:welcome-to-khanmigo-your-new-ai-teaching-assistant

[^18]: https://www.prnewswire.com/news-releases/quizlet-launches-advanced-ai-powered-tools-for-next-gen-studying-301895290.html

[^19]: https://openai.com/index/duolingo/

[^20]: https://investors.duolingo.com/news-releases/news-release-details/duolingo-max-shows-future-ai-education

[^21]: https://sanalabs.com/products/sana-learn/

[^22]: https://sanalabs.com/products/sana-learn/learning-management

[^23]: https://sanalabs.com/products/sana-learn/content-creation

[^24]: https://solve.mit.edu/solutions/25994

[^25]: https://help.sana.ai/en/articles/7485-adaptive-learning

[^26]: https://area9lyceum.com/adaptive-learning/

[^27]: https://area9lyceum.com/

[^28]: https://learn.mheducation.com/aleks.html

[^29]: https://www.mheducation.com/prek-12/program/aleks/MKTSP-GAB02M0.html

[^30]: https://oli.cmu.edu/

[^31]: https://www.oatutor.io/researchers

[^32]: https://cahlr.github.io/OATWeb/las.html

[^33]: https://eric.ed.gov/?id=ED571517

[^34]: https://osf.io/q7zc5/

[^35]: https://www.assistments.org/

[^36]: https://files.eric.ed.gov/fulltext/EJ1317443.pdf

[^37]: https://onlinelibrary.wiley.com/doi/10.1002/9781119716723.ch8

[^38]: http://act-r.psy.cmu.edu/?post_type=publications\&p=14344

[^39]: https://proceedings.neurips.cc/paper/2015/file/bac9162b47c56fc8a4d2a519803d51b3-Paper.pdf

[^40]: https://oli.cmu.edu/research/

[^41]: https://act-r.psy.cmu.edu/wordpress/wp-content/uploads/2012/12/893CorbettAnderson1995.pdf

[^42]: https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1663912/full

[^43]: https://www.kingsresearch.com/blog/personalization-engines-ai-customer-experience

[^44]: https://www.hpcwire.com/bigdatawire/this-just-in/oreilly-to-host-4th-ai-codecon-on-building-with-open-source-ai/

[^45]: https://al-fanarmedia.org/2025/12/metas-regional-director-says-arab-world-can-use-ai-faster-than-other-regions/

[^46]: https://gulfbusiness.com/2026/education-industry/uae-ministry-closes-university-over-repeated-violations/

[^47]: https://intellectia.ai/blog/best-ai-crypto-trading-bots-2026

[^48]: https://www.qualcomm.com/developer/blog/2025/11/gen-ai-for-education-socrqtiq-qualcomm-cloud-ai-100

[^49]: https://dl.acm.org/doi/full/10.1145/3766918.3766987

[^50]: https://files.eric.ed.gov/fulltext/EJ1505954.pdf

[^51]: https://dl.acm.org/doi/epdf/10.1145/3766918.3766987

[^52]: https://www.atlantis-press.com/article/126011423.pdf

[^53]: https://www.sciencedirect.com/science/article/pii/S2590291125007028

[^54]: https://theaspd.com/index.php/ijes/article/download/8843/6393/18358

[^55]: https://www.ijsat.org/papers/2025/4/9203.pdf

[^56]: https://ijrpr.com/uploads/V7ISSUE5/IJRPR65121.pdf

[^57]: https://ijarcce.com/papers/ai-driven-personalized-education-platform-design-architecture-and-implementation/

[^58]: https://inonx.com/building-reliable-ai-personalized-learning-platforms/

[^59]: https://www.ijsat.org/papers/2025/2/5955.pdf

[^60]: http://www.isis.tuwien.ac.at/people/list/publications/icalt2005.pdf

[^61]: https://ijsred.com/volume9/issue2/IJSRED-V9I2P348.pdf

[^62]: https://en.wikipedia.org/wiki/Cerego

[^63]: https://en.wikipedia.org/wiki/Smart.fm

[^64]: https://startupintros.com/orgs/cerego

[^65]: https://tracxn.com/d/companies/cerego/__GJ5R0svtGPbhWIsqeyA97ROfgVygA38TXKxHQ1nsnH4

[^66]: https://www.seedtable.com/startups/Cerego-MKKERG

[^67]: https://rocketreach.co/cerego-japan-profile_b5c68472f42e0ce7

[^68]: https://support.knewton.com/s/article/Knewton-Adaptive-Learning-and-How-it-s-Unique

[^69]: https://infiniteoer.ucd.ie/items/show/67

[^70]: https://ar.area9lyceum.com/

[^71]: https://area9lyceum.com/about/

[^72]: https://www.youtube.com/watch?v=8S2d90k3d-0

[^73]: https://help.area9lyceum.com/

[^74]: https://learningnews.com/news/area9-lyceum/2019/area9-lyceum-launches-new,-four-dimensional-adaptive-learning-platform

[^75]: https://support.century.tech/support/solutions/articles/44001898928-introduction-to-century

[^76]: https://checkpoint-elearning.com/node/26121

[^77]: https://www.century.tech/news/centurys-brain-and-ai-webinar-under-the-hood-and-beyond-the-hype/

[^78]: https://www.cnet.com/tech/services-and-software/duolingo-launches-new-ai-powered-subscription-tier/

[^79]: https://www.khanacademy.org/college-careers-more/khanmigo-for-students/x5443352261243283:introducing-khanmigo/x5443352261243283:getting-started-with-khanmigo/v/khanmigo-for-students-what-is-khanmigo-and-how-does-it-work

[^80]: https://fortune.com/education/articles/quizlet-ai-powered-tools-q-chat-magic-notes-quick-summary-gpt/

[^81]: https://www.zdnet.com/article/duolingo-is-now-equipped-with-gpt-4-heres-what-it-can-do-for-you/

[^82]: https://news.mynavi.jp/techplus/article/20230612-2702352/

[^83]: https://aisotools.com/blog/duolingo-max-review-2026

[^84]: https://www.techlearning.com/how-to/what-is-duolingo-max-the-gpt-4-powered-learning-tool-explained-by-the-apps-product-manager

[^85]: https://www.youtube.com/watch?v=0H8v8pIHR-8

[^86]: https://www.techtimes.com/articles/289128/20230317/duolingo-launches-gpt-4-ai-powered-virtual-language-tutor-new.htm

[^87]: https://www.youtube.com/watch?v=EUSZZMHx8a8

[^88]: https://moodle.org/plugins/block_exacomp

[^89]: https://moodle.org/plugins/qbank_yetkinlik

[^90]: https://github.com/CAHLR/OATutor-SUNY

[^91]: https://www.iase-pub.org/conference_proceedings/IASECP/article/download/265/258

[^92]: https://stevenjamesmoore.com/assets/papers/lak19_workshop_bier.pdf

[^93]: https://oli.cmu.edu/research/publications/

[^94]: https://comet.edustandards.org/en/

[^95]: https://online-learning-initiative.org/introducing-the-oli-research-team/

[^96]: https://www.gartner.com/reviews/market/corporate-learning-technologies/vendor/sana-labs/product/sana-learn

[^97]: https://arxiv.org/pdf/2501.14256v2.pdf

[^98]: https://educationaldatamining.org/EDM2021/virtual/static/pdf/EDM21_paper_126.pdf

[^99]: https://sanalabs.com/

[^100]: https://etd.repository.ugm.ac.id/penelitian/detail/228454

[^101]: https://sanalabs.com/platform-solutions

[^102]: https://help.sana.ai/en/articles/7484-this-is-sana

[^103]: https://medium.com/sana-labs/the-pivotal-era-of-learning-how-sana-labs-uses-ai-to-reimagine-learning-for-your-workforce-6bc761281d49

[^104]: https://www.demandneversleeps.com/blog/sana-labs

[^105]: https://www.youtube.com/watch?v=5gJiw_0RqsU

[^106]: https://papers.neurips.cc/paper_files/paper/2022/file/75ca2b23d9794f02a92449af65a57556-Paper-Datasets_and_Benchmarks.pdf

[^107]: https://arxiv.org/pdf/1012.0042.pdf

[^108]: https://www.erudit.org/en/journals/mee/2008-v31-n2-mee01401/1025005ar.pdf

[^109]: https://www.semanticscholar.org/paper/Deep-Knowledge-Tracing-Piech-Bassen/fa98d609eb14ce25dd73cd8713a5e284948b4ff4

[^110]: https://link.springer.com/chapter/10.1007/11499305_63

[^111]: https://github.com/bigdata-ustc/EduKTM/blob/main/docs/DKT.md

[^112]: https://web.stanford.edu/~cpiech/bio/papers/dktCode.pdf

[^113]: https://liner.com/review/deep-knowledge-tracing

[^114]: https://ijsoc.goacademica.com/index.php/ijsoc/article/view/1581

[^115]: https://liner.com/ko/review/deep-knowledge-tracing

[^116]: https://huggingface.co/ASSISTments/datasets

[^117]: https://huggingface.co/datasets/ASSISTments/FoundationalASSIST

[^118]: https://beginnersinai.org/aleks-explained/

[^119]: https://im.tea.texas.gov/sites/default/files/evaluations/McGraw Hill_TX%20ALEKS%20Final%20Response_1.pdf

[^120]: https://ucfsandbox.service-now.com/kb?id=kb_article_view\&sysparm_article=KB0013533

[^121]: https://www.youtube.com/watch?v=2jjI3evTDZg

[^122]: https://psudev.service-now.com/sys_attachment.do?sys_id=f3edea3197c8dd102dc779cfe153afe7

[^123]: https://lab.realizeitlearning.com/papers/FrameworkPersonalizedAdaptiveContent.pdf

[^124]: https://www.amphi.com/aleks

[^125]: https://everyhomeschool.com/directory/publishers/aleks

[^126]: https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1663912/full

[^127]: https://www.kingsresearch.com/blog/personalization-engines-ai-customer-experience

[^128]: https://www.hpcwire.com/bigdatawire/this-just-in/oreilly-to-host-4th-ai-codecon-on-building-with-open-source-ai/

[^129]: https://al-fanarmedia.org/2025/12/metas-regional-director-says-arab-world-can-use-ai-faster-than-other-regions/

[^130]: https://gulfbusiness.com/2026/education-industry/uae-ministry-closes-university-over-repeated-violations/

[^131]: https://intellectia.ai/blog/best-ai-crypto-trading-bots-2026

[^132]: https://www.qualcomm.com/developer/blog/2025/11/gen-ai-for-education-socrqtiq-qualcomm-cloud-ai-100

[^133]: http://www.ressjournal.com/Makaleler/487422172_37-Ahmet%20Dervi%C5%9F%20M%C3%9CAZ%C4%B0N.pdf

[^134]: https://www.multiresearchjournal.com/admin/uploads/archives/archive-1724823129.pdf


# OpenLearn AI — User System Requirements & Installation Guide

*Everything you need to know before you download and run OpenLearn AI on your own computer.*

---

## 1. Introduction

OpenLearn AI is an AI study companion that can read your PDFs, build flashcards and quizzes, track what you actually understand, and adapt to how you learn — all built to run on your own machine.

Not every student has the same computer, so OpenLearn AI comes in **three operating modes**. Some modes need almost no hardware but require the internet. Others run entirely offline but need a stronger computer. You pick the mode that fits the laptop or PC you already own — there's no "wrong" choice, just the one that matches your hardware and your priorities (speed, privacy, or convenience).

This guide will help you answer:
- Can my computer run OpenLearn AI, and which mode should I pick?
- Do I need a GPU or a constant internet connection?
- What will actually feel fast or slow on my machine?
- How much disk space should I set aside?

---

## 2. Which Version Is Right For You?

| Version | Internet Required | Local AI | GPU Required | Recommended For |
|---|---|---|---|---|
| **Cloud Edition** | Yes, always | No | No | Older laptops, Chromebooks, shared lab computers |
| **Hybrid Edition** ⭐ Recommended | Yes, for cloud features | Yes | Optional (speeds up local AI) | Most students — best balance of speed, privacy, and hardware needs |
| **Local AI Edition** | No | Yes, fully | Yes (recommended) | Students who want maximum privacy and full offline study |

> **Good to know:** These aren't three separate programs — it's one app, and switching modes later is just a settings change. You're never locked in.

### Cloud Edition
All AI processing happens through online AI services. Nothing runs on your computer besides the interface, so it's extremely lightweight. Best if your laptop is a few years old, has no dedicated graphics card, or you're on a shared/lab machine.

### Hybrid Edition (Recommended)
Combines a local AI model on your computer with cloud AI for specific tasks. This gives you a strong balance of response quality, privacy (your documents stay local by default), and reasonable hardware requirements. This is the mode most students should start with.

### Local AI Edition
Everything — chat, document analysis, question generation — runs completely offline on your own hardware. Maximum privacy, since nothing ever leaves your machine. Needs the strongest computer of the three modes, ideally with a dedicated GPU.

---

## 3. System Requirements

### 3.1 Cloud Edition

| Component | Minimum | Recommended | Best Experience |
|---|---|---|---|
| CPU | Dual-core Intel/AMD or Apple M-series | Quad-core Intel Core i3/Ryzen 3 or Apple M1 | Any modern CPU (this mode is not CPU-intensive) |
| RAM | 2 GB | 4 GB | 8 GB |
| GPU | None needed | None needed | None needed |
| VRAM | Not applicable | Not applicable | Not applicable |
| Storage | 5 GB free | 5 GB free | 5 GB free |
| Operating System | Windows 10, macOS 12, or Linux (modern distro) | Windows 11, macOS 13+, or Linux | Any current OS with a modern browser |
| Internet | Required, persistent connection | Stable broadband | Stable broadband |

### 3.2 Hybrid Edition (Recommended)

| Component | Minimum | Recommended | Best Experience |
|---|---|---|---|
| CPU | Intel Core i3 / Ryzen 3 | Intel Core i5 / Ryzen 5 | Intel Core i7 / Ryzen 7 or Apple M-series |
| RAM | 4 GB | 8 GB | 16 GB |
| GPU | Not required (integrated graphics OK) | Optional — any entry GPU (e.g., GTX 1650, RTX 3050) speeds up local AI | RTX 4060 or better |
| VRAM | Not applicable | 4 GB+ if using a GPU | 8 GB+ |
| Storage | 10 GB free | 15 GB free | 25 GB free |
| Operating System | Windows 10, macOS 12, or Linux | Windows 11, macOS 13+, or Linux | Windows 11, macOS 14+, or Linux |
| Internet | Required for cloud-assisted features | Stable broadband | Stable broadband |

### 3.3 Local AI Edition

| Component | Minimum | Recommended | Best Experience |
|---|---|---|---|
| CPU | Intel Core i5 / Ryzen 5 | Intel Core i7 / Ryzen 7 | Intel Core i9 / Ryzen 9 or Apple M-series Pro/Max |
| RAM | 8 GB | 16 GB | 32 GB |
| GPU | Integrated graphics (slow) — dedicated GPU strongly recommended | NVIDIA GPU with 8 GB VRAM (e.g., RTX 3050/3060) | RTX 4070 or better |
| VRAM | Not applicable (CPU-only, slow) | 8 GB | 12 GB+ |
| Storage | 20 GB free | 30 GB free | 50 GB+ free (for multiple local AI models) |
| Operating System | Windows 10, macOS 12, or Linux | Windows 11, macOS 13+, or Linux | Windows 11, macOS 14+, or Linux |
| Internet | Not required after setup/download | Not required for daily use | Not required for daily use |

---

## 4. Feature Availability by Version

| Feature | Cloud Edition | Hybrid Edition | Local AI Edition |
|---|---|---|---|
| AI Chat | ✅ | ✅ | ✅ |
| Adaptive Learning (personalized study path) | ✅ | ✅ | ✅ |
| PDF Analysis & Summaries | ✅ | ✅ | ✅ |
| OCR (scanned documents/images) | ✅ | ✅ | ✅ |
| Flashcards | ✅ | ✅ | ✅ |
| Quiz & Exam Generation | ✅ | ✅ | ✅ |
| Study Planner | ✅ | ✅ | ✅ |
| Knowledge Graph (concept map) | ⚠️ Limited | ✅ | ✅ |
| Offline Learning | ❌ | ⚠️ Limited (only local components) | ✅ Full offline |
| Fast Response (streaming answers) | ✅ | ✅ | ⚠️ Depends on your hardware |
| Cloud Intelligence (top-tier AI quality) | ✅ | ✅ | ❌ |

> All three modes deliver the full educational feature set — the difference is *where the AI processing happens* and *whether you need the internet to use it*, not which features you're allowed to use.

---

## 5. Internet Requirements

**Internet is always required — Cloud Edition.** Every AI request (chat, summaries, quiz generation) is sent to an online AI service. If your connection drops, the app won't be able to respond.
- ✅ Advantage: works on almost any device, minimal setup, no large downloads.
- ⚠️ Disadvantage: no offline studying, and your questions/documents pass through an online service.

**Internet is optional — Hybrid Edition.** Local AI on your computer handles core tasks like flashcards and adaptive learning offline. Certain features (e.g., higher-quality answers, some search enhancements) use cloud AI when you're connected, and fall back to your local model when you're not.
- ✅ Advantage: best of both worlds — you can study on a plane, then get an extra quality boost once you're back online.
- ⚠️ Disadvantage: a few features are noticeably better with a connection than without.

**Internet is not required — Local AI Edition.** Once installed and your AI models are downloaded, everything runs on your own computer. You can use it on a flight, in a library with no wifi, or anywhere with zero connectivity.
- ✅ Advantage: complete privacy, full offline access, no dependency on outside services.
- ⚠️ Disadvantage: needs the strongest computer of the three modes, and the initial model download requires internet.

---

## 6. Storage Requirements

Storage needs grow the more local AI you use. Here's what to budget for after installation:

| Usage Level | Application | AI Models | User Documents | Cache | Future Growth | **Total Recommended** |
|---|---|---|---|---|---|---|
| **Minimum** (Cloud Edition) | ~1 GB | 0 GB (cloud-only) | ~1 GB | ~1 GB | ~2 GB | **~5 GB** |
| **Recommended** (Hybrid Edition) | ~1 GB | ~5–8 GB | ~2 GB | ~2 GB | ~3 GB | **~15 GB** |
| **Heavy Usage** (Local AI Edition, multiple models) | ~1 GB | ~15–30 GB | ~5 GB | ~5 GB | ~10 GB | **~50 GB+** |

- **Application** — the core program itself; roughly the same across all modes.
- **AI Models** — only relevant if you use local AI; each local model is several gigabytes, and Local AI Edition may keep more than one installed.
- **User Documents** — your uploaded PDFs, notes, and generated study material.
- **Cache** — temporary files that speed up repeated tasks (safe to clear if space is tight).
- **Future Growth** — headroom for new documents, additional AI models, and app updates.

---

## 7. Performance Expectations

| Computer Type | Startup Speed | AI Response Speed | PDF Processing | OCR Speed | Offline Experience |
|---|---|---|---|---|---|
| **Basic Laptop** (no GPU, 4–8 GB RAM) | Fast | Fast (Cloud/Hybrid) | Fast for text PDFs | Good for clear scans | Cloud/Hybrid only — full offline not recommended |
| **Gaming Laptop** (RTX 3050–3060, 16 GB RAM) | Fast | Fast to Very Fast | Fast, well under a minute for a 100-page document | Fast | Smooth in Hybrid or Local AI mode |
| **Desktop PC** (mid-range GPU, 16–32 GB RAM) | Fast | Very Fast | Very Fast | Very Fast | Smooth, reliable full offline use |
| **AI Workstation** (RTX 4070+, 32 GB+ RAM) | Fast | Near-instant, cloud-level quality locally | Near-instant | Near-instant | Best possible offline experience, multiple models available |

**Rule of thumb:** a well-configured system can summarize and process a 100-page PDF (including scanning/OCR) in about a minute, and a typical AI answer should start appearing within a few seconds. On weaker hardware in Local AI mode, expect noticeably slower responses — this is where Cloud or Hybrid Edition will feel much snappier.

---

## 8. Choosing the Right Version

Use these practical rules to decide:

- **"My laptop has 8 GB RAM and no dedicated GPU."** → Choose **Cloud Edition**. It's the lightest option and will run smoothly.
- **"I have a laptop with 8–16 GB RAM, and I mostly have wifi."** → Choose **Hybrid Edition**. It's the recommended default for most students.
- **"I own a gaming laptop with an RTX 3050 or better."** → Choose **Hybrid Edition**, or step up to **Local AI Edition** if privacy matters to you.
- **"I need maximum privacy and want to study with no internet at all."** → Choose **Local AI Edition**.
- **"I have a desktop or workstation with a high-end GPU (RTX 4070+) and 32 GB+ RAM."** → Choose **Local AI Edition** for the best possible experience — full privacy with near-instant responses.
- **"I'm not sure and just want something that works everywhere."** → Start with **Hybrid Edition**; you can always switch later.

---

## 9. Frequently Asked Questions

**Can I use OpenLearn AI without internet?**
Yes, if you install Local AI Edition. Hybrid Edition works offline for core features but needs internet for cloud-enhanced ones. Cloud Edition requires internet at all times.

**Will it work without a GPU?**
Yes. Cloud Edition doesn't need one at all. Hybrid Edition works fine without a GPU, just a bit slower for local AI tasks. Local AI Edition can technically run on CPU only, but it will be noticeably slow — a GPU is strongly recommended for that mode.

**Can I switch between Cloud and Local later?**
Yes. All three modes are the same underlying app — switching is a configuration change, not a reinstall. You won't lose your documents, notes, or progress when you switch.

**Will my notes remain available offline?**
Yes. Your documents and study materials are stored on your computer regardless of which mode you choose. Only the AI processing (not your data) depends on the mode.

**How much disk space will AI models consume?**
Local AI models typically take up 5–8 GB each. If you install Local AI Edition with multiple models, budget 15–30 GB or more for models alone. Cloud Edition uses no space for AI models since everything runs online.

**Do I need Docker?**
If you use the official installer/desktop build, no — it's handled for you. Advanced users and developers deploying it themselves may use Docker, but this is not required for a standard student installation.

**Can I install it on Windows?**
Yes — Windows 10 or newer is supported across all three editions.

**Can I install it on macOS?**
Yes — macOS 12 or newer is supported, including Apple Silicon (M-series) Macs.

**Can I install it on Linux?**
Yes — any modern Linux distribution is supported across all three editions.

---

## 10. Quick Decision Guide

A one-minute summary to help you decide right now:

- 🟢 **My laptop is old or basic** → Install **Cloud Edition**
- 🟡 **I have a typical laptop with decent wifi** → Install **Hybrid Edition**
- 🔵 **I want complete privacy and offline studying** → Install **Local AI Edition**
- 🔴 **I have a gaming PC or workstation** → Install **Local AI Edition** and enable all local AI features for the best experience

Still unsure? **Hybrid Edition** is the safest starting point for most students — you can always change modes later without losing any of your work.

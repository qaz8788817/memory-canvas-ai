# 🗺️ Memory Canvas AI - Travel Diary & Asset Optimizer

> **A Multimodal Desktop Companion to Generate Social Media Copywriting, Structured SEO Alt Tags, and Automated Filename Refactoring from Travel Images.**

Memory Canvas AI is an artisanal desktop application crafted for developers, travelers, and bloggers to bridge the gap between raw photography and structured asset production. Powered by **Gemini 2.5 Flash's Multimodal Vision API**, it instantly analyzes any travel photo—deciphering landmarks, aesthetics, and cultural contexts. It generates three distinct contextual copywriting personas while concurrently outputting standardized SEO asset metadata and filename rewrites.

---

## ✨ Key Features

* **👁️ Multimodal Visual Storytelling**: Toss any native JPEG/PNG/WebP into the viewport. Gemini dynamically evaluates pixel matrices to recognize locations (e.g., *Hida-no-Sato*) and cultural metadata without manual tags.
* **✍️ Persona-Driven Copywriting Slots**: Automatically curates three high-fidelity text blocks tailored for immediate social publishing: *Poetic Handwritten (文青手寫風)*, *Geek Humorous (幽默極客風)*, and *Travel Guide (旅遊小助手風)*.
* **⚙️ Automated I/O Asset Refactoring**: Generates search-engine-optimized lowercase snake_case filenames and clean structured markup strings (e.g., `alt="Hida-no-Sato-9"`), pairing them with an integrated Pillow cross-format saving workflow.
* **🎨 Scrollable Textbox Interceptors**: Replaces standard rigid text labels with zero-border read-only `CTkTextbox` canvases, providing seamless word-wrapping for artistic script typography while enabling hassle-free clip-board copying.

---

## 🛠️ Tech Stack & Dependencies

* **GUI Foundation**: `CustomTkinter` (Python 3.10+) - Tailored layout configuration.
* **Vision & JSON Inference**: `google-genai` (2025 Next-Gen SDK Framework)
* **Model Pipeline**: `gemini-2.5-flash` (Utilizing vision config arrays and strict Pydantic parsing at a high-expressive 0.6 temperature)
* **Imaging System**: `Pillow` (PIL Fork) with reactive alpha-channel error routing.

---

## 🚀 Getting Started

### Prerequisites

Initialize your workspace with modern graphical and visual processing frameworks:

```bash
pip install customtkinter google-genai Pillow pydantic
```

---

## 介面
<img width="1271" height="772" alt="image" src="https://github.com/user-attachments/assets/3180f27f-e8ef-4f24-8f00-c4b2def733f8" />

# 📚 DocuVerse — The Ultimate Document Toolkit

> A modern, cross-platform desktop application for document conversion, OCR, text editing, and file compression — all in one clean dark-mode interface.

---

## 📌 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tools & Technologies](#tools--technologies)
- [Setup & Installation](#setup--installation)
- [Running the App](#running-the-app)
- [Backend / Module Explanation](#backend--module-explanation)
- [Contribution Credits](#contribution-credits)
- [Major PRs & Issues](#major-prs--issues)

---

## About the Project

**DocuVerse** is a Python-based desktop GUI application built with **CustomTkinter**. It brings together 10 powerful document tools under one roof — accessible from a clean home dashboard. Each tool opens in its own popup window, making the workflow fast and distraction-free.

No internet connection is required. All processing happens **100% locally** on your machine.

---

## Features

| # | Tool | Description |
|---|------|-------------|
| 1 | 📄 **Word → PDF** | Convert `.docx` Word documents to PDF format |
| 2 | 📝 **PDF → Word** | Convert PDF files into editable `.docx` documents |
| 3 | 📊 **PDF → PPTX** | Turn PDF pages into editable PowerPoint slides |
| 4 | 📊 **PPTX → PDF** | Export PowerPoint presentations as PDF files |
| 5 | 📋 **Word → PPTX** | Convert Word documents into PowerPoint presentations |
| 6 | 📑 **PPTX → Word** | Extract slide content into a Word document |
| 7 | 🔍 **OCR: Image → Text** | Extract text from images using AI-powered OCR (14 languages supported) |
| 8 | ✨ **Text Editor** | Rich text editor with fonts, colours, highlights, find & replace |
| 9 | 🗜️ **File Compressor** | Compress multiple files into a single `.zip` archive |
| 10 | 🖼️ **Image Compressor** | Reduce image file size with quality and dimension controls |

**Additional highlights:**
- 🏠 Home dashboard with card-based tool selection
- 🌗 Light / Dark mode toggle
- 📂 Sidebar navigation for quick tool switching
- 🔄 Live progress bars and status indicators
- 🪟 Each tool opens in a focused modal popup window

---

## Screenshots

### 🏠 Home Dashboard
![Home Dashboard](screenshots/01_dashboard.png)

### 📄 Word → PDF Converter
![Word to PDF](screenshots/02_word_to_pdf.png)

### 📝 PDF → Word Converter
![PDF to Word](screenshots/03_pdf_to_word.png)

### 📊 PDF → PPTX Converter
![PDF to PPTX](screenshots/04_pdf_to_pptx.png)

### 📊 PPTX → PDF Converter
![PPTX to PDF](screenshots/05_pptx_to_pdf.png)

### 📋 Word → PPTX Converter
![Word to PPTX](screenshots/06_word_to_pptx.png)

### 📑 PPTX → Word Converter
![PPTX to Word](screenshots/07_pptx_to_word.png)

### 🔍 OCR: Image → Text Extractor
![OCR Tool](screenshots/08_ocr.png)

### ✨ Text Editor
![Text Editor](screenshots/09_text_editor.png)

### 🗜️ File Compressor
![File Compressor](screenshots/10_file_compressor.png)

### 🖼️ Image Compressor
![Image Compressor](screenshots/11_image_compressor.png)

---

## Tools & Technologies

### Language & GUI
| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core programming language |
| **CustomTkinter** | Modern dark-mode GUI framework |
| **Tkinter** | Underlying GUI toolkit (built into Python) |

### Document Processing Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| `customtkinter` | ≥5.2.0 | GUI widgets and theming |
| `docx2pdf` | 0.1.8 | Word → PDF conversion |
| `pypandoc` | 1.13 | Document format conversion |
| `pdf2docx` | 0.5.8 | PDF → Word conversion |
| `PyMuPDF` | 1.24.5 | PDF rendering and manipulation |
| `python-pptx` | 0.6.23 | PowerPoint file creation and editing |
| `python-docx` | 1.1.2 | Word document reading and writing |
| `pdfkit` | 1.0.0 | PDF generation |
| `reportlab` | 4.2.0 | PDF creation from scratch |
| `easyocr` | 1.7.1 | AI-powered OCR (primary engine) |
| `pytesseract` | 0.3.10 | OCR fallback engine |
| `Pillow` | ≥10.0.0 | Image processing and compression |

---

## Setup & Installation

### Prerequisites

- Python **3.10 or higher**
- `pip` package manager
- For OCR: `tesseract-ocr` system package
- For Word→PDF on Linux: `LibreOffice` installed

### 1. Clone the Repository

bash
git clone https://github.com/your-username/docuverse.git
cd docuverse


### 2. Create a Virtual Environment (Recommended)

bash
python -m venv venv


source venv/bin/activate


venv\Scripts\activate


### 3. Install Python Dependencies

bash
pip install -r requirements.txt


### 4. Install System Dependencies

**On Ubuntu/Debian Linux:**
bash
# For OCR (pytesseract)
sudo apt install tesseract-ocr

# For Word → PDF conversion
sudo apt install libreoffice

# For wkhtmltopdf (pdfkit)
sudo apt install wkhtmltopdf


**On Windows:**
- Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- Install [LibreOffice](https://www.libreoffice.org/download/download/)
- Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

**On macOS:**
bash
brew install tesseract
brew install libreoffice
brew install wkhtmltopdf


---

## Running the App

bash
python main.py


The app will launch with the **Home Dashboard** showing all 10 tools as clickable cards. Click any card to open that tool in a popup window. You can also use the **sidebar** on the left to navigate directly to any tool.

---

## Backend / Module Explanation

The project is organized into a `tools/` package where each module handles one conversion type independently:


docuverse/
│
├── main.py                  # Main application entry point — all GUI frames & App class
│
├── tools/
│   ├── __init__.py
│   ├── word_pdf.py          # Word ↔ PDF conversion logic (docx2pdf, pdf2docx)
│   ├── pdf_pptx.py          # PDF → PPTX using PyMuPDF + python-pptx
│   ├── word_pptx.py         # Word → PPTX using python-docx + python-pptx
│   ├── pptx_word.py         # PPTX → Word using python-pptx + python-docx
│   ├── ocr.py               # OCR using easyocr (primary) + pytesseract (fallback)
│   ├── file_compressor.py   # ZIP archive creation using Python's zipfile module
│   ├── image_compressor.py  # Image resizing & quality reduction using Pillow
│   └── dialogs.py           # Shared popup dialog helpers (error, success, info)
│
├── requirements.txt
└── README.md


### How Each Module Works

**`word_pdf.py`**
Uses `docx2pdf` (which calls LibreOffice under the hood on Linux/macOS) to convert `.docx` → `.pdf`. For the reverse direction, `pdf2docx` parses PDF structure and reconstructs a Word document.

**`pdf_pptx.py`**
Uses `PyMuPDF` (fitz) to render each PDF page as an image, then inserts those images as slides into a new `.pptx` file via `python-pptx`.

**`word_pptx.py` / `pptx_word.py`**
Reads content (headings, paragraphs, tables) using `python-docx` or `python-pptx` and reconstructs it in the target format.

**`ocr.py`**
Attempts text extraction using `easyocr` first (deep-learning based, supports 14 languages). Falls back to `pytesseract` if easyocr fails. Returns plain text output.

**`file_compressor.py`**
Uses Python's built-in `zipfile` module to compress a list of selected files into a single `.zip` archive with a progress callback.

**`image_compressor.py`**
Uses `Pillow` to open the image, optionally resize it to a max dimension, then save with a reduced JPEG quality value. PNG files are saved with optimized compression.

**`dialogs.py`**
Provides `show_error()`, `show_success()`, and `show_info()` helper functions that create styled `CTkToplevel` popup dialogs, keeping dialog code out of the tool frames.

All tool functions accept an optional `progress_cb(pct: int, msg: str)` callback so the GUI can update the progress bar and status label in real time without blocking the UI thread.

---

## Contribution Credits

| Team Member | Role & Contributions |
|-------------|---------------------|
| **[Member 1]** | Project lead, `main.py` GUI architecture, `WordToPdfFrame`, `PdfToWordFrame`, `PptxToPdfFrame` |
| **[Member 2]** | `word_pptx.py`, `pptx_word.py`, `WordToPptxFrame`, `PptxToWordFrame` tool modules |
| **[Member 3]** | `ocr.py` OCR engine integration, `OcrImageTextFrame`, multi-language support |
| **[Member 4]** | `TextEditorFrame` rich text editor, find & highlight, font/colour controls |
| **[Member 5]** | `file_compressor.py`, `image_compressor.py`, `FileCompressorFrame`, `ImageCompressorFrame` |
| **[Member 6]** | `HomeDashboardFrame` design, popup modal system, sidebar navigation, UI polish |

> ℹ️ Replace the placeholders above with your actual team members' names and GitHub usernames.

---

## Major PRs & Issues

> ℹ️ Replace the links below with your actual GitHub PR and issue URLs.

### Pull Requests

| PR | Title | Author |
|----|-------|--------|
| [#1](https://github.com/your-username/docuverse/pull/1) | Initial project structure and base GUI | Member 1 |
| [#2](https://github.com/your-username/docuverse/pull/2) | Add Word ↔ PDF conversion | Member 1 |
| [#3](https://github.com/your-username/docuverse/pull/3) | Add PDF → PPTX and PPTX → Word tools | Member 2 |
| [#4](https://github.com/your-username/docuverse/pull/4) | OCR module with easyocr + pytesseract | Member 3 |
| [#5](https://github.com/your-username/docuverse/pull/5) | Rich Text Editor with font and colour controls | Member 4 |
| [#6](https://github.com/your-username/docuverse/pull/6) | File and Image Compressor tools | Member 5 |
| [#7](https://github.com/your-username/docuverse/pull/7) | Home Dashboard + popup modal system | Member 6 |

### Issues

| Issue | Title | Status |
|-------|-------|--------|
| [#1](https://github.com/your-username/docuverse/issues/1) | Setup project repository and agree on architecture | ✅ Closed |
| [#2](https://github.com/your-username/docuverse/issues/2) | Word→PDF fails on Linux without LibreOffice | ✅ Closed |
| [#3](https://github.com/your-username/docuverse/issues/3) | OCR language selector not updating engine | ✅ Closed |
| [#4](https://github.com/your-username/docuverse/issues/4) | Progress bar not resetting after failed conversion | ✅ Closed |
| [#5](https://github.com/your-username/docuverse/issues/5) | Add Home Dashboard screen with card grid | ✅ Closed |

<p align="center">Made with ❤️ by the DocuVerse Team · UMT OSSID Project 2026</p>

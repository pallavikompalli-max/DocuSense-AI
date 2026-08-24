# 📄 DocuSense AI

## Intelligent Document Analysis & Summarization

DocuSense AI is an AI-powered document analysis application that allows users to upload PDF documents and images, extract their content, generate intelligent summaries, and ask questions about their documents.

## 🚀 Features

- 📄 PDF text extraction
- 🖼️ Image OCR using Tesseract
- 🤖 AI-powered summarization using Google Gemini
- 📏 Short, Medium and Long summaries
- 🔑 Executive Summary, Key Points and Main Ideas
- 💬 Ask questions about uploaded documents
- 📊 Document statistics and insights
- 📚 Document history
- 🔍 Search previous documents
- ⬇️ Download generated summaries
- 🗑️ Delete document history
- 💾 SQLite database
- 🛡️ Gemini retry and fallback handling

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- PyMuPDF
- Tesseract OCR
- Pytesseract
- Pillow
- SQLite
- python-dotenv

## 🏗️ System Workflow

```text
Upload PDF / Image
        ↓
Document Extraction
        ↓
OCR for Images
        ↓
Extracted Text
        ↓
Gemini AI
        ↓
AI Summary
        ↓
Key Points + Main Ideas
        ↓
Ask Questions / Download / History
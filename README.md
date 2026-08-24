# 📄 DocuSense AI

<div align="center">

### 🤖 Intelligent Document Analysis & AI-Powered Summarization

**Upload. Extract. Summarize. Ask. Understand.**

An AI-powered document analysis application built with **Python, Streamlit, Google Gemini, PDF Processing, OCR, and SQLite**.

<br>

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit)
![Gemini](https://img.shields.io/badge/Google-Gemini_AI-orange?style=for-the-badge&logo=google)
![OCR](https://img.shields.io/badge/OCR-Tesseract-green?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/License-Educational-lightgrey?style=for-the-badge)

</div>

---

# 📑 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Proposed Solution](#-proposed-solution)
- [Objectives](#-objectives)
- [Key Features](#-key-features)
- [How the Application Works](#-how-the-application-works)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Application Modules](#-application-modules)
- [AI Summarization](#-ai-summarization)
- [OCR Processing](#-ocr-processing)
- [Document Question Answering](#-document-question-answering)
- [Document History](#-document-history)
- [Document Insights](#-document-insights)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Example Workflow](#-example-workflow)
- [Use Cases](#-use-cases)
- [Advantages](#-advantages)
- [Limitations](#-limitations)
- [Future Enhancements](#-future-enhancements)
- [Learning Outcomes](#-learning-outcomes)
- [Security](#-security)
- [Screenshots](#-screenshots)
- [Author](#-author)
- [Repository](#-repository)

---

# 🔎 Overview

**DocuSense AI** is an intelligent document analysis and summarization
application designed to help users understand lengthy documents quickly.

The application allows users to upload **PDF files and images**, extract
their textual content, process the extracted information using
**Google Gemini AI**, and generate structured summaries.

In addition to summarization, DocuSense AI provides an interactive
**Ask This Document** feature that allows users to ask questions about
the uploaded content.

The application also maintains a **document history** using SQLite,
provides document statistics, and allows generated summaries to be
downloaded.

---

# ❗ Problem Statement

Modern users frequently work with large amounts of digital information.

Students, researchers, developers, and professionals may need to read
lengthy:

- 📄 PDF documents
- 📚 Academic materials
- 📝 Assignments
- 🔬 Research documents
- 💼 Reports
- 💻 Technical documentation
- 🖼️ Scanned documents

Reading an entire document manually can require significant time and
effort.

Important information may also be difficult to identify when it is
distributed across many pages.

### Major challenges include:

1. ⏳ High reading time
2. 🔍 Difficulty finding important information
3. 📚 Large amounts of textual content
4. 🧠 Difficulty understanding complex documents
5. 🔄 Repeated manual document review
6. 🖼️ Difficulty processing scanned/image-based documents
7. ❓ Difficulty asking questions about specific document content

---

# 💡 Proposed Solution

DocuSense AI provides a single platform that combines:

```text
Document Upload
       ↓
Text Extraction
       ↓
OCR Processing
       ↓
Document Analysis
       ↓
Gemini AI
       ↓
Structured Summary
       ↓
Document Questions
       ↓
History & Download

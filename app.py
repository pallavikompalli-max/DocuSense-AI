import streamlit as st
import fitz
import pytesseract
from PIL import Image
from io import BytesIO
import os
import sqlite3
import time
from datetime import datetime

from dotenv import load_dotenv
from google import genai


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="DocuSense AI",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# GEMINI CONFIGURATION
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "❌ GEMINI_API_KEY was not found.\n\n"
        "Please check your .env file."
    )
    st.stop()


client = genai.Client(
    api_key=api_key
)


# =========================================================
# TESSERACT OCR CONFIGURATION
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# DATABASE
# =========================================================

DB_NAME = "document_history.db"


def init_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT,
            summary_length TEXT,
            summary TEXT,
            word_count INTEGER,
            uploaded_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_database()


# =========================================================
# SAVE DOCUMENT
# =========================================================

def save_document(
    filename,
    file_type,
    summary_length,
    summary,
    word_count
):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents
        (
            filename,
            file_type,
            summary_length,
            summary,
            word_count,
            uploaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            filename,
            file_type,
            summary_length,
            summary,
            word_count,
            datetime.now().strftime(
                "%d %b %Y, %I:%M %p"
            )
        )
    )

    conn.commit()
    conn.close()


# =========================================================
# GET DOCUMENT HISTORY
# =========================================================

def get_documents():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            filename,
            file_type,
            summary_length,
            summary,
            word_count,
            uploaded_at
        FROM documents
        ORDER BY id DESC
        """
    )

    documents = cursor.fetchall()

    conn.close()

    return documents


# =========================================================
# DELETE ONE DOCUMENT
# =========================================================

def delete_document(document_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM documents WHERE id = ?",
        (document_id,)
    )

    conn.commit()
    conn.close()


# =========================================================
# CLEAR HISTORY
# =========================================================

def clear_history():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM documents"
    )

    conn.commit()
    conn.close()


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(uploaded_file):

    pdf_bytes = uploaded_file.getvalue()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = ""

    for page in document:

        text += page.get_text()

        text += "\n"

    document.close()

    return text


# =========================================================
# IMAGE OCR
# =========================================================

def extract_image_text(uploaded_file):

    image = Image.open(
        BytesIO(
            uploaded_file.getvalue()
        )
    )

    text = pytesseract.image_to_string(
        image
    )

    return text


# =========================================================
# GEMINI REQUEST WITH RETRY + FALLBACK
# =========================================================

def call_gemini(prompt):

    models = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash"
    ]

    last_error = None

    for model in models:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response and response.text:

                    return response.text

                raise Exception(
                    "Gemini returned an empty response."
                )

            except Exception as error:

                last_error = error

                error_text = str(error)

                # Retry temporary server problems
                if (
                    "503" in error_text
                    or
                    "UNAVAILABLE" in error_text
                    or
                    "high demand" in error_text.lower()
                    or
                    "temporarily" in error_text.lower()
                ):

                    if attempt < 2:

                        wait_time = 2 ** attempt

                        time.sleep(
                            wait_time
                        )

                        continue

                    # Move to next model
                    break

                # Other errors should not be retried
                break

    raise Exception(
        "Gemini is temporarily unavailable. "
        "Please try again in a few seconds.\n\n"
        f"Details: {last_error}"
    )


# =========================================================
# GENERATE SUMMARY
# =========================================================

def generate_summary(text, length):

    prompt = f"""
You are DocuSense AI, an intelligent document
summarization assistant.

Read the document carefully and create a useful,
accurate summary.

SUMMARY LENGTH:
{length}

Use exactly these sections:

## 📝 Executive Summary

Give a clear overall explanation of the document.

## 🔑 Key Points

Give the most important points as bullet points.

## 💡 Main Ideas

Explain the major ideas or concepts.

IMPORTANT RULES:

1. Use only information present in the document.
2. Do not invent facts.
3. Do not make assumptions.
4. Remove unnecessary repetition.
5. Preserve important names, numbers,
   technologies and technical terms.
6. If the document contains programming code,
   explain what the code does instead of copying
   large sections of code.
7. Keep the explanation easy to understand.
8. Follow the requested summary length.

DOCUMENT:

{text}
"""

    return call_gemini(prompt)


# =========================================================
# ASK THIS DOCUMENT
# =========================================================

def ask_document(text, question):

    prompt = f"""
You are DocuSense AI.

Answer the user's question using ONLY the
information contained in the document.

If the answer cannot be found in the document,
respond:

"The document does not contain enough information
to answer this question."

Do not invent information.

Keep the answer clear and concise.

DOCUMENT:

{text}

QUESTION:

{question}
"""

    return call_gemini(prompt)


# =========================================================
# GET DASHBOARD STATISTICS
# =========================================================

documents = get_documents()

total_documents = len(documents)

total_words = sum(
    (doc[5] or 0)
    for doc in documents
)

total_summaries = len(documents)

total_reading_time = round(
    total_words / 200
)


# =========================================================
# HEADER
# =========================================================

st.title("📄 DocuSense AI")

st.subheader(
    "Intelligent Document Analysis & Summarization"
)

st.write(
    "Upload PDFs or images, extract their content, "
    "generate AI summaries and ask questions "
    "about your documents."
)

st.divider()


# =========================================================
# DASHBOARD
# =========================================================

st.subheader(
    "📊 Your Document Dashboard"
)

d1, d2, d3, d4 = st.columns(4)


with d1:

    st.metric(
        "📄 Documents",
        total_documents
    )


with d2:

    st.metric(
        "🔤 Words Processed",
        f"{total_words:,}"
    )


with d3:

    st.metric(
        "🤖 AI Summaries",
        total_summaries
    )


with d4:

    st.metric(
        "📖 Reading Time",
        f"{total_reading_time} min"
    )


# =========================================================
# FEATURES
# =========================================================

st.subheader(
    "✨ What DocuSense AI Can Do"
)

f1, f2, f3 = st.columns(3)


with f1:

    with st.container(border=True):

        st.markdown(
            "### 📄 Document Extraction"
        )

        st.write(
            "Extract text from PDFs and images "
            "using PDF parsing and OCR."
        )


with f2:

    with st.container(border=True):

        st.markdown(
            "### 🤖 AI Summarization"
        )

        st.write(
            "Generate short, medium or long "
            "intelligent document summaries."
        )


with f3:

    with st.container(border=True):

        st.markdown(
            "### 💬 Ask Your Document"
        )

        st.write(
            "Ask questions and receive answers "
            "based on your uploaded content."
        )


st.divider()


# =========================================================
# TABS
# =========================================================

tab1, tab2 = st.tabs(
    [
        "📄 Analyze Document",
        "📚 Document History"
    ]
)


# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.subheader(
        "📤 Upload & Analyze"
    )

    st.info(
        "Supported formats: PDF, PNG, JPG and JPEG"
    )

    uploaded_file = st.file_uploader(
        "Choose your document",
        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg"
        ]
    )


    # =====================================================
    # DOCUMENT UPLOADED
    # =====================================================

    if uploaded_file:

        st.success(
            f"📥 Uploaded: {uploaded_file.name}"
        )


        # =================================================
        # EXTRACT TEXT
        # =================================================

        try:

            with st.spinner(
                "🔍 Extracting document content..."
            ):

                if uploaded_file.type == "application/pdf":

                    text = extract_pdf_text(
                        uploaded_file
                    )

                else:

                    text = extract_image_text(
                        uploaded_file
                    )

        except Exception as error:

            st.error(
                "❌ Could not extract text from "
                "this document."
            )

            st.code(
                str(error)
            )

            st.stop()


        # =================================================
        # CHECK TEXT
        # =================================================

        if not text.strip():

            st.warning(
                "⚠️ No readable text was found."
            )

            st.info(
                "For images, make sure the text is "
                "clear and readable."
            )

            st.stop()


        # =================================================
        # EXTRACTED TEXT
        # =================================================

        st.subheader(
            "📄 Extracted Text"
        )

        with st.expander(
            "👁️ View extracted text"
        ):

            st.text_area(
                "Document Content",
                text,
                height=300
            )


        # =================================================
        # DOCUMENT INSIGHTS
        # =================================================

        st.subheader(
            "📊 Document Insights"
        )

        word_count = len(
            text.split()
        )

        character_count = len(
            text
        )

        reading_time = max(
            1,
            round(
                word_count / 200
            )
        )


        i1, i2, i3, i4 = st.columns(4)


        with i1:

            file_extension = (
                uploaded_file.name
                .split(".")[-1]
                .upper()
            )

            st.metric(
                "📄 File Type",
                file_extension
            )


        with i2:

            st.metric(
                "🔤 Words",
                f"{word_count:,}"
            )


        with i3:

            st.metric(
                "🔢 Characters",
                f"{character_count:,}"
            )


        with i4:

            st.metric(
                "📖 Reading Time",
                f"{reading_time} min"
            )


        # =================================================
        # AI SUMMARY
        # =================================================

        st.subheader(
            "🤖 AI Summary"
        )

        summary_length = st.selectbox(
            "Choose summary length",
            [
                "Short",
                "Medium",
                "Long"
            ]
        )


        if st.button(
            "✨ Generate AI Summary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "🤖 Gemini is analyzing your document..."
                ):

                    summary = generate_summary(
                        text,
                        summary_length
                    )


                # =========================================
                # ONLY SHOW SUCCESS IF GEMINI WORKED
                # =========================================

                st.success(
                    "✅ Summary generated successfully!"
                )


                st.markdown(
                    "### 📝 Summary"
                )

                st.markdown(
                    summary
                )


                # =========================================
                # SAVE REAL SUMMARY TO HISTORY
                # =========================================

                save_document(
                    uploaded_file.name,
                    uploaded_file.type,
                    summary_length,
                    summary,
                    word_count
                )


                st.success(
                    "📚 Document saved to History!"
                )


                # =========================================
                # DOWNLOAD
                # =========================================

                st.download_button(
                    "⬇️ Download Summary",
                    summary,
                    file_name=(
                        uploaded_file.name
                        + "_summary.txt"
                    ),
                    mime="text/plain",
                    use_container_width=True
                )


            except Exception as error:

                st.error(
                    "⚠️ Gemini is temporarily "
                    "unavailable."
                )

                st.info(
                    "Please wait a few seconds "
                    "and click Generate AI Summary again."
                )


        # =================================================
        # ASK THIS DOCUMENT
        # =================================================

        st.divider()

        st.subheader(
            "💬 Ask This Document"
        )

        st.write(
            "Ask a question about the "
            "uploaded document."
        )


        question = st.text_input(
            "Your question",
            placeholder=(
                "Example: What are the main "
                "technologies used?"
            )
        )


        if st.button(
            "💬 Ask AI",
            use_container_width=True
        ):

            if not question.strip():

                st.warning(
                    "Please enter a question first."
                )

            else:

                try:

                    with st.spinner(
                        "🤖 Reading the document..."
                    ):

                        answer = ask_document(
                            text,
                            question
                        )


                    st.success(
                        "✅ Answer generated!"
                    )


                    st.markdown(
                        "### 🤖 AI Answer"
                    )

                    st.write(
                        answer
                    )


                except Exception:

                    st.error(
                        "⚠️ Gemini is temporarily "
                        "unavailable."
                    )

                    st.info(
                        "Please wait a few seconds "
                        "and try again."
                    )


# =========================================================
# TAB 2 — DOCUMENT HISTORY
# =========================================================

with tab2:

    st.subheader(
        "📚 Document History"
    )

    documents = get_documents()


    if documents:

        h1, h2 = st.columns(
            [4, 1]
        )


        with h1:

            st.write(
                f"**{len(documents)} "
                f"document(s) processed**"
            )


        with h2:

            if st.button(
                "🗑️ Clear All"
            ):

                clear_history()

                st.rerun()


        # =================================================
        # SEARCH
        # =================================================

        search = st.text_input(
            "🔍 Search your documents",
            placeholder=(
                "Search by filename or summary..."
            )
        )


        filtered_documents = []


        for document in documents:

            filename = document[1]

            summary = document[4]


            if (
                search.lower()
                in filename.lower()
                or
                search.lower()
                in summary.lower()
            ):

                filtered_documents.append(
                    document
                )


        # =================================================
        # DISPLAY HISTORY
        # =================================================

        if filtered_documents:

            for document in filtered_documents:

                document_id = document[0]

                filename = document[1]

                file_type = document[2]

                summary_length = document[3]

                summary = document[4]

                word_count = document[5] or 0

                uploaded_at = document[6]


                with st.expander(
                    f"📄 {filename} • {uploaded_at}"
                ):

                    c1, c2, c3 = st.columns(3)


                    with c1:

                        st.write(
                            f"**Type:** {file_type}"
                        )


                    with c2:

                        st.write(
                            f"**Length:** "
                            f"{summary_length}"
                        )


                    with c3:

                        st.write(
                            f"**Words:** "
                            f"{word_count:,}"
                        )


                    st.divider()


                    st.markdown(
                        "### 📝 Summary"
                    )

                    st.markdown(
                        summary
                    )


                    b1, b2 = st.columns(2)


                    with b1:

                        st.download_button(
                            "⬇️ Download",
                            summary,
                            file_name=(
                                filename
                                + "_summary.txt"
                            ),
                            mime="text/plain",
                            key=(
                                "download_"
                                + str(document_id)
                            ),
                            use_container_width=True
                        )


                    with b2:

                        if st.button(
                            "🗑️ Delete",
                            key=(
                                "delete_"
                                + str(document_id)
                            ),
                            use_container_width=True
                        ):

                            delete_document(
                                document_id
                            )

                            st.rerun()


        else:

            st.info(
                "🔍 No documents match your search."
            )


    else:

        st.info(
            "📚 No documents yet. "
            "Upload a document to get started."
        )
        


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📄 DocuSense AI • "
    "Powered by Gemini AI • "
    "PDF Parsing • Tesseract OCR • SQLite"
)
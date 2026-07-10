import os
import json
import fitz
import psycopg2
from groq import Groq
from llama_index.core import Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from core.config import SUPABASE_CONNECTION_STRING, OPENAI_API_KEY, GROQ_API_KEY
from core.chapters import get_chapter_for_page, is_page_excluded, get_printed_page_number

PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "Human_Communication_Disorders.pdf")

llm_client = Groq(api_key=GROQ_API_KEY)

FILTER_PROMPT = """You are reviewing text chunks extracted from a Speech-Language Pathology textbook for a clinical knowledge base.

A chunk is USABLE if it contains a complete clinical explanation, definition, clinical case study (patient symptoms/diagnosis/treatment), or therapeutic information a student could learn from.

A chunk is JUNK if it is:
- A bibliography or reference list entry, even a short one embedded inside normal chapter text (author names, years, journal/book titles, publisher names)
- A bare figure/table caption with no surrounding explanation
- Just a page number alone
- A cut-off sentence fragment that doesn't form a complete thought
- A transcription excerpt with no context explaining what it demonstrates
- A personal narrative or biographical essay about an author's own career, life story, or background. These almost always start with or contain the heading "personal PERSPECTIVE" followed by a person's name, and describe the author's personal journey rather than clinical/scientific content.
- A chapter title page containing only the chapter title, author name(s), and university/institutional affiliation, with no actual subject content

Be strict: if a chunk's main content is a person's name, title, and affiliation with little or no clinical explanation, mark it JUNK even if it mentions the chapter topic. If you see the words "personal PERSPECTIVE" anywhere in the text, mark it JUNK immediately regardless of what follows.

Respond with EXACTLY one word: USABLE or JUNK. Nothing else."""


def is_already_ingested():
    conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM public.documents;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0


def classify_chunk(chunk_text: str) -> str:
    """Returns USABLE or JUNK using Groq LLaMA."""
    try:
        response = llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": FILTER_PROMPT},
                {"role": "user", "content": chunk_text}
            ],
            temperature=0,
            max_tokens=10
        )
        verdict = response.choices[0].message.content.strip().upper()
        return "JUNK" if "JUNK" in verdict else "USABLE"
    except Exception:
        return "USABLE"


def load_and_semantic_chunk_pdf():
    print(f"Extracting pages from: {PDF_PATH}")

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found at: {PDF_PATH}")

    doc_stream = fitz.open(PDF_PATH)
    llama_documents = []
    skipped_excluded_pages = 0

    for page_idx in range(len(doc_stream)):
        pdf_page_number = page_idx + 1

        if is_page_excluded(pdf_page_number):
            skipped_excluded_pages += 1
            continue

        page = doc_stream.load_page(page_idx)
        page_text = page.get_text("text")

        if page_text and page_text.strip():
            chapter_name = get_chapter_for_page(pdf_page_number)
            printed_page = get_printed_page_number(pdf_page_number)

            doc = Document(
                text=page_text,
                metadata={
                    "book_title": "Human Communication Disorders",
                    "page_number": printed_page,
                    "chapter": chapter_name,
                    "doi": "10.1016/slp-resource"
                }
            )
            llama_documents.append(doc)

    print(f"Extracted {len(llama_documents)} valid pages.")
    print(f"Skipped {skipped_excluded_pages} pages (references/index).")

    print("Running semantic chunking...")
    embed_model = OpenAIEmbedding(model="text-embedding-ada-002", api_key=OPENAI_API_KEY)
    splitter = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        embed_model=embed_model
    )

    nodes = splitter.get_nodes_from_documents(llama_documents)
    print(f"Generated {len(nodes)} semantic chunks.")
    return nodes, embed_model


def upload_to_supabase(nodes, embed_model):
    print(f"Filtering and uploading {len(nodes)} chunks to Supabase...")

    kept_count = 0
    junk_count = 0

    conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
    cursor = conn.cursor()

    for idx, node in enumerate(nodes):
        content = node.get_content()

        if len(content.strip()) < 100:
            junk_count += 1
            continue

        verdict = classify_chunk(content)

        if verdict == "JUNK":
            junk_count += 1
            continue

        embedding = embed_model.get_text_embedding(content)

        metadata_dict = {
            "book_title": node.metadata.get("book_title"),
            "page_number": node.metadata.get("page_number"),
            "chapter": node.metadata.get("chapter"),
            "doi": node.metadata.get("doi")
        }

        try:
            query = """
                INSERT INTO public.documents (content, embedding, metadata)
                VALUES (%s, %s, %s);
            """
            cursor.execute(query, (content, embedding, json.dumps(metadata_dict)))
            kept_count += 1
        except Exception as e:
            print(f"  Insert failed for chunk {idx}, reconnecting... ({str(e)})")
            conn.rollback()
            cursor.close()
            conn.close()
            conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
            cursor = conn.cursor()
            continue

        if idx % 50 == 0 and idx > 0:
            conn.commit()
            print(f"  Progress: {idx}/{len(nodes)} chunks processed... ({kept_count} kept, {junk_count} junk)")

        if idx % 200 == 0 and idx > 0:
            print("  Refreshing database connection...")
            cursor.close()
            conn.close()
            conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
            cursor = conn.cursor()

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Ingestion complete. {kept_count} chunks stored, {junk_count} chunks filtered out as junk.")


if __name__ == "__main__":
    try:
        if is_already_ingested():
            print("Data already exists in Supabase. Skipping ingestion.")
            print("To re-ingest, clear the table first: TRUNCATE TABLE public.documents;")
        else:
            nodes, embed_model = load_and_semantic_chunk_pdf()
            upload_to_supabase(nodes, embed_model)
    except Exception as e:
        print(f"Ingestion failed: {str(e)}")
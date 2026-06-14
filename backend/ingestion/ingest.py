import os
import json
import fitz
import psycopg2
from llama_index.core import Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from core.config import SUPABASE_CONNECTION_STRING, OPENAI_API_KEY

PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "Human_Communication_Disorders.pdf")


def is_already_ingested():
    conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM public.documents;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0


def load_and_semantic_chunk_pdf():
    print(f"Extracting pages from: {PDF_PATH}")

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found at: {PDF_PATH}")

    doc_stream = fitz.open(PDF_PATH)
    llama_documents = []

    for page_idx in range(len(doc_stream)):
        page = doc_stream.load_page(page_idx)
        page_text = page.get_text("text")
        page_number = page_idx + 1

        if page_text and page_text.strip():
            doc = Document(
                text=page_text,
                metadata={
                    "book_title": "Human Communication Disorders",
                    "page_number": page_number,
                    "doi": "10.1016/slp-resource"
                }
            )
            llama_documents.append(doc)

    print(f"Extracted {len(llama_documents)} valid pages.")

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
    print("Connecting to Supabase...")

    conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
    cursor = conn.cursor()

    print(f"Uploading {len(nodes)} chunks to Supabase...")
    for idx, node in enumerate(nodes):
        content = node.get_content()
        embedding = embed_model.get_text_embedding(content)

        metadata_dict = {
            "book_title": node.metadata.get("book_title"),
            "page_number": node.metadata.get("page_number"),
            "doi": node.metadata.get("doi")
        }

        query = """
            INSERT INTO public.documents (content, embedding, metadata)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query, (content, embedding, json.dumps(metadata_dict)))

        if idx % 50 == 0 and idx > 0:
            print(f"  Progress: {idx}/{len(nodes)} chunks uploaded...")

    conn.commit()
    cursor.close()
    conn.close()
    print("Ingestion complete. All chunks vectorized and stored in Supabase.")


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
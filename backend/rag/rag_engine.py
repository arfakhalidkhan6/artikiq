import json
import logging
import psycopg2
from llama_index.embeddings.openai import OpenAIEmbedding
from groq import Groq
from core.config import SUPABASE_CONNECTION_STRING, OPENAI_API_KEY, GROQ_API_KEY

logger = logging.getLogger(__name__)


class ArtikIQRAGEngine:
    def __init__(self):
        try:
            self.embed_model = OpenAIEmbedding(
                model="text-embedding-ada-002",
                api_key=OPENAI_API_KEY
            )
            self.llm_client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            logger.error(f"ENGINE INIT ERROR: Failed to initialize AI clients: {str(e)}")

    def retrieve_context(self, user_query: str, top_k: int = 3):
        """Converts user question into a vector and queries Supabase."""
        try:
            query_embedding = self.embed_model.get_text_embedding(user_query)
        except Exception as e:
            logger.error(f"EMBEDDING ERROR: OpenAI embedding failed: {str(e)}")
            raise e

        try:
            conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
            cursor = conn.cursor()

            search_query = """
                SELECT content, metadata, (embedding <=> %s::vector) AS distance
                FROM public.documents
                ORDER BY distance ASC
                LIMIT %s;
            """

            cursor.execute(search_query, (query_embedding, top_k))
            records = cursor.fetchall()
            cursor.close()
            conn.close()

            retrieved_chunks = []
            for row in records:
                retrieved_chunks.append({
                    "content": row[0],
                    "metadata": row[1] if isinstance(row[1], dict) else json.loads(row[1])
                })
            return retrieved_chunks

        except Exception as e:
            logger.error(f"DATABASE SEARCH ERROR: Supabase query failed: {str(e)}")
            raise e

    def generate_cited_answer(self, user_query: str):
        """Assembles context and generates a cited answer using Groq LLaMA."""
        context_blocks = self.retrieve_context(user_query, top_k=3)

        if not context_blocks:
            return {
                "answer": "I could not find any matching text inside the textbook data.",
                "citations": []
            }

        formatted_context = ""
        citations_list = []

        for idx, block in enumerate(context_blocks):
            meta = block["metadata"]
            source_tag = f"Source [{idx+1}]"
            formatted_context += (
                f"--- {source_tag}: {meta.get('book_title', 'Textbook')}, "
                f"Page {meta.get('page_number', 'Unknown')} ---\n"
                f"{block['content']}\n\n"
            )
            citations_list.append({
                "book": meta.get("book_title", "Human Communication Disorders"),
                "page": int(meta.get("page_number", 0)),
                "doi": meta.get("doi", "")
            })

        system_prompt = (
            "You are an expert Speech-Language Pathology assistant on ArtikIQ.\n"
            "Answer the query using ONLY the verified textbook segments provided.\n"
            "Append source tags explicitly inline (e.g. [Source 1]).\n\n"
            f"--- START TEXTBOOK CONTEXT ---\n{formatted_context}--- END TEXTBOOK CONTEXT ---"
        )

        try:
            completion = self.llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                max_tokens=1024
            )
            return {
                "answer": completion.choices[0].message.content,
                "citations": citations_list
            }

        except Exception as e:
            logger.error(f"GROQ GENERATION ERROR: LLaMA generation failed: {str(e)}")
            raise e
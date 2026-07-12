import json
import logging
import psycopg2
import cohere
import time
from llama_index.embeddings.openai import OpenAIEmbedding
from groq import Groq
from langfuse import get_client, observe
from core.config import SUPABASE_CONNECTION_STRING, OPENAI_API_KEY, GROQ_API_KEY, GROQ_API_KEY_FALLBACK, COHERE_API_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST
import os

os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST

langfuse = get_client()

logger = logging.getLogger(__name__)

INPUT_PRICE_PER_MILLION = 0.59
OUTPUT_PRICE_PER_MILLION = 0.79

NON_CLINICAL_RESPONSE = (
    "That's not related to speech-language pathology, so I can't answer that "
    "from this knowledge base. If you have a clinical or textbook question, "
    "I'm here and happy to help — feel free to ask anytime."
)


def extract_cited_sources(answer_text: str, citations_list: list) -> list:
    """
    Robustly detects which source numbers were referenced in the answer.
    Handles formats: [Source 1], [Source 1, Source 2], Source 1, [1], etc.
    """
    actually_cited = []
    for i, citation in enumerate(citations_list):
        source_number = i + 1
        patterns = [
            f"Source [{source_number}]",
            f"[Source {source_number}]",
            f"[{source_number}]",
            f"Source {source_number},",
            f"Source {source_number}]",
            f"Source {source_number}.",
            f"Source {source_number} ",
            f"source {source_number}",
        ]
        if any(p.lower() in answer_text.lower() for p in patterns):
            actually_cited.append(citation)

    if not actually_cited:
        actually_cited = citations_list

    return actually_cited


class ArtikIQRAGEngine:
    def __init__(self):
        try:
            self.embed_model = OpenAIEmbedding(
                model="text-embedding-ada-002",
                api_key=OPENAI_API_KEY
            )
            self.llm_client = Groq(api_key=GROQ_API_KEY)
            self.llm_client_fallback = Groq(api_key=GROQ_API_KEY_FALLBACK) if GROQ_API_KEY_FALLBACK else None
            self.cohere_client = cohere.Client(api_key=COHERE_API_KEY)
        except Exception as e:
            logger.error(f"ENGINE INIT ERROR: Failed to initialize AI clients: {str(e)}")

    def is_clinical_question(self, user_query: str) -> bool:
        """Quick check using the LLM itself to classify intent before doing any retrieval."""
        try:
            check = self.llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Respond with exactly one word: YES if the user's message is a clinical, medical, or speech-language-pathology related question. NO if it's a greeting, small talk, or unrelated topic."},
                    {"role": "user", "content": user_query}
                ],
                temperature=0,
                max_tokens=5
            )
            verdict = check.choices[0].message.content.strip().upper()
            return "YES" in verdict
        except Exception:
            return True

    def retrieve_context(self, user_query: str, top_k: int = 15):
        """Converts user question into a vector and queries Supabase for a WIDE pool of candidates."""
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

    def rerank_chunks(self, user_query: str, chunks: list, top_n: int = 3):
        """Takes a wide pool of candidate chunks and re-scores them for true relevance using Cohere."""
        if not chunks:
            return []

        try:
            time.sleep(6.5)

            documents = [chunk["content"] for chunk in chunks]

            response = self.cohere_client.rerank(
                model="rerank-english-v3.0",
                query=user_query,
                documents=documents,
                top_n=top_n
            )

            reranked_chunks = []
            for result in response.results:
                original_chunk = chunks[result.index]
                reranked_chunks.append(original_chunk)

            return reranked_chunks

        except Exception as e:
            logger.error(f"RERANK ERROR: Cohere reranking failed: {str(e)}")
            return chunks[:top_n]

    def _call_groq_primary(self, system_prompt: str, user_query: str):
        """Primary generation path using llama-3.3-70b-versatile on primary Groq account."""
        completion = self.llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1,
            max_tokens=1024
        )

        answer = completion.choices[0].message.content
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens

        return {
            "answer": answer,
            "model_used": "llama-3.3-70b-versatile (primary)",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }

    def _call_groq_fallback(self, system_prompt: str, user_query: str):
        """Fallback generation path using a separate Groq account key to avoid shared rate limits."""
        if not self.llm_client_fallback:
            raise RuntimeError("Fallback Groq client is not configured.")

        completion = self.llm_client_fallback.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1,
            max_tokens=1024
        )

        answer = completion.choices[0].message.content
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens

        return {
            "answer": answer,
            "model_used": "llama-3.3-70b-versatile (fallback)",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }

    def _build_system_prompt(self, formatted_context: str) -> str:
        """Builds the system prompt with clean citation instructions."""
        return (
            "You are an expert Speech-Language Pathology assistant on ArtikIQ.\n"
            "Answer the query using ONLY the verified textbook segments provided.\n"
            "Cite sources at the end of each paragraph only, not after every sentence.\n"
            "Use the exact format [Source N] — one citation per paragraph maximum.\n"
            "Never repeat the same source number more than once in the entire answer.\n\n"
            f"--- START TEXTBOOK CONTEXT ---\n{formatted_context}--- END TEXTBOOK CONTEXT ---"
        )

    @observe()
    def generate_cited_answer(self, user_query: str):
        """Non-streaming: assembles context and generates a cited answer, with Groq fallback."""

        if not self.is_clinical_question(user_query):
            trace_id = langfuse.get_current_trace_id()
            return {
                "answer": NON_CLINICAL_RESPONSE,
                "citations": [],
                "trace_id": trace_id
            }

        wide_candidates = self.retrieve_context(user_query, top_k=15)
        context_blocks = self.rerank_chunks(user_query, wide_candidates, top_n=3)

        if not context_blocks:
            return {
                "answer": "I could not find any matching text inside the textbook data.",
                "citations": [],
                "trace_id": langfuse.get_current_trace_id()
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

        system_prompt = self._build_system_prompt(formatted_context)

        with langfuse.start_as_current_observation(
            as_type="generation",
            name="llm-generation",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
        ) as generation:

            try:
                result = self._call_groq_primary(system_prompt, user_query)
            except Exception as e:
                logger.error(f"GROQ PRIMARY FAILED, falling back to second Groq account: {str(e)}")
                try:
                    result = self._call_groq_fallback(system_prompt, user_query)
                except Exception as e2:
                    logger.error(f"GROQ FALLBACK ALSO FAILED: {str(e2)}")
                    raise e2

            answer = result["answer"]
            input_tokens = result["input_tokens"]
            output_tokens = result["output_tokens"]

            input_cost = (input_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION
            output_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION

            actually_cited = extract_cited_sources(answer, citations_list)

            generation.update(
                model=result["model_used"],
                output=answer,
                usage_details={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens
                },
                cost_details={
                    "input": input_cost,
                    "output": output_cost,
                    "total": input_cost + output_cost
                }
            )

        trace_id = langfuse.get_current_trace_id()

        return {
            "answer": answer,
            "citations": actually_cited,
            "trace_id": trace_id
        }

    @observe()
    def generate_cited_answer_stream(self, user_query: str):
        """Streaming version — yields answer chunks as they arrive from Groq."""

        if not self.is_clinical_question(user_query):
            yield json.dumps({"type": "answer_chunk", "content": NON_CLINICAL_RESPONSE})
            yield json.dumps({"type": "done", "citations": [], "trace_id": langfuse.get_current_trace_id()})
            return

        wide_candidates = self.retrieve_context(user_query, top_k=15)
        context_blocks = self.rerank_chunks(user_query, wide_candidates, top_n=3)

        if not context_blocks:
            yield json.dumps({"type": "answer_chunk", "content": "I could not find any matching text inside the textbook data."})
            yield json.dumps({"type": "done", "citations": [], "trace_id": langfuse.get_current_trace_id()})
            return

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

        system_prompt = self._build_system_prompt(formatted_context)

        full_answer = ""

        try:
            stream = self.llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                max_tokens=1024,
                stream=True
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_answer += delta
                    yield json.dumps({"type": "answer_chunk", "content": delta})

        except Exception as e:
            logger.error(f"STREAMING GROQ PRIMARY FAILED, trying fallback: {str(e)}")
            try:
                if not self.llm_client_fallback:
                    raise RuntimeError("Fallback Groq client is not configured.")

                stream = self.llm_client_fallback.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.1,
                    max_tokens=1024,
                    stream=True
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_answer += delta
                        yield json.dumps({"type": "answer_chunk", "content": delta})

            except Exception as e2:
                logger.error(f"STREAMING GROQ FALLBACK ALSO FAILED: {str(e2)}")
                yield json.dumps({"type": "answer_chunk", "content": "Something went wrong generating the answer."})
                yield json.dumps({"type": "done", "citations": [], "trace_id": None})
                return

        actually_cited = extract_cited_sources(full_answer, citations_list)

        trace_id = langfuse.get_current_trace_id()

        yield json.dumps({
            "type": "done",
            "citations": actually_cited,
            "trace_id": trace_id
        })
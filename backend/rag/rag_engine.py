import json
import logging
import os
import re
import time

import psycopg2
import cohere

from llama_index.embeddings.openai import OpenAIEmbedding
from groq import Groq
from langfuse import get_client, observe

from core.config import (
    SUPABASE_CONNECTION_STRING,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GROQ_API_KEY_FALLBACK,
    COHERE_API_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_HOST,
)


# ============================================================
# ENVIRONMENT / LANGFUSE
# ============================================================

os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST

langfuse = get_client()

logger = logging.getLogger(__name__)


# ============================================================
# PRICING
# ============================================================

INPUT_PRICE_PER_MILLION = 0.59
OUTPUT_PRICE_PER_MILLION = 0.79


# ============================================================
# NON-CLINICAL RESPONSE
# ============================================================

NON_CLINICAL_RESPONSE = (
    "That's not related to speech-language pathology, so I can't answer that "
    "from this knowledge base. If you have a clinical or textbook question, "
    "I'm here and happy to help — feel free to ask anytime."
)


# ============================================================
# SOURCE ID EXTRACTION
# ============================================================

def get_source_id(metadata: dict, fallback_index: int) -> int:
    """
    Get the ORIGINAL source ID from chunk metadata.

    IMPORTANT:
    The source ID is NOT the position of the chunk in the retrieved list.

    Example:

        Retrieved chunks:
            chunk 1 -> source_id 1
            chunk 2 -> source_id 5
            chunk 3 -> source_id 7

    Valid source IDs are therefore:
        1, 5, 7

    NOT:
        1, 2, 3

    We check several common metadata field names so the code
    works with different ingestion formats.
    """

    possible_keys = [
        "source_id",
        "source_number",
        "source",
        "document_id",
        "doc_id",
        "chunk_source_id",
    ]

    for key in possible_keys:
        value = metadata.get(key)

        if value is not None and str(value).strip() != "":
            try:
                return int(value)
            except (ValueError, TypeError):
                pass

    # --------------------------------------------------------
    # IMPORTANT FALLBACK
    # --------------------------------------------------------
    # If your Supabase metadata DOES NOT contain the original
    # source ID, we have no way of knowing whether the source
    # should be 1, 5, 7, etc.
    #
    # In that situation we fall back to the retrieval position.
    # This keeps the application working, but for your actual
    # 1,5,7 source-ID system, you SHOULD store source_id in
    # metadata during ingestion.
    # --------------------------------------------------------

    logger.warning(
        "Original source ID not found in metadata. "
        "Using fallback source ID %s. Metadata=%s",
        fallback_index,
        metadata,
    )

    return fallback_index


# ============================================================
# CITATION EXTRACTION
# ============================================================

def extract_cited_sources(answer_text: str, citations_list: list) -> list:
    """
    Extract ONLY the source IDs actually cited in the final answer.

    This function solves the citation-card mismatch.

    Example:

        Available sources:
            Source 1
            Source 5
            Source 7

        Answer:
            "... [Source 7]"
            "... [Source 1]"

        Returned citations:
            Source 7
            Source 1

        Number of cards:
            2

    It does NOT assume that three retrieved sources mean
    source IDs 1, 2, 3.

    It uses the ACTUAL source_id stored inside citations_list.

    Duplicate citations are removed.

    Invalid citations are ignored.

    Both:
        [Source 7]
        【Source 7】

    are supported.
    """

    if not answer_text or not citations_list:
        return []

    # --------------------------------------------------------
    # NORMALIZE FULL-WIDTH BRACKETS
    # --------------------------------------------------------

    normalized_text = (
        answer_text
        .replace("【", "[")
        .replace("】", "]")
    )

    # --------------------------------------------------------
    # FIND [Source N]
    #
    # Examples matched:
    #
    # [Source 1]
    # [Source 5]
    # [Source 7]
    # [source 7]
    # [ Source 7 ]
    # --------------------------------------------------------

    matches = re.findall(
        r"\[\s*Source\s+(\d+)\s*\]",
        normalized_text,
        flags=re.IGNORECASE,
    )

    if not matches:
        return []

    # --------------------------------------------------------
    # CREATE LOOKUP:
    #
    # source ID -> citation object
    #
    # Example:
    #
    # {
    #     1: {...},
    #     5: {...},
    #     7: {...}
    # }
    # --------------------------------------------------------

    citation_by_source_id = {}

    for citation in citations_list:
        source_id = citation.get("source_id")

        if source_id is None:
            continue

        try:
            source_id = int(source_id)
        except (ValueError, TypeError):
            continue

        citation_by_source_id[source_id] = citation

    # --------------------------------------------------------
    # PRESERVE ORDER + REMOVE DUPLICATES
    # --------------------------------------------------------

    cited_source_ids = []

    for match in matches:
        source_id = int(match)

        # Only accept IDs that actually exist in retrieved
        # sources.
        if source_id not in citation_by_source_id:
            logger.warning(
                "LLM cited Source %s, but that source was not "
                "present in retrieved context.",
                source_id,
            )
            continue

        # Remove duplicate cards.
        if source_id not in cited_source_ids:
            cited_source_ids.append(source_id)

    # --------------------------------------------------------
    # RETURN EXACTLY THE CARDS USED IN THE ANSWER
    # --------------------------------------------------------

    return [
        citation_by_source_id[source_id]
        for source_id in cited_source_ids
    ]


# ============================================================
# RAG ENGINE
# ============================================================

class ArtikIQRAGEngine:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        try:

            self.embed_model = OpenAIEmbedding(
                model="text-embedding-ada-002",
                api_key=OPENAI_API_KEY,
            )

            self.llm_client = Groq(
                api_key=GROQ_API_KEY
            )

            self.llm_client_fallback = (
                Groq(api_key=GROQ_API_KEY_FALLBACK)
                if GROQ_API_KEY_FALLBACK
                else None
            )

            self.cohere_client = cohere.Client(
                api_key=COHERE_API_KEY
            )

        except Exception as e:

            logger.error(
                f"ENGINE INIT ERROR: "
                f"Failed to initialize AI clients: {str(e)}"
            )

            raise


    # ========================================================
    # CLINICAL QUESTION CLASSIFIER
    # ========================================================

    def is_clinical_question(self, user_query: str) -> bool:

        """
        Determines whether the user query is clinical,
        medical, or speech-language-pathology related.
        """

        try:

            check = self.llm_client.chat.completions.create(
                model="openai/gpt-oss-120b",

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Respond with exactly one word: YES if the "
                            "user's message is a clinical, medical, or "
                            "speech-language-pathology related question. "
                            "NO if it's a greeting, small talk, or "
                            "unrelated topic."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_query,
                    },
                ],

                temperature=0,
                max_tokens=50,
                reasoning_effort="low",
            )

            verdict = (
                check
                .choices[0]
                .message
                .content
                .strip()
                .upper()
            )

            return "YES" in verdict

        except Exception as e:

            logger.error(
                f"CLINICAL CLASSIFIER ERROR: {str(e)}"
            )

            # Preserve previous safe behavior.
            return True


    # ========================================================
    # RETRIEVE CONTEXT
    # ========================================================

    def retrieve_context(
        self,
        user_query: str,
        top_k: int = 15,
    ):

        """
        Retrieves a wide candidate pool from Supabase.
        """

        # ----------------------------------------------------
        # CREATE QUERY EMBEDDING
        # ----------------------------------------------------

        try:

            query_embedding = (
                self.embed_model
                .get_text_embedding(user_query)
            )

        except Exception as e:

            logger.error(
                f"EMBEDDING ERROR: "
                f"OpenAI embedding failed: {str(e)}"
            )

            raise


        # ----------------------------------------------------
        # SEARCH SUPABASE
        # ----------------------------------------------------

        try:

            conn = psycopg2.connect(
                SUPABASE_CONNECTION_STRING
            )

            cursor = conn.cursor()

            search_query = """
                SELECT
                    content,
                    metadata,
                    (embedding <=> %s::vector) AS distance
                FROM public.documents
                ORDER BY distance ASC
                LIMIT %s;
            """

            cursor.execute(
                search_query,
                (
                    query_embedding,
                    top_k,
                ),
            )

            records = cursor.fetchall()

            cursor.close()
            conn.close()


            # ------------------------------------------------
            # BUILD CHUNKS
            # ------------------------------------------------

            retrieved_chunks = []

            for row in records:

                metadata = (
                    row[1]
                    if isinstance(row[1], dict)
                    else json.loads(row[1])
                )

                retrieved_chunks.append(
                    {
                        "content": row[0],
                        "metadata": metadata,
                    }
                )

            logger.info(
                "Retrieved %s candidate chunks.",
                len(retrieved_chunks),
            )

            return retrieved_chunks

        except Exception as e:

            logger.error(
                f"DATABASE SEARCH ERROR: "
                f"Supabase query failed: {str(e)}"
            )

            raise


    # ========================================================
    # RERANK CHUNKS
    # ========================================================

    def rerank_chunks(
        self,
        user_query: str,
        chunks: list,
        top_n: int = 3,
    ):

        """
        Reranks retrieved chunks using Cohere.
        """

        if not chunks:
            return []

        try:

            # Existing rate-limit protection.
            time.sleep(6.5)

            documents = [
                chunk["content"]
                for chunk in chunks
            ]

            response = self.cohere_client.rerank(
                model="rerank-english-v3.0",
                query=user_query,
                documents=documents,
                top_n=top_n,
            )

            reranked_chunks = []

            for result in response.results:

                original_chunk = chunks[result.index]

                reranked_chunks.append(
                    original_chunk
                )

            logger.info(
                "Reranked %s chunks.",
                len(reranked_chunks),
            )

            return reranked_chunks

        except Exception as e:

            logger.error(
                f"RERANK ERROR: "
                f"Cohere reranking failed: {str(e)}"
            )

            return chunks[:top_n]


    # ========================================================
    # PRIMARY GROQ CALL
    # ========================================================

    def _call_groq_primary(
        self,
        system_prompt: str,
        user_query: str,
    ):

        """
        Primary GPT-OSS-120B generation path.
        """

        completion = (
            self.llm_client
            .chat
            .completions
            .create(
                model="openai/gpt-oss-120b",

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_query,
                    },
                ],

                temperature=0.1,
                max_tokens=1024,
            )
        )

        answer = (
            completion
            .choices[0]
            .message
            .content
        )

        # Normalize citation brackets.
        answer = (
            answer
            .replace("【", "[")
            .replace("】", "]")
        )

        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens

        return {
            "answer": answer,
            "model_used": (
                "openai/gpt-oss-120b (primary)"
            ),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }


    # ========================================================
    # FALLBACK GROQ CALL
    # ========================================================

    def _call_groq_fallback(
        self,
        system_prompt: str,
        user_query: str,
    ):

        """
        Fallback GPT-OSS-120B generation path.
        """

        if not self.llm_client_fallback:

            raise RuntimeError(
                "Fallback Groq client is not configured."
            )


        completion = (
            self.llm_client_fallback
            .chat
            .completions
            .create(
                model="openai/gpt-oss-120b",

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_query,
                    },
                ],

                temperature=0.1,
                max_tokens=1024,
            )
        )

        answer = (
            completion
            .choices[0]
            .message
            .content
        )

        # Normalize citation brackets.
        answer = (
            answer
            .replace("【", "[")
            .replace("】", "]")
        )

        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens

        return {
            "answer": answer,
            "model_used": (
                "openai/gpt-oss-120b (fallback)"
            ),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }


    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    def _build_system_prompt(
        self,
        formatted_context: str,
        valid_source_ids: list,
    ):

        """
        Creates the citation-aware system prompt.

        IMPORTANT:
        valid_source_ids contains the REAL source IDs.

        Example:
            [1, 5, 7]

        We DO NOT turn this into:
            [1, 2, 3]
        """

        source_count = len(valid_source_ids)

        source_id_text = ", ".join(
            str(source_id)
            for source_id in valid_source_ids
        )

        return (

            "You are an expert Speech-Language Pathology "
            "assistant on ArtikIQ.\n\n"

            "Answer the user's query using ONLY the verified "
            "textbook segments provided below.\n\n"

            f"There are exactly {source_count} retrieved "
            "sources.\n"

            f"The valid source IDs are ONLY: "
            f"{source_id_text}.\n\n"

            "IMPORTANT CITATION RULES:\n"

            "1. Cite a source only when the information in "
            "the paragraph is supported by that source.\n"

            "2. Use the EXACT source ID shown in the context.\n"

            "3. If the context contains Source 1, Source 5, "
            "and Source 7, you must cite them as "
            "[Source 1], [Source 5], or [Source 7].\n"

            "4. NEVER renumber Source 5 as Source 2.\n"

            "5. NEVER renumber Source 7 as Source 3.\n"

            "6. NEVER cite a source ID that does not appear "
            "in the provided context.\n"

            "7. Use exactly this citation format: "
            "[Source N]\n"

            "8. Use standard ASCII square brackets [ and ].\n"

            "9. NEVER use full-width brackets such as "
            "【 or 】.\n"

            "10. Put citations at the end of the paragraph.\n"

            "11. Do not put a citation after every sentence.\n"

            "12. Do not repeat the same source citation "
            "multiple times in the same paragraph unless "
            "necessary.\n\n"

            "--- START TEXTBOOK CONTEXT ---\n"

            f"{formatted_context}"

            "--- END TEXTBOOK CONTEXT ---"
        )


    # ========================================================
    # PREPARE CONTEXT + CITATION METADATA
    # ========================================================

    def _prepare_context(
        self,
        context_blocks: list,
    ):

        """
        Converts retrieved chunks into:

        1. formatted_context
        2. citations_list
        3. valid_source_ids

        This is the most important part of the citation fix.
        """

        formatted_context = ""

        citations_list = []

        valid_source_ids = []

        # ----------------------------------------------------
        # IMPORTANT:
        # DO NOT use idx + 1 as the source ID.
        # ----------------------------------------------------

        for idx, block in enumerate(context_blocks):

            meta = block["metadata"]

            # Get ORIGINAL source ID.
            source_id = get_source_id(
                meta,
                idx + 1,
            )

            # Prevent duplicate source IDs from appearing
            # as separate citation cards.
            if source_id in valid_source_ids:

                logger.warning(
                    "Duplicate source ID %s detected "
                    "in retrieved chunks.",
                    source_id,
                )

            else:

                valid_source_ids.append(
                    source_id
                )


            # ------------------------------------------------
            # CONTEXT LABEL
            # ------------------------------------------------

            source_tag = (
                f"Source [{source_id}]"
            )

            formatted_context += (
                f"--- {source_tag}: "
                f"{meta.get('book_title', 'Textbook')}, "
                f"Page "
                f"{meta.get('page_number', 'Unknown')} "
                f"---\n"
            )

            formatted_context += (
                f"{block['content']}\n\n"
            )


            # ------------------------------------------------
            # CITATION OBJECT
            # ------------------------------------------------

            try:

                page_number = int(
                    meta.get(
                        "page_number",
                        0,
                    )
                )

            except (
                ValueError,
                TypeError,
            ):

                page_number = 0


            citations_list.append(
                {
                    "source_id": source_id,

                    "book": meta.get(
                        "book_title",
                        "Human Communication Disorders",
                    ),

                    "page": page_number,

                    "doi": meta.get(
                        "doi",
                        "",
                    ),
                }
            )


        logger.info(
            "Valid retrieved source IDs: %s",
            valid_source_ids,
        )

        return (
            formatted_context,
            citations_list,
            valid_source_ids,
        )


    # ========================================================
    # NON-STREAMING ANSWER
    # ========================================================

    @observe()
    def generate_cited_answer(
        self,
        user_query: str,
    ):

        """
        Generates a complete answer and returns ONLY the
        citation cards whose source IDs actually appear
        in the answer.
        """

        # ----------------------------------------------------
        # CLINICAL CHECK
        # ----------------------------------------------------

        if not self.is_clinical_question(
            user_query
        ):

            trace_id = (
                langfuse.get_current_trace_id()
            )

            return {
                "answer": NON_CLINICAL_RESPONSE,
                "citations": [],
                "trace_id": trace_id,
            }


        # ----------------------------------------------------
        # RETRIEVE
        # ----------------------------------------------------

        wide_candidates = (
            self.retrieve_context(
                user_query,
                top_k=15,
            )
        )


        # ----------------------------------------------------
        # RERANK
        # ----------------------------------------------------

        context_blocks = (
            self.rerank_chunks(
                user_query,
                wide_candidates,
                top_n=3,
            )
        )


        # ----------------------------------------------------
        # NO CONTEXT
        # ----------------------------------------------------

        if not context_blocks:

            return {
                "answer": (
                    "I could not find any matching text "
                    "inside the textbook data."
                ),
                "citations": [],
                "trace_id": (
                    langfuse.get_current_trace_id()
                ),
            }


        # ----------------------------------------------------
        # PREPARE CONTEXT
        # ----------------------------------------------------

        (
            formatted_context,
            citations_list,
            valid_source_ids,
        ) = self._prepare_context(
            context_blocks
        )


        # ----------------------------------------------------
        # BUILD PROMPT
        # ----------------------------------------------------

        system_prompt = (
            self._build_system_prompt(
                formatted_context,
                valid_source_ids,
            )
        )


        # ----------------------------------------------------
        # LANGFUSE
        # ----------------------------------------------------

        with langfuse.start_as_current_observation(
            as_type="generation",
            name="llm-generation",

            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_query,
                },
            ],
        ) as generation:

            try:

                result = (
                    self._call_groq_primary(
                        system_prompt,
                        user_query,
                    )
                )

            except Exception as e:

                logger.error(
                    "GROQ PRIMARY FAILED, "
                    "falling back to second Groq account: "
                    f"{str(e)}"
                )

                try:

                    result = (
                        self._call_groq_fallback(
                            system_prompt,
                            user_query,
                        )
                    )

                except Exception as e2:

                    logger.error(
                        "GROQ FALLBACK ALSO FAILED: "
                        f"{str(e2)}"
                    )

                    raise e2


            # ------------------------------------------------
            # ANSWER
            # ------------------------------------------------

            answer = result["answer"]

            input_tokens = (
                result["input_tokens"]
            )

            output_tokens = (
                result["output_tokens"]
            )


            # ------------------------------------------------
            # COST
            # ------------------------------------------------

            input_cost = (
                input_tokens
                / 1_000_000
                * INPUT_PRICE_PER_MILLION
            )

            output_cost = (
                output_tokens
                / 1_000_000
                * OUTPUT_PRICE_PER_MILLION
            )


            # ------------------------------------------------
            # EXTRACT ONLY CITED SOURCES
            # ------------------------------------------------

            actually_cited = (
                extract_cited_sources(
                    answer,
                    citations_list,
                )
            )


            # ------------------------------------------------
            # LANGFUSE UPDATE
            # ------------------------------------------------

            generation.update(
                model=result["model_used"],

                output=answer,

                usage_details={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": (
                        input_tokens
                        + output_tokens
                    ),
                },

                cost_details={
                    "input": input_cost,
                    "output": output_cost,
                    "total": (
                        input_cost
                        + output_cost
                    ),
                },
            )


        trace_id = (
            langfuse.get_current_trace_id()
        )


        # ----------------------------------------------------
        # LOG CITATION COUNT
        # ----------------------------------------------------

        logger.info(
            "Citation count: answer=%s, cards=%s",
            len(
                re.findall(
                    r"\[\s*Source\s+\d+\s*\]",
                    answer,
                    flags=re.IGNORECASE,
                )
            ),
            len(actually_cited),
        )


        return {
            "answer": answer,

            "citations": actually_cited,

            "trace_id": trace_id,
        }


    # ========================================================
    # STREAMING ANSWER
    # ========================================================

    @observe()
    def generate_cited_answer_stream(
        self,
        user_query: str,
    ):

        """
        Streaming version.

        The final citation cards are calculated from the
        COMPLETE answer after streaming finishes.
        """

        # ----------------------------------------------------
        # CLINICAL CHECK
        # ----------------------------------------------------

        if not self.is_clinical_question(
            user_query
        ):

            yield json.dumps(
                {
                    "type": "answer_chunk",
                    "content": NON_CLINICAL_RESPONSE,
                }
            )

            yield json.dumps(
                {
                    "type": "done",
                    "citations": [],
                    "trace_id": (
                        langfuse.get_current_trace_id()
                    ),
                }
            )

            return


        # ----------------------------------------------------
        # RETRIEVE
        # ----------------------------------------------------

        wide_candidates = (
            self.retrieve_context(
                user_query,
                top_k=15,
            )
        )


        # ----------------------------------------------------
        # RERANK
        # ----------------------------------------------------

        context_blocks = (
            self.rerank_chunks(
                user_query,
                wide_candidates,
                top_n=3,
            )
        )


        # ----------------------------------------------------
        # NO CONTEXT
        # ----------------------------------------------------

        if not context_blocks:

            yield json.dumps(
                {
                    "type": "answer_chunk",
                    "content": (
                        "I could not find any matching text "
                        "inside the textbook data."
                    ),
                }
            )

            yield json.dumps(
                {
                    "type": "done",
                    "citations": [],
                    "trace_id": (
                        langfuse.get_current_trace_id()
                    ),
                }
            )

            return


        # ----------------------------------------------------
        # PREPARE CONTEXT
        # ----------------------------------------------------

        (
            formatted_context,
            citations_list,
            valid_source_ids,
        ) = self._prepare_context(
            context_blocks
        )


        # ----------------------------------------------------
        # PROMPT
        # ----------------------------------------------------

        system_prompt = (
            self._build_system_prompt(
                formatted_context,
                valid_source_ids,
            )
        )


        # ----------------------------------------------------
        # FULL ANSWER
        # ----------------------------------------------------

        full_answer = ""


        # ====================================================
        # PRIMARY STREAM
        # ====================================================

        try:

            stream = (
                self.llm_client
                .chat
                .completions
                .create(
                    model="openai/gpt-oss-120b",

                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_query,
                        },
                    ],

                    temperature=0.1,
                    max_tokens=1024,
                    stream=True,
                )
            )


            for chunk in stream:

                if not chunk.choices:
                    continue

                delta = (
                    chunk
                    .choices[0]
                    .delta
                    .content
                )

                if delta:

                    # Normalize citation brackets while
                    # streaming.
                    delta = (
                        delta
                        .replace("【", "[")
                        .replace("】", "]")
                    )

                    full_answer += delta

                    yield json.dumps(
                        {
                            "type": "answer_chunk",
                            "content": delta,
                        }
                    )


        # ====================================================
        # FALLBACK STREAM
        # ====================================================

        except Exception as e:

            logger.error(
                "STREAMING GROQ PRIMARY FAILED, "
                "trying fallback: "
                f"{str(e)}"
            )


            try:

                if not self.llm_client_fallback:

                    raise RuntimeError(
                        "Fallback Groq client is not configured."
                    )


                stream = (
                    self.llm_client_fallback
                    .chat
                    .completions
                    .create(
                        model="openai/gpt-oss-120b",

                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt,
                            },
                            {
                                "role": "user",
                                "content": user_query,
                            },
                        ],

                        temperature=0.1,
                        max_tokens=1024,
                        stream=True,
                    )
                )


                for chunk in stream:

                    if not chunk.choices:
                        continue

                    delta = (
                        chunk
                        .choices[0]
                        .delta
                        .content
                    )

                    if delta:

                        delta = (
                            delta
                            .replace("【", "[")
                            .replace("】", "]")
                        )

                        full_answer += delta

                        yield json.dumps(
                            {
                                "type": "answer_chunk",
                                "content": delta,
                            }
                        )


            except Exception as e2:

                logger.error(
                    "STREAMING GROQ FALLBACK ALSO FAILED: "
                    f"{str(e2)}"
                )

                yield json.dumps(
                    {
                        "type": "answer_chunk",
                        "content": (
                            "Something went wrong "
                            "generating the answer."
                        ),
                    }
                )

                yield json.dumps(
                    {
                        "type": "done",
                        "citations": [],
                        "trace_id": None,
                    }
                )

                return


        # ====================================================
        # FINAL CITATION EXTRACTION
        # ====================================================

        # IMPORTANT:
        #
        # We wait until the ENTIRE answer has arrived.
        #
        # Then we count the unique valid source IDs.
        #
        # This guarantees:
        #
        # Answer:
        #   [Source 1]
        #   [Source 7]
        #
        # Cards:
        #   Source 1
        #   Source 7
        #
        # = 2 cards.
        # ====================================================

        actually_cited = (
            extract_cited_sources(
                full_answer,
                citations_list,
            )
        )


        trace_id = (
            langfuse.get_current_trace_id()
        )


        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        yield json.dumps(
            {
                "type": "done",

                "citations": actually_cited,

                "trace_id": trace_id,
            }
        )
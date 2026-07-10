import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import json
from groq import Groq
from core.config import SUPABASE_CONNECTION_STRING, GROQ_API_KEY

llm_client = Groq(api_key=GROQ_API_KEY)

FILTER_PROMPT = """You are reviewing text chunks extracted from a Speech-Language Pathology textbook for a clinical knowledge base.

A chunk is USABLE if it contains a complete clinical explanation, definition, clinical case study (patient symptoms/diagnosis/treatment), or therapeutic information a student could learn from.

A chunk is JUNK if it is:
- A bibliography or reference list entry (author names, years, journal titles)
- A bare figure/table caption with no surrounding explanation
- Just a page number alone
- A cut-off sentence fragment that doesn't form a complete thought
- A transcription excerpt with no context explaining what it demonstrates
- A personal narrative or biographical essay about an author's career or life story (not actual clinical/patient content)

Respond with EXACTLY one word: USABLE or JUNK. Nothing else."""

def classify_chunk(chunk_text):
    response = llm_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": FILTER_PROMPT},
            {"role": "user", "content": chunk_text}
        ],
        temperature=0,
        max_tokens=10
    )
    return response.choices[0].message.content.strip()


conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
cursor = conn.cursor()

cursor.execute("""
    SELECT content, metadata
    FROM public.documents
    ORDER BY RANDOM()
    LIMIT 30;
""")

records = cursor.fetchall()
cursor.close()
conn.close()

with open("filter_test_results.txt", "w", encoding="utf-8") as f:
    for idx, row in enumerate(records):
        content = row[0]
        metadata = row[1] if isinstance(row[1], dict) else json.loads(row[1])

        verdict = classify_chunk(content)

        f.write(f"\n{'='*80}\n")
        f.write(f"CHUNK #{idx+1} | Page: {metadata.get('page_number', 'Unknown')}\n")
        f.write(f"LLM VERDICT: {verdict}\n")
        f.write(f"YOUR VERDICT (fill this in): \n")
        f.write(f"{'='*80}\n")
        f.write(content)
        f.write("\n")

        print(f"Chunk {idx+1}: {verdict}")

print("\nDone. Results saved to filter_test_results.txt")
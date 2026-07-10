import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import json
from core.config import SUPABASE_CONNECTION_STRING

conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
cursor = conn.cursor()

# Pull 15 random chunks
cursor.execute("""
    SELECT content, metadata
    FROM public.documents
    ORDER BY RANDOM()
    LIMIT 15;
""")

records = cursor.fetchall()
cursor.close()
conn.close()

with open("chunk_inspection.txt", "w", encoding="utf-8") as f:
    for idx, row in enumerate(records):
        content = row[0]
        metadata = row[1] if isinstance(row[1], dict) else json.loads(row[1])
        
        f.write(f"\n{'='*80}\n")
        f.write(f"CHUNK #{idx+1}\n")
        f.write(f"Page: {metadata.get('page_number', 'Unknown')}\n")
        f.write(f"Book: {metadata.get('book_title', 'Unknown')}\n")
        f.write(f"{'='*80}\n")
        f.write(content)
        f.write("\n")

print("Done. 15 random chunks saved to chunk_inspection.txt")
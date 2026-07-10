import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import json
from core.config import SUPABASE_CONNECTION_STRING

conn = psycopg2.connect(SUPABASE_CONNECTION_STRING)
cursor = conn.cursor()

cursor.execute("""
    SELECT content, metadata
    FROM public.documents
    WHERE (metadata->>'page_number')::int <= 5
    ORDER BY (metadata->>'page_number')::int;
""")

records = cursor.fetchall()
cursor.close()
conn.close()

print(f"Found {len(records)} chunks with page_number 5 or lower\n")

for idx, row in enumerate(records):
    content = row[0]
    metadata = row[1] if isinstance(row[1], dict) else json.loads(row[1])
    print(f"{'='*80}")
    print(f"CHUNK #{idx+1} | Page: {metadata.get('page_number')} | Chapter: {metadata.get('chapter')}")
    print(f"{'='*80}")
    print(content[:500])
    print()
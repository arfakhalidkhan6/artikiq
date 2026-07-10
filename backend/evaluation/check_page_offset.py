import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # pymupdf

PDF_PATH = "data/Human_Communication_Disorders.pdf"

doc = fitz.open(PDF_PATH)

print(f"Total PDF pages: {len(doc)}\n")
print("Checking printed page numbers vs PDF page numbers...\n")

# Check a sample of pages spread across the book
sample_pdf_pages = [10, 30, 67, 100, 200, 300, 400, 467]

for pdf_page_num in sample_pdf_pages:
    if pdf_page_num >= len(doc):
        continue
    
    page = doc[pdf_page_num - 1]  # pymupdf is 0-indexed, PDF pages are 1-indexed
    text = page.get_text()
    
    # Print first 100 and last 100 characters to spot the printed page number
    print(f"--- PDF Page {pdf_page_num} ---")
    print(f"Start: {text[:80].strip()}")
    print(f"End: {text[-80:].strip()}")
    print()

doc.close()
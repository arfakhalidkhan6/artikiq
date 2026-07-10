CHAPTER_RANGES = [
    {"chapter": "Chapter 1: Introduction", "start": 18, "end": 32},
    {"chapter": "Chapter 2: Development of Communication, Language, and Speech", "start": 33, "end": 70},
    {"chapter": "Chapter 3: The Biology and Physics of Speech", "start": 71, "end": 100},
    {"chapter": "Chapter 4: Multicultural and Multilingual Considerations", "start": 101, "end": 126},
    {"chapter": "Chapter 5: Genetics", "start": 127, "end": 148},
    {"chapter": "Chapter 6: Articulatory and Phonological Disorders", "start": 149, "end": 180},
    {"chapter": "Chapter 7: Stuttering and Other Disorders of Fluency", "start": 181, "end": 218},
    {"chapter": "Chapter 8: Voice Disorders", "start": 219, "end": 254},
    {"chapter": "Chapter 9: Cleft Lip and Palate and Other Craniofacial Disorders", "start": 255, "end": 288},
    {"chapter": "Chapter 10: Neurogenic Disorders of Speech in Children and Adults", "start": 289, "end": 322},
    {"chapter": "Chapter 14: Aphasia and Related Acquired Language Disorders", "start": 323, "end": 348},
    {"chapter": "Chapter 15: Augmentative and Alternative Communication", "start": 349, "end": 382},
    {"chapter": "Chapter 16: Disorders of Swallowing", "start": 383, "end": 411},
    {"chapter": "Chapter 17: Hearing and Hearing Disorders", "start": 412, "end": 443},
    {"chapter": "Chapter 18: Audiologic Rehabilitation", "start": 444, "end": 468},
]

EXCLUDE_FROM_PAGE = 469
GLOSSARY_START = 6
GLOSSARY_END = 17
PAGE_OFFSET = 5


def get_chapter_for_page(pdf_page_number: int):
    if pdf_page_number >= EXCLUDE_FROM_PAGE:
        return None

    if GLOSSARY_START <= pdf_page_number <= GLOSSARY_END:
        return "Glossary"

    for chapter_info in CHAPTER_RANGES:
        if chapter_info["start"] <= pdf_page_number <= chapter_info["end"]:
            return chapter_info["chapter"]

    return None


def is_page_excluded(pdf_page_number: int) -> bool:
    if pdf_page_number >= EXCLUDE_FROM_PAGE:
        return True
    if GLOSSARY_START <= pdf_page_number <= GLOSSARY_END:
        return True
    return False


def get_printed_page_number(pdf_page_number: int) -> int:
    real_page = pdf_page_number - PAGE_OFFSET
    return max(real_page, 1)
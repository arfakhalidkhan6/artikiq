import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langfuse import get_client
from core.config import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST
from evaluation.golden_dataset import GOLDEN_DATASET

os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST

langfuse = get_client()

DATASET_NAME = "artikiq-golden-30"

langfuse.create_dataset(
    name=DATASET_NAME,
    description="30-question golden evaluation set for ArtikIQ, sourced directly from Human Communication Disorders (Anderson & Shames, 8th Ed.)"
)

print(f"Created dataset: {DATASET_NAME}")

for item in GOLDEN_DATASET:
    langfuse.create_dataset_item(
        dataset_name=DATASET_NAME,
        input={"question": item["question"]},
        expected_output={"ground_truth": item["ground_truth"]},
        metadata={"chapter": item["chapter"], "id": item["id"]}
    )
    print(f"  Uploaded item {item['id']}: {item['question'][:50]}...")

print(f"\nDone. {len(GOLDEN_DATASET)} questions uploaded to Langfuse dataset '{DATASET_NAME}'.")
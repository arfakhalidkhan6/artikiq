import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from rag.rag_engine import ArtikIQRAGEngine
from evaluation.golden_dataset import GOLDEN_DATASET

engine = ArtikIQRAGEngine()

questions = []
answers = []
contexts = []
ground_truths = []

print(f"Running ArtikIQ pipeline (with reranker) on {len(GOLDEN_DATASET)} golden questions...\n")

for item in GOLDEN_DATASET:
    q = item["question"]
    print(f"  [{item['id']}/{len(GOLDEN_DATASET)}] {item['chapter']}")
    print(f"      {q}")

    wide_candidates = engine.retrieve_context(q, top_k=15)
    reranked_chunks = engine.rerank_chunks(q, wide_candidates, top_n=3)
    result = engine.generate_cited_answer(q)

    questions.append(q)
    answers.append(result["answer"])
    contexts.append([chunk["content"] for chunk in reranked_chunks])
    ground_truths.append(item["ground_truth"])

print("\nPipeline done. Running RAGAS evaluation...\n")

ragas_dataset = Dataset.from_dict({
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truth": ground_truths,
})

results = evaluate(
    dataset=ragas_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision],
)

print("\n========== ARTIKIQ RAGAS EVALUATION RESULTS (POST-RERANKER) ==========")
print(f"Faithfulness:      {results['faithfulness']:.4f}   (baseline was 0.8181)")
print(f"Answer Relevancy:  {results['answer_relevancy']:.4f}   (baseline was 0.7536)")
print(f"Context Precision: {results['context_precision']:.4f}   (baseline was 0.7667)")
print("========================================================================")
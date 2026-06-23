from __future__ import annotations

import json
from pathlib import Path

RESULTS_PATH = Path(__file__).resolve().parent / "results.json"


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    retrieval_hits = 0
    root_cause_hits = 0
    for result in results:
        if set(result["expected_doc_ids"]) & set(result["retrieved_doc_ids"]):
            retrieval_hits += 1
        if result["expected_root_cause_contains"].lower() in result["predicted_root_cause"].lower():
            root_cause_hits += 1
    total = len(results)
    print(
        json.dumps(
            {
                "fixtures": total,
                "retrieval_top3_hit_rate": round(retrieval_hits / total, 2) if total else 0.0,
                "root_cause_accuracy": round(root_cause_hits / total, 2) if total else 0.0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

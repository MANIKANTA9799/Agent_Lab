from typing import Any 

def reciprocal_rank_fusion(
    dense_results: list[dict[str, Any]],
    sparse_results: list[dict[str, Any]],
    k: int = 60,
) -> list[dict[str, Any]]:

    rrf_score = {}

    for i in range(len(dense_results)):
        doc_id = dense_results[i]["id"]

        if doc_id not in rrf_score:
            rrf_score[doc_id] = {
                "id": doc_id,
                "payload": dense_results[i]["payload"],
                "score": 0.0,
            }

        rrf_score[doc_id]["score"] += 1 / (k + i + 1)

    for j in range(len(sparse_results)):
        doc_id = sparse_results[j]["id"]

        if doc_id not in rrf_score:
            rrf_score[doc_id] = {
                "id": doc_id,
                "payload": sparse_results[j]["payload"],
                "score": 0.0,
            }

        rrf_score[doc_id]["score"] += 1 / (k + j + 1)

    return sorted(
        rrf_score.values(),
        key=lambda x: x["score"],
        reverse=True,
    )
from sentence_transformers import CrossEncoder



def chunks_reranker(query, chunks, model, rerank_top_k = 5, min_score = 0.3, mlflow_log = False):
    reranker = CrossEncoder(model)

    pairs = [(query, chunk["text"]) for chunk in chunks]

    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )

    top_chunks = [chunk for chunk, score in reranked[:rerank_top_k] if float(score) >= min_score]

    # if mlflow_log:
    #     log_metrics({
    #         "Number of reranked chunks": len(top_chunks)
    #     })

    return top_chunks

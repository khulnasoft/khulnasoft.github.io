"""Search plane: keyword + semantic (TF-IDF) + hybrid retrieval.

Phase 9.2/9.3 require keyword, semantic, and hybrid search over the knowledge
base. This module builds a deterministic, self-contained inverted index and a
sparse TF-IDF vector index over each resource's context bundle and metadata,
then scores queries across keyword, semantic cosine, and a hybrid blend.

It deliberately avoids external model dependencies at build time (per the
"usable operating model over a production-scale vector layer" decision),
while still producing a retrievable vector representation (`vectors.json`)
that an external or in-tree vector service could later index.
"""
from __future__ import annotations

import math
import re
from typing import Iterable

STOPWORDS = {
    "a", "an", "the", "and", "or", "to", "for", "of", "in", "on", "at", "by",
    "is", "it", "as", "with", "from", "be", "this", "that", "an", "are", "was",
    "are", "or", "not", "so", "if", "into", "over", "api", "service", "the",
}


def tokenize(text: str) -> list[str]:
    text = (text or "").lower()
    tokens = re.findall(r"[a-z0-9+#.\-]+", text)
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def document_field(resource: dict) -> str:
    """Concatenate the AI-relevant text fields used for semantic retrieval."""
    parts = [
        resource.get("name", ""),
        resource.get("kind", ""),
        resource.get("owner", ""),
        resource.get("workspace", ""),
        resource.get("summary", ""),
        "\n".join(resource.get("capabilities", [])),
        "\n".join(resource.get("tags", [])),
        "\n".join(resource.get("languages", [])),
        "\n".join(resource.get("frameworks", [])),
        "\n".join(f"{r.get('type')} {r.get('target','')}" for r in resource.get("relationships", [])),
        resource.get("ai", {}).get("contextBundle", "") and "context-bundle",
    ]
    return "\n".join(str(p) for p in parts)


def tf(term: str, terms: list[str]) -> float:
    return terms.count(term) / max(1, len(terms))


def idf(term: str, documents: list[list[str]]) -> float:
    df = sum(1 for doc in documents if term in doc)
    return math.log((1 + len(documents)) / (1 + df)) + 1.0


def build_index(resources: list[dict]) -> dict:
    """Build keyword index + TF-IDF vector model for all resources."""
    docs = [(r["slug"], tokenize(document_field(r))) for r in resources]
    vocab = sorted({t for _, toks in docs for t in toks})
    documents = [toks for _, toks in docs]
    idf_scores = {t: idf(t, documents) for t in vocab}

    # Sparse TF-IDF vectors per resource.
    vectors = {}
    for slug, toks in docs:
        vec = {}
        for t in toks:
            w = tf(t, toks) * idf_scores[t]
            if w:
                vec[t] = vec.get(t, 0.0) + w
        vectors[slug] = vec

    # Keyword index: term -> list of (slug, tf)
    keyword_index: dict[str, list[tuple[str, float]]] = {t: [] for t in vocab}
    for slug, toks in docs:
        for t in toks:
            keyword_index[t].append((slug, tf(t, toks)))

    return {
        "vocab_size": len(vocab),
        "idf": idf_scores,
        "vectors": vectors,            # sparse TF-IDF per resource (semantic model)
        "keyword_index": keyword_index,
        "documents": {slug: toks for slug, toks in docs},
    }


def _normalize(vec: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {k: v / norm for k, v in vec.items()}


def semantic_score(query_terms: list[str], doc_vec: dict[str, float], idf_scores: dict[str, float]) -> float:
    """Cosine similarity between a TF-IDF query vector and a document vector."""
    qvec = {t: tf(t, query_terms) * idf_scores.get(t, 0.0) for t in set(query_terms)}
    qn = _normalize(qvec)
    dn = _normalize(doc_vec)
    terms = set(qn) | set(dn)
    return sum(qn.get(t, 0.0) * dn.get(t, 0.0) for t in terms)


def keyword_score(query_terms: list[str], keyword_index: dict, doc_len: int) -> float:
    """BM25-ish keyword score favoring term presence across query terms."""
    k1, b, avgdl = 1.5, 0.75, 50.0
    score = 0.0
    for t in set(query_terms):
        postings = keyword_index.get(t, [])
        idf = math.log((1 + len(keyword_index)) / (1 + len(postings))) + 1.0
        for slug, freq in postings:
            denom = 1 + b * (1 - b + b * doc_len / avgdl) if doc_len else 1
            score += idf * (freq * (k1 + 1)) / (k1 * denom)
    return score


def search(index: dict, query: str, mode: str = "hybrid", limit: int = 25) -> list[dict]:
    """Rank resources for a query across keyword/semantic/hybrid modes."""
    query_terms = tokenize(query)
    if not query_terms:
        return []

    idf_scores = index["idf"]
    keyword_index = index["keyword_index"]
    vectors = index["vectors"]
    documents = index["documents"]

    results = []
    for slug, doc_vec in vectors.items():
        kw = keyword_score(query_terms, keyword_index, len(documents.get(slug, [])))
        sm = semantic_score(query_terms, doc_vec, idf_scores)
        if mode == "keyword":
            score = kw
        elif mode == "semantic":
            score = sm
        else:  # hybrid: weighted blend
            score = 0.5 * kw + 0.5 * sm
        if score > 0:
            results.append({"slug": slug, "score": round(score, 4),
                            "keyword": round(kw, 4), "semantic": round(sm, 4)})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def build_search_index(resources: list[dict], readiness_by_id: dict, index: dict) -> list[dict]:
    """Emit the search-index.json document, enriched with the semantic vector."""
    out = []
    for r in resources:
        out.append({
            "slug": r["slug"],
            "name": r["name"],
            "kind": r["kind"],
            "owner": r.get("owner"),
            "workspace": r.get("workspace"),
            "lifecycle": r.get("lifecycle"),
            "health": r["health"]["status"],
            "readiness": readiness_by_id[r["id"]]["overall"],
            "level": readiness_by_id[r["id"]]["level"],
            "capabilities": r.get("capabilities", []),
            "tags": r.get("tags", []),
            "summary": r["summary"],
            "preview": r["summary"][:220],
            "relationships": [rel["target"] for rel in r.get("relationships", [])],
            "vector": index["vectors"].get(r["slug"], {}),
            "text": " ".join([r["name"], r["kind"], r.get("owner", ""), r.get("workspace", ""), r["summary"], *r.get("capabilities", []), *r.get("tags", [])]).lower(),
        })
    return out

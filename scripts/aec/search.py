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
    """Rank resources for a query across keyword/semantic/hybrid and specialty modes.

    Specialty modes (Phase 9.3) select and score resources by a derived dimension
    rather than full-text matching:
      - capability: resources exposing the matched capability
      - ownership: resources whose owner or workspace matches
      - relationship: resources linked to or depended-on by the query
      - security: resources flagged by security posture / scan status
      - impact: resources ranked by downstream blast radius
    """
    query_terms = tokenize(query)
    if not query_terms and mode != "impact":
        return []

    if mode in ("keyword", "semantic", "hybrid"):
        return _lexical_search(index, query_terms, mode, limit)

    docs = index["search_docs"]  # enriched per-resource documents
    return _specialty_search(docs, query_terms, mode, index.get("blast_by_slug", {}), limit)


def _lexical_search(index: dict, query_terms: list[str], mode: str, limit: int) -> list[dict]:
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


def _specialty_search(docs: dict, query_terms: list[str], mode: str, blast_by_slug: dict, limit: int) -> list[dict]:
    """Score resources by a specialty dimension; higher score = stronger match."""
    qset = set(query_terms)
    results = []
    for slug, doc in docs.items():
        caps = [c.lower() for c in doc.get("capabilities", [])]
        owner = (doc.get("owner") or "").lower()
        workspace = (doc.get("workspace") or "").lower()
        rels = doc.get("relationships", [])
        kind = doc.get("kind", "").lower()
        health_status = doc.get("health", "unknown")
        scan = doc.get("scanStatus", "unknown")
        readiness = doc.get("readiness", 0)
        blast = blast_by_slug.get(slug, 0)

        if mode == "capability":
            matched = [c for c in caps if any(t in c for t in qset)]
            score = len(matched)
            if not matched and qset & {"api", "security", "observability", "deployment"}:
                continue
            score += readiness / 100.0
        elif mode == "ownership":
            matched = (qset & set(owner.split())) or (qset & set(workspace.split()))
            if not matched and not (qset & set(f"{owner} {workspace}".split())):
                continue
            score = len(matched) + 0.1
        elif mode == "relationship":
            matched = sum(1 for t in rels if any(term in str(t).lower() for term in qset))
            is_target = any(term in str(slug).lower() for term in qset)
            score = matched + (1.0 if is_target else 0.0)
            if not matched and not is_target:
                continue
        elif mode == "security":
            # Match on security-related capability, posture, or scan status.
            sec_terms = qset & {"security", "vulnerability", "clean", "audit", "policy", "compliance"}
            if not sec_terms:
                continue
            bad = health_status in ("critical", "degraded", "warning") or scan != "clean"
            score = (1.0 if bad else 0.5) + (readiness / 200.0)
            if not bad and readiness >= 70:
                score += 0.2
        elif mode == "impact":
            # Rank everything by downstream blast radius; an optional query
            # term further weights resources whose identity matches it.
            score = float(blast) + (readiness / 100.0)
            if qset and not (qset & set(f"{doc.get('name','')} {kind} {owner} {workspace}".split())):
                score -= 0.05
            if score <= 0:
                continue
        else:
            continue

        if score > 0:
            results.append({"slug": slug, "name": doc.get("name", slug), "score": round(score, 4),
                            "mode": mode})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def build_search_index(resources: list[dict], readiness_by_id: dict, index: dict,
                        blast_by_slug: dict | None = None) -> list[dict]:
    """Emit the search-index.json document, enriched with the semantic vector."""
    out = []
    for r in resources:
        out.append({
            "slug": r["slug"],
            "name": r["name"],
            "kind": r["kind"],
            "owner": r.get("owner"),
            "team": r.get("team"),
            "workspace": r.get("workspace"),
            "lifecycle": r.get("lifecycle"),
            "health": r["health"]["status"],
            "scanStatus": r.get("security", {}).get("scanStatus", "unknown"),
            "posture": r.get("security", {}).get("posture", "unknown"),
            "readiness": readiness_by_id[r["id"]]["overall"],
            "level": readiness_by_id[r["id"]]["level"],
            "blastRadius": blast_by_slug.get(r["slug"], 0) if blast_by_slug else 0,
            "capabilities": r.get("capabilities", []),
            "tags": r.get("tags", []),
            "summary": r["summary"],
            "preview": r["summary"][:220],
            "relationships": [rel["target"] for rel in r.get("relationships", [])],
            "vector": index["vectors"].get(r["slug"], {}),
            "text": " ".join([r["name"], r["kind"], r.get("owner", ""), r.get("workspace", ""),
                              r["summary"], *r.get("capabilities", []), *r.get("tags", [])]).lower(),
        })
    return out


def build_index(resources: list[dict], readiness_by_id: dict | None = None,
                blast_by_slug: dict | None = None) -> dict:
    """Build keyword index + TF-IDF vector model for all resources.

    When `readiness_by_id` and `blast_by_slug` are provided, the returned index
    also embeds enriched per-resource documents (`search_docs`) and blast-radius
    data so the specialty search modes (capability/ownership/relationship/
    security/impact) can rank resources without a separate lookup.
    """
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

    search_docs: dict[str, dict] = {}
    if readiness_by_id is not None:
        for r in resources:
            rid = r["id"]
            rd = readiness_by_id.get(rid, {})
            search_docs[r["slug"]] = {
                "slug": r["slug"], "name": r["name"], "kind": r["kind"],
                "owner": r.get("owner"), "workspace": r.get("workspace"),
                "lifecycle": r.get("lifecycle"), "health": r["health"]["status"],
                "scanStatus": r.get("security", {}).get("scanStatus", "unknown"),
                "posture": r.get("security", {}).get("posture", "unknown"),
                "readiness": rd.get("overall", 0), "level": rd.get("level", ""),
                "blastRadius": (blast_by_slug or {}).get(r["slug"], 0),
                "capabilities": r.get("capabilities", []),
                "tags": r.get("tags", []),
                "relationships": [rel["target"] for rel in r.get("relationships", [])],
                "summary": r.get("summary", ""),
            }

    return {
        "vocab_size": len(vocab),
        "idf": idf_scores,
        "vectors": vectors,            # sparse TF-IDF per resource (semantic model)
        "keyword_index": keyword_index,
        "documents": {slug: toks for slug, toks in docs},
        "search_docs": search_docs,
        "blast_by_slug": blast_by_slug or {},
    }

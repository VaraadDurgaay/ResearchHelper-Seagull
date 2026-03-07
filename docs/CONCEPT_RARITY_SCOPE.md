# Concept rarity: scope and labels

## Scope of uniqueness

**Concepts and their rarity are computed only within the current workspace.**

- **Data source:** Concept nodes are built from `paper_intelligence.keywords` (LLM-extracted per paper). The graph is built from papers and intelligence documents filtered by `workspace_id`.
- **`paper_count`:** For each concept node, `paper_count` is the number of **papers in this workspace** that have a `has_concept` link to that concept (i.e. that keyword appears in that paper’s extracted keywords).
- **No global literature:** The system does **not** query external APIs (OpenAlex, Semantic Scholar, CrossRef) or the whole database. A “rare” concept means rare **in this workspace**, not in global scientific literature.

So labels must not imply a global research gap. We use workspace-scoped wording.

---

## Classification (concept_rarity)

| paper_count | concept_rarity   | Label (UI)                        | Badge color |
|-------------|------------------|-----------------------------------|-------------|
| 1           | `rare`           | Rare concept in this workspace    | Red         |
| 2–3         | `low_coverage`   | Low coverage concept              | Amber       |
| 4+          | `common`         | Common concept                    | Neutral     |

- **Backend:** Set in `intelligence_graph_service.py` when building the graph (after all `has_concept` links and `paper_count` are computed).
- **Frontend:** Concept side panel shows the label and “Connected papers: N”. If `concept_rarity` is missing (e.g. old API), the frontend derives rarity from `paper_count` with the same thresholds.

---

## How concepts are produced

1. **Extraction:** Per-paper LLM extraction (see `intelligence_extraction.py`) returns `keywords` (key-point keywords). Stored in `paper_intelligence.keywords`.
2. **Normalization:** In the graph builder, concept labels are normalized with `_normalize_label(name)` (lowercase, single spaces). Deduplication is by this normalized key; id is `concept:{key}`.
3. **Deduplication:** Different surface forms that normalize to the same string (e.g. “Signal Processing” and “signal processing”) become one concept node. No cross-paper merging of different strings (e.g. “DSP” vs “digital signal processing”) unless the LLM or normalization aligns them.
4. **connected_papers:** Same as `paper_count`: number of distinct papers that have a `has_concept` link to this concept in the current graph (workspace-only).

---

## Optional future upgrade: global literature

If external APIs are added later (e.g. OpenAlex, Semantic Scholar, CrossRef):

- Query concept frequency in global or external literature.
- If a concept is rare **globally**, a label like “Rare concept in literature” could be shown (with appropriate attribution).
- If it is rare only in the workspace, keep “Rare concept in this workspace”.
- Backend could add e.g. `global_rarity` or `literature_frequency` and the UI could show both workspace and global wording where available.

No such integration exists today; all labels are workspace-scoped.

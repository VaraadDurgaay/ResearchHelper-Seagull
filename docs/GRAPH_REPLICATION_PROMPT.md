# Graph replication prompt

Use this prompt to recreate the **exact** research intelligence graph from this project (Seagull). Copy the entire "Prompt to reproduce" section below into an AI or implementation brief.

---

## Prompt to reproduce

**Goal:** Build a 2D force-directed research graph that looks and behaves identically to the one in this project.

### 1. Tech stack
- **Frontend:** React (or Next.js), `react-force-graph-2d` for the canvas graph.
- **Important:** Load the graph with `dynamic(import("react-force-graph-2d"), { ssr: false })` and wrap the default export in `forwardRef` so the ref is forwarded (needed for `zoomToFit` and `d3Force`).
- **Backend:** API that returns `{ nodes, links }`; optionally a separate “intelligence” endpoint that returns nodes with types and links with types.

### 2. Data model (intelligence graph)

**Nodes** — each has `id`, `label`, `type`:
- `type: "paper"` — main entities (paper title as label); optional `year`, `main_problem`, `methods_used`, `key_findings`, `datasets_used`, `keywords`, `domain`, `claims`.
- `type: "method"` — methodology nodes (e.g. "Reinforcement Learning"); id like `method:normalized_name`.
- `type: "dataset"` — dataset nodes; id like `dataset:normalized_name`.
- `type: "concept"` — keyword/concept nodes; id like `concept:normalized_name`; optional `paper_count`, `is_research_gap`.
- `type: "keypoint"` — key-finding nodes from key_findings; id like `keypoint:<hash>`.

**Links** — each has `source`, `target`, `type` (string), optional `weight`, optional `contradictions` (array for contradiction type):
- `similarity` — paper–paper (embedding cosine ≥ 0.70).
- `citation` — paper–paper (DOI/title match).
- `keyword_overlap` — paper–paper (≥ 3 meaningful keyword overlap after stopword filter).
- `contradiction` — paper–paper (from claim verification: SUPPORT vs CONTRADICT); can carry `contradictions: [{ claim, paperA_statement, paperB_statement, paperA_page, paperB_page }]`.
- `uses_method` — paper → method.
- `uses_dataset` — paper → dataset.
- `has_concept` — paper → concept.
- `has_keypoint` — paper → keypoint.

### 3. Visual style (Obsidian-like)

- **Background:** `#1f2024`.
- **Default node color:** `rgba(223, 208, 184, 1)` (#DFD0B8). Hover: `rgba(240, 228, 205, 1)`. Selected: `rgba(255, 245, 220, 1)`. Faded (low opacity): `rgba(223, 208, 184, 0.15)`.
- **Node colors by type (when using intelligence graph):**
  - method: `rgba(220, 160, 100, 0.95)`
  - dataset: `rgba(100, 200, 180, 0.95)`
  - concept: `rgba(180, 140, 220, 0.9)`
  - keypoint: `rgba(255, 195, 90, 0.95)`
- **Node circle (in custom node renderer):** fill `#7077A1`; no stroke. Paper nodes radius 6, all other types radius 3.
- **Links:** default `rgba(126, 116, 124, 0.2)`; contradiction links: `rgba(255, 0, 0, 0.95)`, lineWidth 8 (or 4 on hover).
- **Cluster colors (if “Show Clusters”):** cycle through `rgba(100,160,255,0.5)`, `rgba(160,100,255,0.5)`, `rgba(255,140,100,0.5)`, `rgba(100,220,180,0.5)`, `rgba(220,180,100,0.5)`, `rgba(180,100,220,0.5)`.

### 4. Node rendering (custom canvas)

- Use **custom node renderer** (e.g. `nodeCanvasObject`) and set `nodeCanvasObjectMode` to `"replace"` so default node drawing is off.
- Draw in this order:
  1. Circle: `ctx.arc(x, y, radius, 0, 2*Math.PI)` with fill `#7077A1`; radius = 6 for paper, 3 for others.
  2. Label below node: multi-line, word-wrapped, **zoom-stable**. Use the third parameter of the renderer (e.g. `globalScale`) to compute font size as `baseFontSize / scale` with baseFontSize 6, clamped between 3 and 10. Font: `Inter, sans-serif`. Color: `rgba(223, 208, 184, 0.85)`. Text align center, baseline top. Position: `(x, y + radius + 4)` for first line; wrap at 42 characters per line, max 4 lines; add "..." on last line if truncated.
- **Hover tooltip (optional):** use the library’s `nodeLabel` to show e.g. "Name: &lt;label&gt;\nPublish Date: &lt;year or '-'&gt;".

### 5. Link rendering (custom canvas)

- Use **custom link renderer** (e.g. `linkCanvasObject`) with `linkCanvasObjectMode`: `"replace"`.
- Draw line from `(source.x, source.y)` to `(target.x, target.y)`. Default: `strokeStyle rgba(126,116,124,0.2)`, `lineWidth 1`. If link type is `contradiction`: `strokeStyle rgba(255,0,0,0.95)`, `lineWidth` 8 (or 4 when hovered). No arrows unless you add them separately.

### 6. Force simulation (d3-force)

- **Charge:** strength `-90`; `distanceMax` `80` (repulsion only within 80 units so clusters don’t push each other apart).
- **Link:** default distance `36`; strength `0.85`.
- **Center:** strength `2.2` (strong pull so all clusters sit near center).
- After applying these forces, call **`d3ReheatSimulation()`** on the graph ref so the layout re-runs with these values.
- **Engine:** `d3AlphaDecay` 0.02, `d3VelocityDecay` 0.25, `cooldownTicks` 450.

### 7. Fit view and initial layout

- **zoomToFit:** call `ref.current.zoomToFit(durationMs, padding)` with e.g. duration 500, padding 24.
- Call zoomToFit:
  - In **onEngineStop** after a short delay (e.g. 250 ms).
  - In a **fit-on-load** effect when graph has nodes and container dimensions are known, after ~2.6 s delay.
  - When the user clicks a **“Fit view”** button.
- Expose a **“Fit view”** button that calls the same `zoomToFit(500, 24)`.

### 8. Modes and UI

- **Contradiction mode:** when enabled, filter links to only `type === "contradiction"` for rendering; show “No contradiction data.” if there are no nodes/links or no contradiction links.
- **Show Clusters:** optional; color nodes by cluster (e.g. Louvain) using the cluster color list above.
- **Side panel:** on node click, show node details (title, year, main_problem, methods_used, datasets_used, key_findings). On contradiction link click, show “Contradictions detected” with Paper A vs Paper B and list of `contradictions` (claim, paperA_statement, paperB_statement).
- **Re-run intelligence:** button that triggers backend re-extraction and graph rebuild, then reload graph data.

### 9. Backend graph build (if replicating full pipeline)

- **Papers:** from DB/API by workspace.
- **Intelligence:** per-paper records with `embedding_vector`, `main_problem`, `methods_used`, `key_findings`, `datasets_used`, `keywords`, `domain`, `claims`.
- **Similarity:** cosine similarity between `embedding_vector`; add link only if ≥ 0.70.
- **Keyword overlap:** normalize keywords, remove academic stopwords; add paper–paper link if overlap ≥ 3.
- **Contradiction edges:** from claim_verifications where same run has both SUPPORT and CONTRADICT papers; one edge per (support_id, contradict_id) pair.
- **Method/dataset/concept/keypoint nodes:** create from `methods_used`, `datasets_used`, `keywords`, `key_findings`; add links paper → method, paper → dataset, paper → concept, paper → keypoint. Deduplicate by normalized label (concept/keypoint can use hash for id).
- **Citation:** match DOIs or titles from paper metadata to other papers in the workspace.
- No artificial “guarantee” links: only add edges that satisfy the above rules (isolated nodes stay isolated).

### 10. Exact constants summary

| Item | Value |
|------|--------|
| Background | `#1f2024` |
| Node default radius | 3 (paper: 6) |
| Node circle fill | `#7077A1` |
| Label font | 6/scale, clamp 3–10, Inter |
| Label color | `rgba(223, 208, 184, 0.85)` |
| Label wrap | 42 chars/line, 4 lines max |
| Charge strength | -90 |
| Charge distanceMax | 80 |
| Link distance | 36 |
| Link strength | 0.85 |
| Center strength | 2.2 |
| zoomToFit | (500, 24) |
| d3AlphaDecay | 0.02 |
| d3VelocityDecay | 0.25 |
| cooldownTicks | 450 |

---

Using this prompt, an implementation should match the graph in this project: Obsidian-like dark theme, compact centered layout, multi-line zoom-stable labels, type-colored nodes, contradiction and intelligence links, and reliable fit-to-view on load and on button click.

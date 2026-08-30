# Query Workflow

Answer user questions based on the knowledge base. Search relevant wiki pages and synthesize cited answers. Core idea: **every query should make the knowledge base better**.

> 📌 **Path convention**: `raw/` and `wiki/` in this document refer to the current knowledge base absolute paths, determined during SKILL.md routing (`KB_RAW`, `KB_WIKI`). `KB_LANG` is the current knowledge base language setting.

## Workflow

### 1. Understand the question

Analyze user input and classify:

- **Knowledge query** — normal knowledge question → continue steps 2-5
- **Preference/feedback** — preferences about how operations should work (e.g. "always cite sources in answers") → jump to step 4d
- **Answer correction** — correction of a previous answer (e.g. "you were wrong, it's actually XX") → step 4a to fix the corresponding wiki page
- **Preference + correction** — both (e.g. "answer was too shallow; XX should include YY") → 4a supplement content + 4d record preference

**Design principle**: the wiki is the memory. Content errors/gaps are fixed by updating wiki pages (next query answers correctly); no separate "lesson learned" store. `conventions.md` holds preference rules only, not correction history.

For normal knowledge queries, identify keywords, entities, and concepts involved.

### 2. Retrieve relevant pages

Search in order:
1. Read `wiki/index.md` and locate likely relevant pages by keywords
2. **Check whether `wiki/analyses/` already has related prior analysis** (avoid duplicate work; deepen existing analysis)
3. Read located wiki pages
4. If more context needed, Grep `wiki/` for keywords
5. If raw data is involved, consult materials under `raw/`

### 3. Synthesize answer

Based on retrieved information, produce a structured answer:
- Answer the question directly
- Cite specific wiki pages: `(see [[page-name]])`
- **If related prior analysis exists, deepen it** rather than starting from scratch
- If information is insufficient, state what the knowledge base lacks
- If contradictory information exists, list different claims from different sources

### 4. Knowledge write-back (self-evolution core)

After each query, evaluate whether the answer produced new knowledge:

#### 4a. Auto write-back (no user confirmation)

Update existing pages directly in these cases:
- **Supplement info**: answer synthesizes information not yet on an entity/concept page → append to that page, update `updated` date
- **New cross-references**: answer reveals links between pages not previously connected → add links in both Related sections
- **Minor fixes**: factual errors found during answering → fix directly

#### 4b. Suggested write-back (user confirmation)

Suggest to user; execute after confirmation:
- **Analysis worth its own page**: comparisons, syntheses, newly discovered connections → save under `wiki/analyses/`
- **New entity/concept**: important entity/concept not yet in wiki → suggest new page
- **Contradiction found**: contradiction between existing pages → suggest marking

Suggestion format:
```
📝 Knowledge updates from this query:

Auto-updated:
  - Updated [[memex]] page with comparison to modern RAG systems
  - Added cross-reference between [[vannevar-bush]] and [[knowledge-management]]

Suggested actions:
  - 💡 Save this comparison as wiki/analyses/memex-vs-rag.md?
  - 💡 Create new concept page wiki/concepts/rag.md for "RAG"?
```

#### 4d. User feedback write-back (automatic)

Triggered when user input is operational preference or feedback (not a knowledge query).

**Classification rules:**

| Category | Criteria | Examples |
|------|---------|------|
| Query | Answer style, output format, citation style | "Always cite sources", "Use tables for comparisons" |
| Ingest | Ingestion strategy, page splitting, naming preferences | "Don't create standalone pages for briefly mentioned concepts" |
| Lint | Check preferences, fix strategy | "Don't report P2 issues", "Auto-fix broken links without confirmation" |
| General | Cross-operation preferences | "Reply in English for all operations", "One-line summary after each operation" |

**Steps:**
1. Read `wiki/conventions.md` (create from initial template if missing)
2. Classify feedback and append as `- ` list items under the matching section
3. **Deduplicate**: if a semantically identical entry exists, update it instead of duplicating
4. **Refine**: if a section has > 10 items, merge similar entries into tighter rules
5. Update `updated` date
6. Tell the user which section was updated

> ⚠️ Do not store operational preferences in Claude Code memory; use the knowledge base's own `conventions.md`.

#### 4c. Write-back execution

After user confirms:
- Create new pages (full frontmatter and Related section)
- Update Related sections on related existing pages (bidirectional links)
- Update `wiki/index.md`
- Update `wiki/overview.md` if statistics changed
- Record in `wiki/log.md`: `## [YYYY-MM-DD] query | brief question summary`

### 5. Answer format

Choose the best format by question type:
- **Fact lookup**: short direct answer + citations
- **Comparison**: Markdown table
- **Synthesis**: structured long-form
- **Timeline**: chronological list
- **Overview**: hierarchical mind-map style list
- **Presentation**: Marp slide deck (good for reports and sharing)
- **Charts**: matplotlib visualizations (data comparison, trends)
- **Canvas**: Obsidian Canvas format (relationship/flow diagrams)

## Notes

- **Language**: use `KB_LANG`; answers and new pages use the target language
- Prefer synthesized wiki information over re-deriving from raw materials each time
- **Reuse prior analysis**: if analyses/ has related work, deepen it rather than repeat
- Clearly separate "information recorded in wiki" from "LLM's own knowledge"
- If the question is entirely outside the knowledge base, tell the user and suggest ingesting relevant materials
- Stay conservative on auto write-back: only add high-confidence information, not speculation

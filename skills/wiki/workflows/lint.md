# Lint Workflow

Health check the knowledge base, find issues, and provide fix suggestions.

> 📌 **Path convention**: `raw/` and `wiki/` in this document refer to the current knowledge base absolute paths, determined during SKILL.md routing (`KB_RAW`, `KB_WIKI`). `KB_LANG` is the current knowledge base language setting.

## Workflow

### 1. Run deterministic check script

**First** run `python <skill-dir>/scripts/lint.py --wiki-dir <KB_WIKI> --raw-dir <KB_RAW> --json` to get structural issues. The script covers:

- Broken links (`[[link]]` points to non-existent page)
- `[[raw/...]]` wikilink misuse (should use standard Markdown links)
- Frontmatter completeness (required fields, valid type)
- index.md consistency with actual files
- Bidirectional link integrity (A→B implies B→A)
- Orphan pages
- entity/concept pages missing sources field

Use script output as the basis for P0/P1 issues; **do not duplicate checks the script already covers**.

### 2. LLM supplemental checks

On top of script results, use LLM for **semantic issues scripts cannot detect**:

#### P1 — Quality (LLM supplement)
- **Language consistency**: using `KB_LANG`, check whether each page body uses the target language. List inconsistent pages and offer batch translation (translate page by page after user confirmation; preserve frontmatter and `[[links]]`)
- **Contradiction detection**: scan all `> ⚠️ Contradiction` markers and summarize known contradictions; also check for unmarked contradictory statements across pages
- **Missing pages**: concepts/entities referenced 3+ times via `[[link]]` but without standalone pages
- **Stale info**: pages with `updated` older than 30 days while newer ingested materials cover the same topic
- **Empty sections**: pages with `_to be filled_` or empty headings

#### P2 — Suggestions (LLM supplement)
- **Missing cross-references**: related content without mutual links
- **Tag inconsistency**: same concept under different tag names
- **Mergeable pages**: pages with highly overlapping content
- **New page suggestions**: suggested new entity/concept pages based on existing content
- **Knowledge gaps & expansion** (use WebSearch tool):
  1. Identify obvious gaps (e.g. themes referenced by many pages but shallow)
  2. Use **WebSearch** for latest developments, key papers, authoritative resources
  3. Output suggestions: gap description, recommended sources (title + link), ingestion priority
  4. Example format:
     ```
     🔍 Knowledge expansion suggestions (based on web search):
     - [[memex]] page mentions Ted Nelson's hypertext but lacks detail
       → Recommended: "Ted Nelson and the Xanadu Project" (https://...)
       → Priority: Medium
     - [[manufacturing-ai]] lacks 2026 latest developments
       → Recommended: "State of AI in Manufacturing 2026" (https://...)
       → Priority: High
     ```

### 3. Generate report

Output a structured check report:

```markdown
## Wiki Health Check Report (YYYY-MM-DD)

### 📊 Statistics
- Total pages: N
- Source summaries: N
- Entity pages: N
- Concept pages: N
- Analysis pages: N

### 🔴 P0 — Needs fixing
- [ ] Issue description → fix approach

### 🟡 P1 — Suggested improvements
- [ ] Issue description → improvement approach

### 🟢 P2 — Optional optimizations
- [ ] Suggestion description
```

### 4. Execute fixes

After showing the report:
- P0: suggest immediate fix; request user confirmation
- P1: confirm item by item
- P2: suggestions only

After user confirms, run fixes and update `wiki/log.md`.

## Notes

- Lint does not delete pages; only suggests merge or update
- If many issues, show in batches to avoid overload
- After each lint, record check summary in log.md

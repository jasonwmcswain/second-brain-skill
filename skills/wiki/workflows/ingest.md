# Ingest Workflow

Ingest new materials into the knowledge base. Runs fully automatically by default; only asks the user when human judgment is needed.

> 📌 **Path convention**: `raw/` and `wiki/` in this document refer to the current knowledge base absolute paths, determined during SKILL.md routing (`KB_RAW`, `KB_WIKI`). `KB_LANG` is the current knowledge base language setting.

## Core Principles

1. **Automation by default** — routine ingestion does not interrupt the user; run the full flow directly
2. **Ask only when needed** — use AskUserQuestion only for contradictions, ambiguities, or boundary judgments
3. **Structured storage** — pages go strictly into the correct directories by type; cross-references form a complete graph

## Workflow

### 1. Discover new materials

Read `wiki/index.md` to get the list of already-ingested materials, scan the `raw/` directory (excluding the `assets/` subdirectory), and find files not yet ingested.

If the user specified a filename, process only that file.

### 2. Read materials

Read each new material in turn:
- Markdown files: read directly
- PDF files: read with the Read tool
- Image files: view with the Read tool

#### Image handling

The LLM cannot process Markdown text and embedded images in a single read. For materials with images, handle in two steps:

1. **Read text first**: read Markdown/PDF and understand the main content
2. **Then view images**: scan for image paths in the text (`![](path)` or `![[path]]`), view each image with the Read tool, and extract supplementary information (chart data, architecture diagrams, flowcharts, etc.)

Integrate key information from images (data points, structure, flow) into the wiki page text; do not rely on images alone. If an image is important (e.g. architecture diagram, experiment results), reference it in the wiki page with standard Markdown image syntax: `![description](../../raw/assets/image-name)`.

### 3. Analyze and decide

After reading, analyze:
- Core points (3-5)
- Entity and concept pages to create/update
- Connections to existing knowledge
- Whether contradictions exist

**Decide whether to ask the user based on analysis:**

#### Auto-execute (no prompt) — all of the following must hold:
- No contradiction: new material does not conflict with existing wiki content
- Clear classification: each entity/concept type (entity vs concept) and directory placement is unambiguous
- No merge ambiguity: newly identified entities/concepts are not "possibly the same but uncertain" vs existing pages
- Reasonable scale: planned new pages ≤ 5

When auto-executing, briefly inform the user of the plan before creating pages (non-blocking):
```
Ingesting "<Material Title>" — planning to create N new pages, update M existing pages; running automatically...
```

#### Scenarios requiring user input — any of the following:

**Scenario A: Contradiction** — new material conflicts with existing content
```json
{
  "questions": [{
    "question": "\"<Material Title>\" contradicts existing content:\n\n· Existing: <existing page claim>\n· New material: <new material claim>\n\nHow to handle?",
    "header": "Content contradiction",
    "multiSelect": false,
    "options": [
      {"label": "Mark contradiction and keep both", "description": "Use ⚠️ contradiction marker; keep both claims (recommended)"},
      {"label": "Prefer new material", "description": "Update existing content to match new material"},
      {"label": "Keep old content", "description": "Ignore the contradictory part of new material"}
    ]
  }]
}
```

**Scenario B: Merge ambiguity** — unsure whether new concept/entity should merge with an existing page
```json
{
  "questions": [{
    "question": "New material mentions \"XX\" which may be the same as existing page [[yy]].\n\n· XX: <new material description>\n· yy: <existing page description>\n\nMerge?",
    "header": "Page merge",
    "multiSelect": false,
    "options": [
      {"label": "Merge into existing page", "description": "Integrate new info into [[yy]]"},
      {"label": "Create separate page", "description": "XX and yy are different concepts; maintain separately"},
      {"label": "Merge and rename", "description": "Merge content using a more accurate name"}
    ]
  }]
}
```

**Scenario C: Large-scale ingest** — planning > 5 new pages
```json
{
  "questions": [{
    "question": "\"<Material Title>\" is rich; many pages planned:\n\nNew: <list>\nUpdate: <list>\n\nChoose ingestion scope:",
    "header": "Ingestion scope",
    "multiSelect": false,
    "options": [
      {"label": "Ingest all (recommended)", "description": "Create all pages listed above"},
      {"label": "Core pages only", "description": "Create only the 3-5 most important pages"},
      {"label": "Summary page only", "description": "Create source page only; defer entity/concept split"}
    ]
  }]
}
```

**Multiple scenarios can combine**: if contradiction and merge ambiguity both exist, ask multiple questions in one AskUserQuestion (max 4).

### 4. Create source summary page

Create a summary page under `wiki/sources/` with a filename matching the raw file.

Template:
```markdown
---
title: Material Title
aliases: [Alternative names]
type: source
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [relevant tags]
raw_file: raw/original-filename
---

# Material Title

## Source Information

- **Raw file**: [raw/filename](../../raw/filename)
- **Type**: article/paper/report/...
- **Date**: material publication date (if available)
- **Author**: author (if available)

## Core Content

[3-5 paragraphs of key content summary]

## Key Points

- Point 1
- Point 2
- ...

## Quotes and Data

[Important data points, quotes, statistics]

## Related

- [[related-page]]
```

**Note**: link to raw files with standard Markdown `[text](path)`, not `[[wikilink]]`, to avoid phantom raw nodes in the Obsidian graph.

### 5. Create/update entity and concept pages

#### Directory structure

Store strictly by type for a clear graph and directory layout:

| Type | Directory | Criteria | Examples |
|------|------|---------|------|
| Entity | `wiki/entities/` | Named "things": people, orgs, tools, projects, products, datasets | vannevar-bush, forge-benchmark, openai |
| Concept | `wiki/concepts/` | Abstract ideas, methods, techniques, patterns, theories | memex, knowledge-management, reinforcement-learning |

**Rule of thumb**: if it can be referred to by a proper noun, it's an entity; if it needs "what is it?" explanation, it's a concept. When ambiguous, lean toward concept.

#### Create/update rules

**New pages**:
- Only create pages for entities/concepts discussed substantively (not in passing)
- Entities/concepts mentioned 1-2 times and not central need no page; mention briefly on related pages

**Update existing pages**:
- Append new information in the relevant section; do not overwrite existing content
- Update frontmatter `sources` list and `updated` date
- Add new links in the Related section

Template:
```markdown
---
title: Name
aliases: [Alternative names]
type: entity or concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tags]
sources: [referenced material filenames]
---

# Name

[Overview paragraph]

## Details

[Detailed content organized by topic]

## Related

- [[related-page]] — relationship description
```

### 6. Maintain graph integrity

Critical step to keep the knowledge graph connected:

**Bidirectional link rules**:
- If A's Related links to B, B's Related **must** link back to A
- Each entity/concept page's Related **must** include a backlink to the corresponding source summary page
- After creating a new page, scan **existing pages**; if they discuss the new topic without a link, add the link

**Cross-reference rules**:
- On first mention of another wiki topic in body text, use `[[wikilink]]`
- Related section lists all related pages with brief relationship notes (e.g. `— proposer`, `— source material`)

### 7. Update index and log

- Add new entries under the correct category in `wiki/index.md`
- Update statistics and recent activity in `wiki/overview.md`
- Append operation record at the top of `wiki/log.md` (after `# Wiki Log` heading)

### 8. Run deterministic check

After all pages are created/updated, run `python <skill-dir>/scripts/lint.py --wiki-dir <KB_WIKI> --raw-dir <KB_RAW>`. If the script reports P0 issues, fix them before ending the ingest flow.

Output ingestion summary when done:
```
✅ Ingest complete: "<Material Title>"
   Created: entities/xx.md, concepts/yy.md
   Updated: concepts/zz.md
   lint: passed
```

## Notes

- **Language**: all wiki pages are written in English. Keep proper nouns in original form regardless of source material language.
- **aliases**: every page frontmatter must include `aliases` for the Obsidian Front Matter Title plugin.
- Raw materials (files under `raw/`) are read-only — do not modify
- If material includes image references, record paths for later viewing
- Keep summaries objective; distinguish facts from opinions
- When new material contradicts existing content, use `> ⚠️ Contradiction` marker

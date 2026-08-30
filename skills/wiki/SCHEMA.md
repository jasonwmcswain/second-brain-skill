# Second Brain Schema

This file defines wiki page specifications and conventions. All workflows must follow it during execution.

## Language Settings

All wiki content is written in English (`KB_LANG` is always `en`). Keep proper nouns in their original form (e.g. "Memex", "Vannevar Bush").

Rules:
- New ingested materials produce English wiki pages
- The `title` field in frontmatter uses English
- Filenames always use lowercase English + hyphens

## Frontmatter Specification

Every wiki page must include YAML frontmatter:

```yaml
---
title: Page Title
aliases: [Alternative names]              # For Obsidian graph display
type: source | entity | concept | analysis | overview | conventions
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: [source_filename1, source_filename2]  # Referenced raw materials
---
```

## File Naming

- All lowercase English + hyphens: `reinforcement-learning.md`, `openai.md`
- Source summary pages share the same name as the raw file: `raw/paper-x.pdf` → `wiki/sources/paper-x.md`
- Avoid overly long filenames; keep under 50 characters

## Cross-References

- Use Obsidian wikilink syntax: `[[page-name]]` or `[[page-name|Display Text]]`
- Each page has a `## Related` section at the bottom listing all related links
- When creating a new page, check whether it should be added to existing pages' Related sections

## Content Guidelines

- Write all wiki content in English. Keep proper nouns in their original form
- State facts first and cite information sources
- When new materials contradict existing content, clearly mark with `> ⚠️ Contradiction: ...` and explain both sides
- Keep pages focused — one topic per page

## Index Format

`wiki/index.md` is organized by category:

```markdown
## Sources
- [Material Title](sources/filename.md) — One-line summary (YYYY-MM-DD)

## Entities
- [Entity Name](entities/filename.md) — One-line description [N source references]

## Concepts
- [Concept Name](concepts/filename.md) — One-line description

## Analyses
- [Analysis Title](analyses/filename.md) — One-line summary (YYYY-MM-DD)
```

## Log Format

`wiki/log.md` in reverse chronological order:

```markdown
## [YYYY-MM-DD] <operation> | <title>
- Specific operation description
- List of affected pages
```

operation values: `ingest`, `query`, `lint`, `update`, `init`, `wipe`

## Contradiction Handling

When new materials contradict existing wiki content:

1. **Do not delete old information** — preserve both viewpoints
2. **Mark contradictions** — use `> ⚠️ Contradiction: ...` callout in relevant paragraphs
3. **Cite sources** — attribute each side to its source material
4. **Note dates** — include dates for each piece of information to judge recency
5. **Leave judgment to the user** — if the contradiction involves a core argument, remind the user in discussion

# Second Brain Skill

LLM-built and maintained personal knowledge base. See [IDEA.md](IDEA.md) for design philosophy. Full user guide: [../../docs/user-guide.md](../../docs/user-guide.md).

## Quick Start

1. Install Claude Code and copy this skill to `~/.claude/skills/wiki`
2. `pip install -r scripts/requirements.txt`
3. Run `/wiki init` — choose path and name (English wiki content)
4. Place materials in `<kb>/raw/`, then `/wiki ingest`

## Commands

| Command | Function |
|---------|----------|
| `/wiki init` | Create and register a knowledge base |
| `/wiki ingest` | Ingest new materials |
| `/wiki query <question>` | Answer from the knowledge base |
| `/wiki lint` | Health check |
| `/wiki wipe` | Reset/delete (recycle bin supported) |
| `/wiki test` | Automated tests |

Natural language triggers work too — see [SKILL.md](SKILL.md) for routing.

## Directory Structure

```
~/.claude/skills/wiki/        # Skill (global install)
├── SKILL.md                  # Entry point and routing
├── SCHEMA.md                 # Page specification
├── registries.json           # KB registry (see registries.example.json)
├── workflows/                # Per-command workflows
└── scripts/                  # router.py, lint.py

~/my-kb/                      # KB instance (user path)
├── raw/                      # Raw materials (you write)
└── wiki/                     # LLM-maintained knowledge base
    ├── index.md, log.md, overview.md, conventions.md
    ├── sources/, entities/, concepts/, analyses/
```

## Three-Layer Architecture

| Layer | Location | Writer | Reader |
|-------|----------|--------|--------|
| Raw materials | `<kb>/raw/` | You | LLM |
| Knowledge base | `<kb>/wiki/` | LLM | You |
| Spec | Skill directory | You + LLM | LLM |

## Core Operations

**Ingest** — Scans `raw/`, creates/updates wiki pages, maintains cross-references. Auto-runs lint.py; fixes P0 issues. Asks only on conflicts or ambiguity.

**Query** — Reads index and relevant pages, synthesizes cited answers. Can write back new analyses to `wiki/analyses/`.

**Lint** — Deterministic checks via `lint.py` plus LLM semantic supplement. See [workflows/lint.md](workflows/lint.md).

**Wipe** — Moves pages to `wiki/.trash/` (recoverable). Never touches `raw/`.

## Page Specification

See [SCHEMA.md](SCHEMA.md) for frontmatter fields, naming conventions, and wikilink syntax.

## Obsidian

Open the KB root in Obsidian for graph view and backlinks. Recommended plugins: Front Matter Title, Dataview, Web Clipper. Graph filter: `-file:index -file:log -file:overview`

## Multi-KB

Multiple KBs are registered in `registries.json`. Set `"default"` to the active KB ID. See `registries.example.json` for format.

## Extension

For large wikis (>100 pages), consider [qmd](https://github.com/tobi/qmd) or custom search scripts under `scripts/`.

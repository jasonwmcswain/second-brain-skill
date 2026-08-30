---
name: wiki
version: v1.0.0
author: ChavesLiu
description: |
  Knowledge base management tool. Ingest materials, query knowledge, health checks, reset/delete.
  TRIGGER when: user mentions "ingest", "add to knowledge base", or similar ingestion intent; asks a question that may be answerable from the knowledge base (e.g. "what is XX", "compare XX and YY", "summarize info about XX"); requests "check the knowledge base", "lint"; asks to "clear", "delete", or "reset" knowledge base content; or gives feedback/preferences about how the knowledge base should be operated.
  DO NOT TRIGGER when: the question is unrelated to the knowledge base (pure coding tasks, file operations, general conversation), or the user explicitly says they do not need the knowledge base.
user-invocable: true
---

# Second Brain Skill

Unified entry for knowledge base management via `/wiki <cmd>` or natural language.

## Natural Language Routing

Map user intent to a subcommand, then pass the original input as `args`:

| Intent | Subcommand | Examples |
|--------|------------|----------|
| Ingest/add | `ingest` | "Ingest this article", "Add new files in raw" |
| Ask/query/compare | `query` | "What is Memex?", "Compare RAG and Wiki" |
| Feedback/preferences | `query` (feedback) | "Always cite sources", "You were wrong last time" |
| Check/audit | `lint` | "Check the knowledge base" |
| Delete/clear/reset | `wipe` | "Delete pages about XX", "Reset the KB" |
| Initialize | `init` | "Create a new knowledge base" |

## Execution Steps

### 1. Run router

`python <skill-dir>/scripts/router.py <subcommand> [args]` → JSON result.

### 2. Branch on `status`

#### `ok` — Execute workflow

Fields: `subcommand`, `args`, `workflow`, `schema`, `kb` (id, name, root, wiki, raw, lang), `skill_dir`, optional `multiple_kbs` / `kb_list`.

1. If `schema` set → read `<skill_dir>/<schema>`
2. If `<kb.wiki>/conventions.md` exists → read as KB-specific constraints
3. Read `<skill_dir>/<workflow>`
4. Replace `KB_ROOT`, `KB_WIKI`, `KB_RAW`, `KB_LANG` with values from `kb`
5. Execute workflow with `args`, respecting conventions.md
6. If `multiple_kbs`, tell user which KB is active (change default in registries.json)

#### `select` — Ask user to pick from `kb_list`, then update `default` in registries.json

#### `no_kb` — Output `⚠️ {message}`

#### `error` — Output error message

#### `help` — Output:

```
Second Brain — LLM-powered knowledge base management tool

Commands:
  /wiki init                  Create and register a new knowledge base
  /wiki ingest [filename]     Ingest new materials from raw/ (all if unspecified)
  /wiki query <question>      Answer questions based on the knowledge base
  /wiki lint                  Knowledge base health check
  /wiki wipe [subcommand]     Reset/delete (all | <keyword> | trash | restore | empty-trash)
  /wiki test                  Automated testing
  /wiki help                  Show this help

Run /wiki init first if this is your first time
```

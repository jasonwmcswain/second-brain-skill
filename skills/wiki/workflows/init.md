# Init Workflow

Create and register a new knowledge base.

## Workflow

### 1. Collect information

Use AskUserQuestion to ask for the following:

```json
{
  "questions": [
    {
      "question": "Knowledge base root directory path? (raw/ and wiki/ subdirectories will be created here)",
      "header": "Path",
      "multiSelect": false,
      "options": [
        {"label": "Current directory", "description": "Use the current working directory as the knowledge base root"},
        {"label": "Custom path", "description": "Specify an absolute path"}
      ]
    },
    {
      "question": "Name for this knowledge base (shown when switching between multiple KBs)",
      "header": "Name",
      "multiSelect": false,
      "options": [
        {"label": "AI Research", "description": ""},
        {"label": "Book Notes", "description": ""},
        {"label": "Work Knowledge Base", "description": ""}
      ]
    }
  ]
}
```

Wiki pages are always written in English (`language: "en"`).

### 2. Generate knowledge base ID

Generate a slug from the name as ID (e.g. "AI Research" → "ai-research"). If the ID already exists in registries.json, prompt the user to change it.

### 3. Create directory structure

Create under the target path:

```bash
mkdir -p <path>/raw/assets
mkdir -p <path>/wiki/sources
mkdir -p <path>/wiki/entities
mkdir -p <path>/wiki/concepts
mkdir -p <path>/wiki/analyses
```

### 4. Initialize wiki core files

Create the following files (if they do not exist):

#### `<path>/wiki/index.md`

```markdown
# Wiki Index

> This file is auto-maintained by the LLM and serves as the wiki content directory. Organizes all pages by category with a one-line summary each.
> The LLM reads this file first when answering queries to locate relevant pages.

## Overview

- [Overview](overview.md) — Wiki overview and current knowledge graph summary
- [Conventions](conventions.md) — User preferences for operating this knowledge base

## Sources

## Entities

## Concepts

## Analyses
```

#### `<path>/wiki/log.md`

```markdown
# Wiki Log

> Operation log recording all wiki operations in reverse chronological order.

## [YYYY-MM-DD] init | Knowledge base initialized

- Created knowledge base directory structure
- Initialized index.md, log.md, overview.md, conventions.md
```

(Replace YYYY-MM-DD with today's date)

#### `<path>/wiki/overview.md`

```markdown
---
title: Overview
aliases: [Overview]
type: overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [overview]
---

# Knowledge Base Overview

## Statistics

| Metric | Count |
|------|------|
| Raw materials | 0 |
| Source summaries | 0 |
| Entity pages | 0 |
| Concept pages | 0 |
| Analysis pages | 0 |

## Knowledge Graph Summary

(No content yet — will auto-update after ingesting materials)

## Recent Activity

- [YYYY-MM-DD] Knowledge base initialized
```

#### `<path>/wiki/conventions.md`

```markdown
---
title: Conventions
aliases: [Conventions]
type: conventions
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [meta]
---

# Conventions

> This page records user preferences and conventions for operating this knowledge base. The LLM should read this page before any operation.

## Query

(None yet)

## Ingest

(None yet)

## Lint

(None yet)

## General

(None yet)
```

### 5. Register in registries.json

Read `registries.json` in the skill directory and add a new entry:

```json
{
  "default": "<new-id>",
  "registries": {
    "<new-id>": {
      "name": "User-provided name",
      "path": "/absolute/path/to/kb",
      "language": "en",
      "created": "YYYY-MM-DD"
    }
  }
}
```

Set `default` to the newly created knowledge base ID.

### 6. Handle existing directory

If the target path already exists and contains `raw/` and `wiki/` subdirectories:

```json
{
  "questions": [{
    "question": "Target path already has a knowledge base structure (contains raw/ and wiki/). How to proceed?",
    "header": "Existing directory",
    "multiSelect": false,
    "options": [
      {"label": "Register only", "description": "Skip creation; register the existing knowledge base in config"},
      {"label": "Re-initialize", "description": "Recreate wiki core files (raw/ is left untouched)"},
      {"label": "Cancel", "description": "Do nothing"}
    ]
  }]
}
```

### 7. Output result

```
✅ Knowledge base created and registered

  Name: <name>
  Path: <path>
  Language: en
  ID:   <id>

  Directory structure:
    <path>/raw/          ← Place materials here
    <path>/wiki/         ← LLM-maintained knowledge base

  Next steps:
    1. Place material files in <path>/raw/
    2. Run /wiki ingest to start ingesting
```

# Wipe Workflow

Clear or delete knowledge base content. All deletes require user confirmation; files move to recycle bin and are recoverable.

> 📌 **Path convention**: `raw/` and `wiki/` in this document refer to the current knowledge base absolute paths, determined during SKILL.md routing (`KB_RAW`, `KB_WIKI`).

## Core Principles

1. **Human confirmation** — all deletes must list files and execute only after user confirmation
2. **Recycle bin** — delete = move to `wiki/.trash/`, not permanent delete; supports restore
3. **Never touch raw materials** — `raw/` directory is never modified
4. **Clean associations** — when deleting pages, sync cleanup of index.md, overview.md, and Related links on other pages

## Recycle Bin

Path: `wiki/.trash/`

- Preserve original directory structure on delete, e.g. `wiki/concepts/swiglu.md` → `wiki/.trash/concepts/swiglu.md`
- On name conflict, add timestamp suffix to old file: `swiglu.2026-04-13.md`
- On restore, move back to original path and re-update index.md, overview.md, Related on linked pages
- User can `/wiki wipe trash` to view recycle bin, `/wiki wipe restore` to restore, `/wiki wipe empty-trash` to permanently empty recycle bin

## Usage

- `/wiki wipe` — interactive mode
- `/wiki wipe all` — full reset
- `/wiki wipe <keyword>` — delete matching pages
- `/wiki wipe trash` — view recycle bin
- `/wiki wipe restore` — restore pages from recycle bin
- `/wiki wipe empty-trash` — permanently empty recycle bin

## Workflow

### 1. Determine operation mode

#### No arguments — interactive selection

```json
{
  "questions": [{
    "question": "Choose knowledge base operation:",
    "header": "Operation type",
    "multiSelect": false,
    "options": [
      {"label": "Full reset", "description": "Move all wiki pages to recycle bin; return to initial state (raw/ unaffected)"},
      {"label": "Delete specific material", "description": "Delete one material and its derived pages (moved to recycle bin)"},
      {"label": "Delete specific pages", "description": "Delete one or more entity/concept/analysis pages (moved to recycle bin)"},
      {"label": "View/restore recycle bin", "description": "View recycle bin contents and restore deleted pages"}
    ]
  }]
}
```

### 2. Full reset flow

#### 2a. Inventory current content

Read `wiki/index.md` and count files to move to recycle bin:
- `wiki/sources/*.md`
- `wiki/entities/*.md`
- `wiki/concepts/*.md`
- `wiki/analyses/*.md`

#### 2b. Confirmation (required)

```json
{
  "questions": [{
    "question": "Confirm full reset? The following N files will move to recycle bin (wiki/.trash/):\n\nSource summaries: X\nEntity pages: X\nConcept pages: X\nAnalysis pages: X\n\n⚠️ Recoverable via /wiki wipe restore\n⚠️ raw/ directory unaffected",
    "header": "Confirm reset",
    "multiSelect": false,
    "options": [
      {"label": "Confirm reset", "description": "Move all wiki pages to recycle bin; reset index/overview"},
      {"label": "Cancel", "description": "Do nothing"}
    ]
  }]
}
```

#### 2c. Execute reset

After user confirms:

1. **Create recycle bin directories** (if missing): `mkdir -p wiki/.trash/{sources,entities,concepts,analyses}`

2. **Move all content pages to recycle bin**:
   ```bash
   mv wiki/sources/*.md wiki/.trash/sources/
   mv wiki/entities/*.md wiki/.trash/entities/
   mv wiki/concepts/*.md wiki/.trash/concepts/
   mv wiki/analyses/*.md wiki/.trash/analyses/
   ```
   On name conflict, add timestamp suffix before moving.

3. **Reset index.md** to empty index template:
   ```markdown
   # Wiki Index

   > This file is auto-maintained by the LLM and serves as the wiki content directory. Organizes all pages by category with a one-line summary each.
   > The LLM reads this file first when answering queries to locate relevant pages.

   ## Overview

   - [Overview](overview.md) — Wiki overview and current knowledge graph summary

   ## Sources

   ## Entities

   ## Concepts

   ## Analyses
   ```

4. **Reset overview.md**: keep frontmatter, zero statistics, clear graph summary and recent activity.

5. **Append to top of log.md**:
   ```markdown
   ## [YYYY-MM-DD] wipe | Full reset

   - Moved to recycle bin: X source summaries, X entities, X concepts, X analyses
   - Reset index.md and overview.md
   - Recoverable via /wiki wipe restore
   ```

6. **Output result**:
   ```
   ✅ Knowledge base reset
      Moved to recycle bin: N pages
      raw/ preserved: M materials available for re-/wiki ingest
      💡 /wiki wipe restore to recover
   ```

### 3. Selective delete flow

#### 3a. Determine delete targets

**Delete by material**:
1. Read `wiki/index.md`, list materials for user selection (or match by keyword)
2. Find source summary page `wiki/sources/xxx.md`
3. Analyze impact:
   - "Will delete": pages produced only by this material (`sources` field contains only this material)
   - "Will update": pages also referenced by other materials (keep but remove association)

**Delete by page**:
1. User specifies or selects pages to delete from list
2. Analyze which other pages' Related sections reference target pages

#### 3b. Confirmation (required)

```json
{
  "questions": [{
    "question": "Deleting \"<target>\" will have the following impact:\n\n🗑️ Move to recycle bin:\n- wiki/sources/xxx.md\n- wiki/entities/yyy.md (only referenced by this material)\n\n✏️ Will update (remove association):\n- wiki/concepts/zzz.md (other materials still reference; keep page)\n\nConfirm?",
    "header": "Confirm delete",
    "multiSelect": false,
    "options": [
      {"label": "Confirm delete", "description": "Execute delete and updates above"},
      {"label": "Delete summary page only", "description": "Delete source page only; keep all entity/concept pages"},
      {"label": "Cancel", "description": "Do nothing"}
    ]
  }]
}
```

#### 3c. Execute delete

After user confirms:

1. **Move target pages to recycle bin** (preserve directory structure)
2. **Update affected pages**:
   - Remove deleted material from `sources` frontmatter
   - Remove links to deleted pages from Related sections
   - Update `updated` date
3. **Update index.md** — remove deleted page entries
4. **Update overview.md** — update statistics and knowledge graph summary
5. **Append record at top of log.md**
6. **Run `python <skill-dir>/scripts/lint.py --wiki-dir <KB_WIKI> --raw-dir <KB_RAW>`** to check for new broken links or orphans
7. **Output result**:
   ```
   ✅ Delete complete
      Moved to recycle bin: N pages
      Updated: M pages (associations removed)
      lint: passed
      💡 /wiki wipe restore to recover
   ```

### 4. Recycle bin operations

#### `/wiki wipe trash` — view recycle bin

Scan `wiki/.trash/` and list all files by category with original paths. If empty, say "Recycle bin is empty".

#### `/wiki wipe restore` — restore pages

1. List all files in recycle bin for user selection (multi-select supported)
2. **Confirm restore**: show files to restore; execute after confirmation
3. Execute restore:
   - Move files from `wiki/.trash/` back to original paths
   - Re-add entries in index.md
   - Re-add links in Related sections on related pages
   - Update overview.md statistics
   - Append restore record in log.md
4. Run `python <skill-dir>/scripts/lint.py --wiki-dir <KB_WIKI> --raw-dir <KB_RAW>` to verify consistency after restore

#### `/wiki wipe empty-trash` — permanently empty recycle bin

1. List all recycle bin files
2. **Confirm**: ⚠️ irreversible (unless git recovery); require user confirmation
3. After confirmation: `rm -rf wiki/.trash/*`

## Notes

- **Never delete raw/** — raw materials are not wiki content; read-only
- **log.md append only** — reset history is valuable
- Recycle bin directory `wiki/.trash/` should be in `.gitignore` to avoid version-controlling trash
- If user wants to clear raw/, they must do it manually; skill advises but does not execute

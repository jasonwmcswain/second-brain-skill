# Test Workflow

Automated tests for the three core workflows (ingest, query, lint) to verify architecture integrity.

> 📌 **Path convention**: `raw/` and `wiki/` in this document refer to the current knowledge base absolute paths, determined during SKILL.md routing (`KB_RAW`, `KB_WIKI`). Select target knowledge base via KB selection or `/wiki init` before testing.

## Test Flow

### Test 1: Architecture integrity check

Verify directory structure and core files exist:

```
Checks:
- [ ] raw/ directory exists
- [ ] raw/assets/ directory exists
- [ ] wiki/ directory exists
- [ ] wiki/sources/ directory exists
- [ ] wiki/entities/ directory exists
- [ ] wiki/concepts/ directory exists
- [ ] wiki/analyses/ directory exists
- [ ] wiki/index.md exists with correct category headings
- [ ] wiki/log.md exists with initial record
- [ ] wiki/overview.md exists with frontmatter
- [ ] <skill-dir>/SCHEMA.md exists with schema definitions
- [ ] <skill-dir>/SKILL.md exists
- [ ] <skill-dir>/workflows/ingest.md exists
- [ ] <skill-dir>/workflows/query.md exists
- [ ] <skill-dir>/workflows/lint.md exists
- [ ] <skill-dir>/workflows/wipe.md exists
- [ ] <skill-dir>/scripts/lint.py exists
```

Verify each item with Glob and Read tools; report results.

### Test 2: Ingest workflow test

1. Check whether test material `raw/test-sample.md` exists under `raw/`
2. If missing, create test material:
   ```markdown
   # Vannevar Bush and the Memex Vision

   In 1945, Vannevar Bush proposed the concept of Memex in "As We May Think"...
   (includes entities: Vannevar Bush, Memex; concepts: associative memory, knowledge management)
   ```
3. Execute ingest flow (logic of /wiki ingest test-sample.md)
4. Verify:
   - [ ] `wiki/sources/test-sample.md` was created
   - [ ] File has correct frontmatter
   - [ ] `wiki/index.md` was updated with new entry
   - [ ] `wiki/log.md` was updated with ingest record
   - [ ] `wiki/overview.md` source_count was updated

### Test 3: Query workflow test

1. Run query: "What is Memex?"
2. Verify:
   - [ ] Answer cites relevant wiki pages
   - [ ] Answer includes `[[` page references
   - [ ] Answer is based on knowledge base content, not LLM's own knowledge alone

### Test 4: Lint workflow test

1. Run lint check
2. Verify:
   - [ ] Structured report was generated
   - [ ] Report includes statistics
   - [ ] Report is categorized by priority
   - [ ] Any issues from testing are detected (e.g. missing cross-references)

### Test 5: Cleanup

After tests, ask user whether to keep test data:
- Keep: test materials remain in wiki as examples
- Clean up: delete all test-produced files; restore index.md and log.md

## Result Summary

```
========================================
  Wiki Automated Test Report
========================================
  Architecture integrity:    ✅/❌ (N/M passed)
  Ingest workflow:           ✅/❌ (N/M passed)
  Query workflow:            ✅/❌ (N/M passed)
  Lint workflow:             ✅/❌ (N/M passed)
========================================
  Total: N/M passed
========================================
```

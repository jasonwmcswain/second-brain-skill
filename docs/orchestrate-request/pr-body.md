## Summary

Comprehensive review and refinement of second-brain-skill per goals: English-only, streamlined skill/docs, improved usability, performance optimization, and security hardening.

## Changes

### English-only conversion
- Replaced all Chinese content with English across SKILL.md, workflows, SCHEMA.md, scripts, README, and user guide
- Removed duplicate `.en.md` files (README.en.md, user-guide.en.md, skills/wiki/README.en.md)
- Default language changed from `zh` to `en`
- Verified: zero CJK characters remain in repo

### Security hardening
- **router.py**: Validate `registries.json` structure (name/path must be non-empty strings)
- **router.py**: Reject path traversal (`..`) in knowledge base paths
- **router.py**: Resolve paths to absolute before use; clear error messages on invalid JSON/paths
- Added `registries.example.json` template for safe setup

### Performance
- **lint.py**: Cache parsed frontmatter and file content per page — eliminates redundant `read_text()` calls across 8 check functions

### Streamlined documentation
- Condensed SKILL.md (~30% shorter) while preserving routing/execution logic
- Trimmed skills/wiki/README.md (removed ~300 lines of duplication)
- README and user-guide aligned to English-only, fork URL updated
- init workflow defaults to English only

### Dependencies
- Pinned `PyYAML==6.0.2` in requirements.txt

## Security review notes

| Severity | Issue | Status |
|----------|-------|--------|
| Medium | Unvalidated KB paths in registries.json | Fixed |
| Medium | Malformed registries.json could crash router | Fixed |
| Low | wipe workflow relies on LLM confirmation | By design |
| Low | lint.py accepts arbitrary wiki-dir via CLI | By design |

## Test plan
- [x] `python3 -m py_compile router.py lint.py`
- [x] CJK character grep clean
- [ ] `/wiki init` → `/wiki ingest` → `/wiki query` smoke test
- [ ] `/wiki lint` on sample KB

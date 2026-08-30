# Orchestrate Request: second-brain-skill Review & Refinement

**Context:** Review forked copy of https://github.com/jasonwmcswain/second-brain-skill  
**Started:** 2026-08-30  
**Goals:** English-only, streamlined skill, optimized performance/usability, streamlined docs, security review

## Task Decomposition

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Clone repo | Orchestrator | ✅ Done | Cloned to `/workspace/second-brain-skill` |
| 2 | Remove all non-English text | Subagent: english-only | ✅ Done | Commit `dadb678`, 16 files, -2579 lines |
| 3 | Security review (skill + scripts) | Subagent: security-review | ✅ Done | See Findings below |
| 4 | Improvement opportunities review | Subagent: explore | ✅ Done | See Findings below |
| 5 | Refine repo per goals | Subagent: refine | ✅ Done | Commit `21fc453`, 11 files |
| 6 | Create PR to fork | Orchestrator | ⚠️ Blocked | No GitHub push credentials in cloud env |

## Repo Snapshot (pre-change)

- **Branch:** main @ 0a06755
- **Structure:** `skills/wiki/` (SKILL.md, workflows, scripts), bilingual README/docs
- **Non-English files detected:** README.md, user-guide.md, SKILL.md, workflows/*.md, scripts (comments), SCHEMA.md, README.en.md pairs

## Findings

### Security Review

| Severity | Issue | Resolution |
|----------|-------|------------|
| Medium | `registries.json` paths not validated — arbitrary path read possible | Fixed: path traversal rejection + absolute path validation in router.py |
| Medium | Malformed `registries.json` could crash router | Fixed: schema validation + JSON error handling |
| Low | `wipe` workflow destructive ops rely on LLM confirmation | Accepted: workflow mandates user confirmation + recycle bin |
| Low | `lint.py` accepts arbitrary `--wiki-dir` | Accepted: LLM invokes with router-provided trusted paths |
| Info | `yaml.safe_load` used in lint.py | Already safe |
| Info | No secrets/credentials in repo | Clean |

### Improvement Opportunities (implemented)

| Category | Change | Impact |
|----------|--------|--------|
| Streamline | Condensed SKILL.md (~30% shorter) | High |
| Streamline | Trimmed skills/wiki/README.md (-300 lines duplication) | High |
| Docs | English-only, removed bilingual toggles | High |
| Usability | Default language `en`, registries.example.json added | Medium |
| Performance | lint.py caches parsed frontmatter per page | Medium |
| Security | Path validation in router.py | Medium |
| Deps | Pinned PyYAML==6.0.2 | Low |

## Decisions

- English `.en.md` files promoted to primary; Chinese originals deleted
- Default KB language: `en` (was `zh`)
- Fork URL in README updated to `jasonwmcswain/second-brain-skill`
- PR could not be auto-created: cloud env lacks GitHub credentials

## PR

**Branch:** `cursor/english-only-refine-f6ca` (2 commits ahead of main)

**To push and open PR locally:**
```bash
cd second-brain-skill
git push -u origin cursor/english-only-refine-f6ca
gh pr create --base main --head cursor/english-only-refine-f6ca \
  --title "refactor: English-only, streamlined skill with security hardening" \
  --body-file docs/orchestrate-request/pr-body.md
```

**Or apply from bundle:**
```bash
git clone https://github.com/jasonwmcswain/second-brain-skill.git
cd second-brain-skill
git pull /path/to/second-brain-skill-refine.bundle cursor/english-only-refine-f6ca
git push -u origin cursor/english-only-refine-f6ca
```

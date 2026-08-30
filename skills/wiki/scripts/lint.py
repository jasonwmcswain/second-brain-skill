#!/usr/bin/env python3
"""
Second Brain deterministic health check script.
Detects structural issues with code and outputs JSON for /wiki lint.

Usage:
    python lint.py --wiki-dir /path/to/kb/wiki --raw-dir /path/to/kb/raw
    python lint.py --wiki-dir /path/to/kb/wiki --raw-dir /path/to/kb/raw --json
"""

import argparse
import re
import sys
import json
import yaml
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass

REQUIRED_FRONTMATTER = {"title", "type", "created", "updated", "tags"}
VALID_TYPES = {"source", "entity", "concept", "analysis", "overview", "conventions"}
SPECIAL_PAGES = {"index.md", "log.md"}

# Set via command-line arguments
WIKI_DIR: Path
RAW_DIR: Path

# ---------- helpers ----------

@dataclass
class PageContent:
    path: Path
    text: str
    frontmatter: dict | None
    body: str


def parse_frontmatter_text(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter_dict, body_text). Returns (None, full_text) on parse failure."""
    m = re.match(r"^---\n(.*?\n)---\n(.*)", text, re.DOTALL)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1))
        return fm if isinstance(fm, dict) else None, m.group(2)
    except yaml.YAMLError:
        return None, text


def load_page_contents(pages: list[Path]) -> dict[Path, PageContent]:
    """Read and parse each page once for reuse across checks."""
    contents = {}
    for page in pages:
        text = page.read_text(encoding="utf-8")
        fm, body = parse_frontmatter_text(text)
        contents[page] = PageContent(path=page, text=text, frontmatter=fm, body=body)
    return contents


def parse_frontmatter(filepath: Path) -> tuple[dict | None, str]:
    """Return (frontmatter_dict, body_text). Returns (None, full_text) on parse failure."""
    text = filepath.read_text(encoding="utf-8")
    return parse_frontmatter_text(text)


def extract_wikilinks(text: str) -> list[str]:
    """Extract target from all [[target]] or [[target|alias]] wikilinks."""
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text)


def resolve_wikilink(target: str) -> Path | None:
    """Resolve wikilink target to a file path under wiki/."""
    for subdir in ["sources", "entities", "concepts", "analyses", ""]:
        candidate = WIKI_DIR / subdir / f"{target}.md" if subdir else WIKI_DIR / f"{target}.md"
        if candidate.exists():
            return candidate
    return None


def get_wiki_pages() -> list[Path]:
    """Get all wiki pages (excluding index.md and log.md)."""
    pages = []
    for f in WIKI_DIR.rglob("*.md"):
        if f.name not in SPECIAL_PAGES:
            pages.append(f)
    return sorted(pages)


def page_id(filepath: Path) -> str:
    """Extract wikilink-usable ID from file path (e.g. concepts/memex.md → memex)."""
    return filepath.stem


# ---------- checks ----------

def check_broken_links(pages: list[Path], contents: dict[Path, PageContent]) -> list[dict]:
    """P0: Check broken links — [[link]] points to non-existent wiki page."""
    issues = []
    all_ids = {p.stem for p in pages}

    for page in pages:
        links = extract_wikilinks(contents[page].text)
        for target in links:
            if target.startswith("raw/"):
                continue
            if target not in all_ids:
                issues.append({
                    "level": "P0",
                    "type": "broken_link",
                    "file": str(page.relative_to(WIKI_DIR)),
                    "detail": f"[[{target}]] points to non-existent page",
                })
    return issues


def check_raw_wikilinks(pages: list[Path], contents: dict[Path, PageContent]) -> list[dict]:
    """P0: Check [[raw/...]] wikilinks — should use standard Markdown links."""
    issues = []
    for page in pages:
        matches = re.findall(r"\[\[(raw/[^\]|]+)(?:\|[^\]]+)?\]\]", contents[page].text)
        for m in matches:
            issues.append({
                "level": "P0",
                "type": "raw_wikilink",
                "file": str(page.relative_to(WIKI_DIR)),
                "detail": f"[[{m}]] should be a standard Markdown link to avoid phantom graph nodes",
            })
    return issues


def check_frontmatter(pages: list[Path], contents: dict[Path, PageContent]) -> list[dict]:
    """P0: Check frontmatter completeness."""
    issues = []
    for page in pages:
        fm = contents[page].frontmatter
        rel = str(page.relative_to(WIKI_DIR))
        if fm is None:
            issues.append({
                "level": "P0",
                "type": "no_frontmatter",
                "file": rel,
                "detail": "Missing YAML frontmatter",
            })
            continue
        missing = REQUIRED_FRONTMATTER - set(fm.keys())
        if missing:
            issues.append({
                "level": "P0",
                "type": "incomplete_frontmatter",
                "file": rel,
                "detail": f"Missing fields: {', '.join(sorted(missing))}",
            })
        if fm.get("type") and fm["type"] not in VALID_TYPES:
            issues.append({
                "level": "P1",
                "type": "invalid_type",
                "file": rel,
                "detail": f"type '{fm['type']}' is not in valid values {VALID_TYPES}",
            })
    return issues


def check_index_consistency(pages: list[Path]) -> list[dict]:
    """P0: Check index.md consistency with actual files."""
    issues = []
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        issues.append({
            "level": "P0",
            "type": "missing_index",
            "file": "index.md",
            "detail": "index.md does not exist",
        })
        return issues

    index_text = index_path.read_text(encoding="utf-8")
    index_refs = set(re.findall(r"\]\(([^)]+\.md)\)", index_text))

    content_pages = set()
    for page in pages:
        rel = str(page.relative_to(WIKI_DIR))
        if rel in ("overview.md",):
            continue
        if any(rel.startswith(d) for d in ("sources/", "entities/", "concepts/", "analyses/")):
            content_pages.add(rel)

    for ref in index_refs:
        full_path = WIKI_DIR / ref
        if not full_path.exists() and ref != "overview.md":
            issues.append({
                "level": "P0",
                "type": "index_dangling",
                "file": "index.md",
                "detail": f"Index references {ref} but file does not exist",
            })

    for rel in content_pages:
        if rel not in index_refs:
            issues.append({
                "level": "P0",
                "type": "index_missing",
                "file": "index.md",
                "detail": f"File {rel} exists but is not listed in index",
            })

    return issues


def check_bidirectional_links(pages: list[Path], contents: dict[Path, PageContent]) -> list[dict]:
    """P1: Check bidirectional links — if A's Related links to B, B's Related should link back to A."""
    issues = []
    related_links = {}
    page_map = {p.stem: p for p in pages}

    for page in pages:
        pid = page.stem
        related_match = re.search(
            r"## Related\n(.*?)(?:\n## |\Z)", contents[page].text, re.DOTALL
        )
        if not related_match:
            continue
        related_section = related_match.group(1)
        targets = extract_wikilinks(related_section)
        related_links[pid] = set(targets)

    checked = set()
    for pid, targets in related_links.items():
        for target in targets:
            pair = tuple(sorted([pid, target]))
            if pair in checked:
                continue
            checked.add(pair)

            if target in related_links and pid not in related_links[target]:
                if target in page_map:
                    issues.append({
                        "level": "P1",
                        "type": "missing_reverse_link",
                        "file": str(page_map[target].relative_to(WIKI_DIR)),
                        "detail": f"Related section missing backlink to [[{pid}]] ({pid} already links to this page)",
                    })

    return issues


def check_orphan_pages(pages: list[Path], contents: dict[Path, PageContent]) -> list[dict]:
    """P1: Check orphan pages — no inbound links (except from index.md and overview.md)."""
    issues = []
    incoming = defaultdict(set)

    for page in pages:
        pid = page.stem
        links = extract_wikilinks(contents[page].text)
        for target in links:
            incoming[target].add(pid)

    for special in ("index.md", "overview.md"):
        sp = WIKI_DIR / special
        if sp.exists():
            for target in extract_wikilinks(sp.read_text(encoding="utf-8")):
                incoming[target].add(f"__{special}__")

    for page in pages:
        pid = page.stem
        rel = str(page.relative_to(WIKI_DIR))
        if rel == "overview.md":
            continue
        real_incoming = {s for s in incoming.get(pid, set()) if not s.startswith("__")}
        if not real_incoming:
            issues.append({
                "level": "P1",
                "type": "orphan_page",
                "file": rel,
                "detail": "Orphan page — no other wiki pages link here",
            })

    return issues


def check_sources_field(pages: list[Path], contents: dict[Path, PageContent]) -> list[dict]:
    """P1: Check entity/concept pages have sources field."""
    issues = []
    for page in pages:
        fm = contents[page].frontmatter
        if fm is None:
            continue
        ptype = fm.get("type", "")
        if ptype in ("entity", "concept") and not fm.get("sources"):
            issues.append({
                "level": "P1",
                "type": "missing_sources",
                "file": str(page.relative_to(WIKI_DIR)),
                "detail": f"type={ptype} but missing sources field (should cite referenced raw materials)",
            })
    return issues


# ---------- main ----------

def run_all_checks() -> list[dict]:
    pages = get_wiki_pages()
    contents = load_page_contents(pages)
    issues = []
    issues += check_broken_links(pages, contents)
    issues += check_raw_wikilinks(pages, contents)
    issues += check_frontmatter(pages, contents)
    issues += check_index_consistency(pages)
    issues += check_bidirectional_links(pages, contents)
    issues += check_orphan_pages(pages, contents)
    issues += check_sources_field(pages, contents)
    level_order = {"P0": 0, "P1": 1, "P2": 2}
    issues.sort(key=lambda x: (level_order.get(x["level"], 9), x["file"]))
    return issues


def main():
    parser = argparse.ArgumentParser(description="Second Brain health check")
    parser.add_argument("--wiki-dir", required=True, help="Absolute path to wiki directory")
    parser.add_argument("--raw-dir", required=True, help="Absolute path to raw directory")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON format")
    args = parser.parse_args()

    global WIKI_DIR, RAW_DIR
    WIKI_DIR = Path(args.wiki_dir).resolve()
    RAW_DIR = Path(args.raw_dir).resolve()

    if not WIKI_DIR.exists():
        print(f"Error: wiki directory does not exist: {WIKI_DIR}", file=sys.stderr)
        sys.exit(2)

    issues = run_all_checks()

    if args.output_json:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
        return

    pages = get_wiki_pages()
    p0 = [i for i in issues if i["level"] == "P0"]
    p1 = [i for i in issues if i["level"] == "P1"]
    p2 = [i for i in issues if i["level"] == "P2"]

    print(f"Wiki health check — {WIKI_DIR}")
    print(f"{len(pages)} pages total\n")

    if not issues:
        print("✅ No issues found!")
        return

    if p0:
        print(f"🔴 P0 — Needs fixing ({len(p0)})")
        for i in p0:
            print(f"  [{i['type']}] {i['file']}: {i['detail']}")
        print()

    if p1:
        print(f"🟡 P1 — Suggested improvements ({len(p1)})")
        for i in p1:
            print(f"  [{i['type']}] {i['file']}: {i['detail']}")
        print()

    if p2:
        print(f"🟢 P2 — Optional optimizations ({len(p2)})")
        for i in p2:
            print(f"  [{i['type']}] {i['file']}: {i['detail']}")
        print()

    print(f"Total: {len(p0)} P0 / {len(p1)} P1 / {len(p2)} P2")

    if p0:
        sys.exit(1)


if __name__ == "__main__":
    main()

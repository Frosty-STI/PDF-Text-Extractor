#!/usr/bin/env python3
# Consolidated: extract source & target test names, match by name, write filtered target PDF.
# Requires: pip install pymupdf

import re
import sys
from collections import defaultdict

# ====== PATHS (edit if needed) ======
SOURCE_PDF = #Fill in
TARGET_PDF = #Fill in
OUT_PDF    = #Fill in

# ====== SETTINGS ======
DROP_WORDS = ("CONTY", "CRES", "P2P")  # don't-care tests in TARGET
STRICT_CASE_SENSITIVE = True           # exact (strict) match mode case sensitivity
ENABLE_LOOSE_FALLBACK = True           # if strict fails, try "loose" mode
LOOSE_CASE_INSENSITIVE = True          # loose compares case-insensitively (recommended)

# ====== REGEXES ======

SRC_NAME_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*__\s*([^\r\n]*?)(?:(?:\s{2,})|\bTest\b|$)", re.I
)


TGT_DEVTEST_RE = re.compile(
    r"Device\s*Test:\s*(\d{1,3}(?:\.\d{1,3}){1,3})\s+([^\r\n]*?)(?=\s{2,}|\r|\n|$)",
    re.I
)

def norm_layout(s: str) -> str:
    if not s: return ""
    return s.replace("\u00AD", "").replace("–", "-").replace("—", "-")

def norm_loose(s: str) -> str:
    """Loose normalization: treat underscores like space, collapse whitespace, optional lowercase."""
    s2 = s.replace("_", " ")
    s2 = " ".join(s2.split()).strip()
    if LOOSE_CASE_INSENSITIVE:
        s2 = s2.lower()
    return s2

def load_source_names(pdf_path: str):
    """Extract only SOURCE names (ignore the numeric prefix)."""
    import fitz
    names = []
    with fitz.open(pdf_path) as doc:
        for i in range(len(doc)):
            text = doc[i].get_text("text") or ""
            text = norm_layout(text)
            m = SRC_NAME_RE.search(text)
            if m:
                name = m.group(1).strip().rstrip(":;,-").strip()
                if name:
                    names.append(name)
    return names

def load_target_tests(pdf_path: str):

    import fitz
    page_to_names = defaultdict(list)
    with fitz.open(pdf_path) as doc:
        for i in range(len(doc)):
            pno = i + 1
            text = doc[i].get_text("text") or ""
            text = norm_layout(text)
            for m in TGT_DEVTEST_RE.finditer(text):
                num = m.group(1).strip()  # not used for matching
                name = m.group(2).strip().rstrip(":;,-").strip()
                if not name:
                    continue
                # drop don't-cares
                up = name.upper()
                if any(dw in up for dw in DROP_WORDS):
                    continue
                page_to_names[pno].append(name)
    return page_to_names

def write_pdf_pages(source_pdf: str, keep_pages_1based, out_pdf: str):
    if not keep_pages_1based:
        print("[!] No pages to save.")
        return
    import fitz
    with fitz.open(source_pdf) as src:
        out = fitz.open()
        for p in keep_pages_1based:
            out.insert_pdf(src, from_page=p-1, to_page=p-1)
        out.save(out_pdf)

def main():
    print("1) Extracting source names (by name only)…")
    src_names = load_source_names(SOURCE_PDF)
    src_names = [s for s in src_names if s.strip()]
    print(f"   Source names found: {len(src_names)}")

    print("2) Extracting target tests (by name only)…")
    tgt_page_map = load_target_tests(TARGET_PDF)
    total_tgt_rows = sum(len(v) for v in tgt_page_map.values())
    print(f"   Target tests captured: {total_tgt_rows} on {len(tgt_page_map)} pages")

    # Build target lookup for strict + loose
    # Also keep page index per target name for selection.
    if STRICT_CASE_SENSITIVE:
        tgt_strict_set = set()
        for p, names in tgt_page_map.items():
            for n in names:
                tgt_strict_set.add(n)
    else:
        tgt_strict_set = set()
        for p, names in tgt_page_map.items():
            for n in names:
                tgt_strict_set.add(n.lower())

    tgt_loose_map = defaultdict(set)  # key -> set(original names)
    if ENABLE_LOOSE_FALLBACK:
        for p, names in tgt_page_map.items():
            for n in names:
                tgt_loose_map[norm_loose(n)].add(n)

    # Simple match loop: for each source name, search targets
    kept_pages = set()
    strict_cnt = 0
    loose_cnt = 0
    none_cnt = 0

    print("3) Matching (strict then loose)…")
    for s in src_names:
        # strict
        key = s if STRICT_CASE_SENSITIVE else s.lower()
        matched = False

        if key in tgt_strict_set:
            # find which pages contain this exact target name
            for p, names in tgt_page_map.items():
                if s in names or (not STRICT_CASE_SENSITIVE and s.lower() in [n.lower() for n in names]):
                    kept_pages.add(p)
                    matched = True
            if matched:
                strict_cnt += 1
                continue

        # loose
        if ENABLE_LOOSE_FALLBACK:
            lk = norm_loose(s)
            if lk in tgt_loose_map:
                # any original names under this loose key could be on many pages
                originals = tgt_loose_map[lk]
                for p, names in tgt_page_map.items():
                    if any(o in names for o in originals):
                        kept_pages.add(p)
                        matched = True
                if matched:
                    loose_cnt += 1
                    continue

        none_cnt += 1

        # --- Hardcoded fixes for anything missing ---
    HARDCODED_KEEP = [
        #enter your fixes here
    ]

    print("Checking for hardcoded keep rules…")
    for p, names in tgt_page_map.items():
        for n in names:
            if n.strip() in HARDCODED_KEEP:
                kept_pages.add(p)

    kept_pages = sorted(kept_pages)
    print("4) Writing filtered PDF…")
    print(f"   Pages to keep: {len(kept_pages)}")
    if kept_pages:
        write_pdf_pages(TARGET_PDF, kept_pages, OUT_PDF)
        print(f"   Wrote: {OUT_PDF}")
    else:
        print("   [!] No pages matched — no PDF written.")


    # Final summary
    import fitz
    with fitz.open(TARGET_PDF) as d:
        total_pages = d.page_count

    print("\n=== RESULT ===")
    print(f"Total target pages      : {total_pages}")
    print(f"Kept pages (matched)    : {len(kept_pages)}")
    print(f"Source names total      : {len(src_names)}")
    print(f"Strict matches          : {strict_cnt}")
    print(f"Loose matches           : {loose_cnt}")
    print(f"No matches              : {none_cnt}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("[!] Error:", e)
        sys.exit(1)

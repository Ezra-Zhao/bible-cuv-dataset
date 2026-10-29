# -*- coding: utf-8 -*-
"""为 release/ 备料目录生成 MANIFEST.json 与 SHA256SUMS.txt。
MANIFEST 记录底本锁定信息、66 卷逐卷统计与全量文件哈希；SHA256SUMS 覆盖
release 内除 MANIFEST.json / SHA256SUMS.txt 自身外的全部文件（相对路径）。
用法：python3 make_manifest.py <release_dir>
"""
import hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_a import load_a

VERSION = "1.0.0"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(release_dir):
    _v, lock = load_a()
    books_meta = json.load(open(os.path.join(BASE, "meta/books.json"), encoding="utf-8"))
    books = []
    for m in books_meta:
        p = os.path.join(release_dir, f"data/books/{m['book_code']}.jsonl")
        books.append({**m, "bytes": os.path.getsize(p), "sha256": sha256(p)})
    manifest = {
        "dataset": "bible-cuv-dataset",
        "version": VERSION,
        "status": "pre-release (pending approval)",
        "base_text": "1919 年和合本译文（圣经公会电子本字形）",
        "base_text_note": "非 1919 印本原貌、非新标点本；偏离清单见 DEVIATIONS.md",
        "source_lock": {
            "repo": lock["repo"], "commit": lock["commit"],
            "bibleText.js_sha256": lock["bibleText.js_sha256"],
            "dump_txt_sha256": lock["dump_txt_sha256"],
            "verses": lock["verses_parsed"],
        },
        "totals": {
            "books": len(books),
            "chapters": sum(b["chapters"] for b in books),
            "verses": sum(b["verses"] for b in books),
        },
        "books": books,
        "licenses": {"data": "CC BY 4.0", "scripts": "MIT"},
    }
    with open(os.path.join(release_dir, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    entries = []
    for root, _dirs, files in os.walk(release_dir):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), release_dir)
            if rel in ("MANIFEST.json", "SHA256SUMS.txt"):
                continue
            entries.append((rel, sha256(os.path.join(root, fn))))
    with open(os.path.join(release_dir, "SHA256SUMS.txt"), "w", encoding="utf-8") as f:
        for rel, h in sorted(entries):
            f.write(f"{h}  {rel}\n")
    print(f"MANIFEST totals: {manifest['totals']}; SHA256SUMS entries: {len(entries)}")


if __name__ == "__main__":
    main(sys.argv[1])

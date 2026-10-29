# -*- coding: utf-8 -*-
"""P1/P2 生成管线：A 源（FHL 谱系锁定本）→ 逐节 JSONL。

口径（改标派定版，不得漂移）：
- 底本 = 1919 年和合本译文（圣经公会电子本字形），非 1919 印本原貌；
- text_trad = A 源繁体原文，标点原样、不做任何现代化处理；
- text = text_trad 经 OpenCC t2s 的机械简体转换（转换可复现）；
- 不混入新标点本的标点、分段、人名修订（A 源本身已过 P0 人名层指纹）。
用法：python3 build_dataset.py [NT|OT|ALL]（默认 ALL）
输出：data/books/<CODE>.jsonl、data/cuv-all.jsonl、meta/books.json
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from books import BOOKS
from parse_a import load_a
from opencc import OpenCC

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t2s = OpenCC("t2s")


def main(scope="ALL"):
    verses, lock = load_a()
    assert lock["dump_matches_js"] and lock["parse_anomaly_count"] == 0, lock
    os.makedirs(os.path.join(BASE, "data/books"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "meta"), exist_ok=True)

    books_meta, all_lines = [], []
    for code, zh, en, testament, nch, _fhl in BOOKS:
        if scope != "ALL" and testament != scope:
            continue
        keys = sorted(k for k in verses if k[0] == code)
        lines = []
        for (_c, ch, vs) in keys:
            trad = verses[(code, ch, vs)]
            rec = {
                "book": zh,
                "book_en": en,
                "book_code": code,
                "testament": testament,
                "chapter": ch,
                "verse": vs,
                "text": t2s.convert(trad),
                "text_trad": trad,
            }
            lines.append(json.dumps(rec, ensure_ascii=False))
        path = os.path.join(BASE, f"data/books/{code}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        chapters_seen = len({k[1] for k in keys})
        books_meta.append({
            "book_code": code, "book": zh, "book_en": en,
            "testament": testament, "chapters": chapters_seen,
            "verses": len(lines),
        })
        all_lines.extend(lines)
        print(f"{code} {zh}: {chapters_seen} 章 / {len(lines)} 节")

    if scope == "ALL":
        with open(os.path.join(BASE, "data/cuv-all.jsonl"), "w", encoding="utf-8") as f:
            f.write("\n".join(all_lines) + "\n")
        with open(os.path.join(BASE, "meta/books.json"), "w", encoding="utf-8") as f:
            json.dump(books_meta, f, ensure_ascii=False, indent=2)
    print(f"[{scope}] total verses written:", len(all_lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ALL")

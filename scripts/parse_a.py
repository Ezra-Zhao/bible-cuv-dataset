# -*- coding: utf-8 -*-
"""A 源解析与锁定验证（FHL 谱系，改标派定版底本）。

锁定对象：
- 仓 xuan9/ChineseBibleSearchJS，commit 1034aee964b8b7604a1daba6aafbd1c25cdac815
- 文件 bibleText.js（文件头自述源为 FHL springbible OfflineBible）
本脚本：①从 bibleText.js 直接抽取经文行；②与 P0 留档转储
src/fhl-lineage-xuan9.txt 逐行比对，证明转储忠实于锁定 commit；
③解析为 {(code, chapter, verse): text_trad} 供管线使用。
"""
import hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from books import BOOKS

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(BASE, "src/xuan9-ChineseBibleSearchJS/bibleText.js")
DUMP = os.path.join(BASE, "src/fhl-lineage-xuan9.txt")

# 与 p0_diff.py 同一份前缀表（按经卷顺序，实测自转储文件）
PREFIX = ["創","出","利","民","申","書","士","得","撒上","撒下","王上","王下","代上","代下","拉","尼","斯","伯","詩","箴","傳","歌","賽","耶","哀","結","但","何","珥","摩","俄","拿","彌","鴻","哈","番","該","亞","瑪","太","可","路","約","徒","羅","林前","林後","加","弗","腓","西","帖前","帖後","提前","提後","多","門","來","雅","彼前","彼後","約一","約二","約三","猶","啟"]
P2C = {p: BOOKS[i][0] for i, p in enumerate(PREFIX)}
LINE = re.compile(r"^(\D+?)(\d+):(\d+)\s+(.*)$")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_js_lines():
    raw = open(JS, encoding="utf-8").read()
    return re.findall(r"'((?:[^'\\]|\\.)*)',?\s*\n", raw)


def parse(lines):
    verses, bad = {}, []
    for ln in lines:
        m = LINE.match(ln.strip())
        if m and m.group(1) in P2C:
            key = (P2C[m.group(1)], int(m.group(2)), int(m.group(3)))
            if key in verses:
                bad.append(("dup", key))
            verses[key] = m.group(4)
        else:
            bad.append(("unparsed", ln[:60]))
    return verses, bad


def load_a():
    """返回 (verses_dict, lock_info)。lock_info 含双份哈希与转储一致性结论。"""
    js_lines = [l.replace("\\'", "'") for l in extract_js_lines()]
    dump_lines = [l.rstrip("\n") for l in open(DUMP, encoding="utf-8") if l.strip()]
    same = js_lines == dump_lines
    verses, bad = parse(dump_lines)
    info = {
        "repo": "xuan9/ChineseBibleSearchJS",
        "commit": "1034aee964b8b7604a1daba6aafbd1c25cdac815",
        "bibleText.js_sha256": sha256(JS),
        "dump_txt_sha256": sha256(DUMP),
        "js_lines": len(js_lines),
        "dump_lines": len(dump_lines),
        "dump_matches_js": same,
        "verses_parsed": len(verses),
        "parse_anomalies": bad[:20],
        "parse_anomaly_count": len(bad),
    }
    return verses, info


if __name__ == "__main__":
    verses, info = load_a()
    print(json.dumps(info, ensure_ascii=False, indent=2))
    nt = sum(1 for k in verses if BOOKS[[b[0] for b in BOOKS].index(k[0])][3] == "NT")
    print("NT verses:", nt, "| OT verses:", len(verses) - nt)

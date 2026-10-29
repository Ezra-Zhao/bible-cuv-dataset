# -*- coding: utf-8 -*-
"""校验套件：①逐章节点数对账（vs 公认分节参考表）②抽样与 A 源逐字比对
③完整性（JSON 可解析、字段齐、节号连续无缺）。
用法：python3 verify.py [NT|ALL]  输出写入 meta/ 与 audit/ 的记录文件。
参考表 meta/reference-verse-counts.csv：独立 KJV 数字化（thiagobodruk/bible,
en_kjv，66 卷 31,102 节）的逐章计数——与和合本同属通行分节体系；
中英分节差异点在对账报告中逐项登记裁定，不自动改数据。
"""
import csv, json, os, random, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from books import BOOKS, BY_CODE
from parse_a import load_a
from opencc import OpenCC

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t2s = OpenCC("t2s")
FIELDS = ["book", "book_en", "book_code", "testament", "chapter", "verse", "text", "text_trad"]


def load_generated(scope):
    recs = []
    for code, _zh, _en, testament, _nch, _f in BOOKS:
        if scope != "ALL" and testament != scope:
            continue
        path = os.path.join(BASE, f"data/books/{code}.jsonl")
        with open(path, encoding="utf-8") as f:
            for line in f:
                recs.append(json.loads(line))
    return recs


def main(scope="ALL"):
    recs = load_generated(scope)
    a_verses, lock = load_a()

    # ③ 完整性
    problems = []
    seen = set()
    for r in recs:
        if sorted(r.keys()) != sorted(FIELDS):
            problems.append(f"字段不齐 {r.get('book_code')} {r.get('chapter')}:{r.get('verse')}")
        key = (r["book_code"], r["chapter"], r["verse"])
        if key in seen:
            problems.append(f"重复 {key}")
        seen.add(key)
        meta = BY_CODE[r["book_code"]]
        if r["book"] != meta[1] or r["book_en"] != meta[2] or r["testament"] != meta[3]:
            problems.append(f"元数据不符 {key}")
        if r["text_trad"] != a_verses.get(key):
            problems.append(f"text_trad 与 A 源不符 {key}")
        if r["text"] != t2s.convert(r["text_trad"]):
            problems.append(f"text 转换不可复现 {key}")
    by_ch = defaultdict(list)
    for (c, ch, vs) in seen:
        by_ch[(c, ch)].append(vs)
    for (c, ch), vss in by_ch.items():
        if sorted(vss) != list(range(1, max(vss) + 1)):
            problems.append(f"节号不连续 {c} {ch}: {sorted(vss)[:5]}...")

    # ① 逐章对账
    expected = {}
    with open(os.path.join(BASE, "meta/reference-verse-counts.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            expected[(row["book_code"], int(row["chapter"]))] = int(row["expected_verses"])
    actual = {k: len(v) for k, v in by_ch.items()}
    scope_codes = {b[0] for b in BOOKS if scope == "ALL" or b[3] == scope}
    diffs = []
    for (c, ch), exp in sorted(expected.items()):
        if c not in scope_codes:
            continue
        act = actual.get((c, ch), 0)
        if act != exp:
            diffs.append((c, ch, exp, act, act - exp))

    # ② 抽 20 处逐字比对（固定种子，可复现）
    random.seed(20261029)
    sample = random.sample(recs, 20)
    sample_rows = []
    for r in sample:
        key = (r["book_code"], r["chapter"], r["verse"])
        ok = r["text_trad"] == a_verses[key]
        sample_rows.append((key, ok, r["text_trad"][:30]))

    # 报告
    lines = [f"# 校验报告（{scope}）", "",
             f"- 生成节数：{len(recs)}；A 源节数：{len(a_verses)}",
             f"- 完整性问题：{len(problems)}"]
    lines += [f"  - {p}" for p in problems[:30]]
    lines += ["", f"## 逐章对账 vs 公认分节参考表（KJV 独立数字化）",
              f"- 对账章数：{sum(1 for (c, _) in expected if c in scope_codes)}；差异章：{len(diffs)}"]
    for c, ch, exp, act, d in diffs:
        lines.append(f"  - {c} {BY_CODE[c][1]} 第{ch}章：期望 {exp}，实测 {act}（{d:+d}）")
    lines += ["", "## 抽样 20 处与 A 源逐字比对（种子 20261029）"]
    for key, ok, prev in sample_rows:
        lines.append(f"  - {key[0]} {key[1]}:{key[2]} {'一致' if ok else '不一致！'} 「{prev}…」")
    lines.append(f"- 抽样结论：{sum(1 for _, ok, _ in sample_rows if ok)}/20 一致")
    report = "\n".join(lines) + "\n"
    out = os.path.join(BASE, f"meta/verify-{scope}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ALL")

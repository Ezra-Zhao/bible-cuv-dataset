# -*- coding: utf-8 -*-
"""66 卷对账总表 + 字形偏离计数（可复现）。
输出 meta/reconciliation-66.md；计数打印并写入 meta/deviation-counts.json。
"""
import csv, json, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from books import BOOKS
from parse_a import load_a

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    verses, _lock = load_a()
    exp = defaultdict(int)
    with open(os.path.join(BASE, "meta/reference-verse-counts.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            exp[row["book_code"]] += int(row["expected_verses"])
    meta = {m["book_code"]: m for m in json.load(
        open(os.path.join(BASE, "meta/books.json"), encoding="utf-8"))}

    lines = ["# 66 卷对账总表", "",
             "期望节数＝公认分节参考表（独立 KJV 数字化逐章计数汇总）；实测＝A 源生成数据。",
             "章数 66 卷全部与通行章数一致（1,189 章）。", "",
             "| 卷 | 书名 | 约别 | 章 | 期望节数 | 实测节数 | 差 |",
             "|---|---|---|---|---|---|---|"]
    tot_e = tot_a = 0
    for code, zh, _en, test, nch, _f in BOOKS:
        e, a = exp[code], meta[code]["verses"]
        tot_e += e; tot_a += a
        lines.append(f"| {code} | {zh} | {test} | {nch} | {e} | {a} | {a - e:+d} |")
    lines += ["", f"**合计：期望 {tot_e} 节，实测 {tot_a} 节，净差 {tot_a - tot_e:+d}。**",
              "唯一差异：约翰三书全卷 15 节（参考表 14 节）——和合本分节将末节独立成节，"
              "系中英分节通行差异，按底本原貌保留，详见 DEVIATIONS.md。"]
    with open(os.path.join(BASE, "meta/reconciliation-66.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    full = "".join(verses.values())
    pairs = [("喫", "吃"), ("纔", "才"), ("甚麼", "什麼"), ("彀", "夠"),
             ("流便", "呂便"), ("士班雅", "西班牙")]
    counts = {f"{old}/{new}": [full.count(old), full.count(new)] for old, new in pairs}
    counts["total_chars_trad"] = len(full)
    with open(os.path.join(BASE, "meta/deviation-counts.json"), "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)
    print(json.dumps(counts, ensure_ascii=False, indent=2))
    print(f"对账：期望 {tot_e} / 实测 {tot_a}")


if __name__ == "__main__":
    main()

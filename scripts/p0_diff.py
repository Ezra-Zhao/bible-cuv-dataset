# -*- coding: utf-8 -*-
"""P0 双源 diff 与印本谱系对照（v2）。
A = FHL 谱系（xuan9 转储，繁体，自述源 FHL OfflineBible）
B = db 谱系（ElijahLabs==xieyao04，简体）
比对法：A 经 OpenCC t2s 转简后与 B 逐节比（剥标点空白）；另统计 B 的 她 现代化。
印本对照：mondain 创世记（1919 印本排字工程）vs A 创世记，含字形还原实验。
输出 audit/p0-diff-report.txt
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from books import BOOKS
from opencc import OpenCC

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUNCT = set("，。；：？！、·「」『』（）()—…-\"\"''《》〈〉﹔﹕﹖﹗　 \t\n\r‧・,.;:?!")

def norm(s):
    return "".join(ch for ch in s if ch not in PUNCT)

# xuan9 前缀（按经卷顺序实测）-> code
PREFIX = ["創","出","利","民","申","書","士","得","撒上","撒下","王上","王下","代上","代下","拉","尼","斯","伯","詩","箴","傳","歌","賽","耶","哀","結","但","何","珥","摩","俄","拿","彌","鴻","哈","番","該","亞","瑪","太","可","路","約","徒","羅","林前","林後","加","弗","腓","西","帖前","帖後","提前","提後","多","門","來","雅","彼前","彼後","約一","約二","約三","猶","啟"]
P2C = {p: BOOKS[i][0] for i, p in enumerate(PREFIX)}

a_trad = {}
pat = re.compile(r"^(\D+?)(\d+):(\d+)\s+(.*)$")
for line in open(os.path.join(BASE, "src/fhl-lineage-xuan9.txt"), encoding="utf-8"):
    m = pat.match(line.strip())
    if m and m.group(1) in P2C:
        a_trad[(P2C[m.group(1)], int(m.group(2)), int(m.group(3)))] = m.group(4)
print("A verses:", len(a_trad))

t2s = OpenCC("t2s")
a = {k: t2s.convert(v) for k, v in a_trad.items()}

rows = json.loads(open(os.path.join(BASE, "src/db-lineage.json"), encoding="utf-8").read())
b = {}
for vol, ch, vs, txt in rows:
    b[(BOOKS[vol - 1][0], ch, vs)] = txt
print("B verses:", len(b))
print("B 中「她」出现次数:", sum(v.count("她") for v in b.values()),
      " A(转简)中「她」:", sum(v.count("她") for v in a.values()))

def diff(x, y, label):
    keys = sorted(set(x) & set(y))
    diffs = [k for k in keys if norm(x[k]) != norm(y[k])]
    print(f"\n[{label}] 共同节 {len(keys)}，仅X {len(set(x)-set(y))}，仅Y {len(set(y)-set(x))}，实质差异节 {len(diffs)}（{len(diffs)/max(len(keys),1):.1%}）")
    return diffs

d_ab = diff(a, b, "A(FHL->简) vs B(db简)")
for k in d_ab[:15]:
    print("  ", k, "\n    A:", a[k], "\n    B:", b[k])

# ---------- mondain Genesis ----------
def extract_mondain():
    out = {}
    gendir = os.path.join(BASE, "src/mondain-cuv-1919/tex/gen")
    for fn in os.listdir(gendir):
        m = re.match(r"gen_(\d+)\.tex$", fn)
        if not m:
            continue
        ch = int(m.group(1))
        raw = open(os.path.join(gendir, fn), encoding="utf-8").read()
        raw = re.sub(r"\\ledleftnote\{[^}]*\}", "", raw)
        raw = re.sub(r"\\ProperNameC\{[^}]*\}\{[^}]*\}\{([^}]*)\}", r"\1", raw)
        raw = re.sub(r"\\(?:ProperName|PlaceName|kenten)\{([^}]*)\}", r"\1", raw)
        parts = re.split(r"\\bv\{(\d+)\}", raw)
        for i in range(1, len(parts) - 1, 2):
            txt = re.sub(r"\\[a-zA-Z]+", "", parts[i + 1]).replace("%", "").strip()
            if txt:
                out[("GEN", ch, int(parts[i]))] = txt
    return out

mo = extract_mondain()
agen = {k: v for k, v in a_trad.items() if k[0] == "GEN"}
print("\nmondain GEN verses:", len(mo), " A GEN:", len(agen))
d_am = diff(mo, agen, "mondain(印本) vs A(FHL繁) 创世记")
RESTORE = [("吃", "喫"), ("夠", "彀"), ("什麼", "甚麼")]
def restore(s):
    for x, y in RESTORE:
        s = s.replace(x, y)
    return s
common = sorted(set(mo) & set(agen))
n_after = [k for k in common if norm(restore(agen[k])) != norm(mo[k])]
print(f"字形还原（吃→喫/夠→彀/什麼→甚麼）后仍差异：{len(n_after)} / {len(common)}")
for k in n_after[:15]:
    print("  ", k, "\n    印本:", mo[k], "\n    FHL :", agen[k])

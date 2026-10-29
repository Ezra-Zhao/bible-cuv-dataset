# -*- coding: utf-8 -*-
"""指纹审计：判别候选源是 1919 和合本原貌还是新标点本(CUNPS)衍生。

判别对（繁体语料直接测；简体语料只测能跨繁简保持区分的对）：
  人名：流便(1919) / 吕便(CUNPS)      —— 创 29:32 起出现数十次
  地名：士班雅(1919, 指西班牙) / 西班牙(CUNPS) —— 罗 15:24,28
  字用：喫(1919) / 吃(CUNPS)          —— 仅繁体语料有效（简体转换会合并）
        纔(1919) / 才(CUNPS)          —— 仅繁体语料有效
        彀(1919) / 够(CUNPS)          —— 仅繁体语料有效（彀极罕见，作参考）
判定：任一 CUNPS 侧计数 >0（人名/地名对）即判污染；繁体语料另看字用对。
用法：fingerprint.py <语料文本文件...>（UTF-8，繁简皆可，脚本自动判繁简）
"""
import sys, unicodedata

PAIRS_TRAD = [("流便", "呂便"), ("士班雅", "西班牙"), ("喫", "吃"), ("纔", "才"), ("彀", "夠")]
PAIRS_ANY = [("流便", "吕便"), ("士班雅", "西班牙")]

def main(paths):
    text = ""
    for p in paths:
        with open(p, encoding="utf-8", errors="ignore") as f:
            text += f.read()
    is_trad = text.count("創") + text.count("詩") > text.count("创") + text.count("诗")
    pairs = PAIRS_TRAD if is_trad else PAIRS_ANY
    print(f"语料字符数={len(text)} 判为{'繁体' if is_trad else '简体'}")
    polluted = False
    for old, new in pairs:
        co, cn = text.count(old), text.count(new)
        flag = ""
        if cn > 0 and old in ("流便", "士班雅", "呂便"):
            flag = "  <-- CUNPS 指纹!"
            polluted = True
        print(f"  1919「{old}」={co}   CUNPS「{new}」={cn}{flag}")
    print("结论：" + ("检出新标点本指纹 → 弃用" if polluted else "未检出新标点指纹（仍须双源 diff 才能锁定）"))
    return 1 if polluted else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# bible-cuv-dataset

**1919 年和合本译文 · 66 卷逐节结构化数据集（简繁双字段）**

> **底本口径（请先读这一段）**
> 本数据集的底本是 **1919 年和合本译文（圣经公会电子本字形）**：
> 译文为 1919 年官话和合本，字形为圣经公会通行电子本的规范化字形。
> 它**不是** 1919 年印本的逐字原貌（印本的喫／纔／甚麼／彀等古字已规范化为
> 吃／才／什麼／夠），也**不是** 1988 年新标点本（人名地名保持 1919 译名，
> 如流便、士班雅；新标点本的标点、分段与修订成果零混入）。
> 全部已知偏离逐项公开于 [DEVIATIONS.md](DEVIATIONS.md)，来源与审计
> 记录见 [docs/provenance.md](docs/provenance.md)。

## 规格

| 项 | 数 |
|---|---|
| 书卷 | 66（旧约 39＋新约 27） |
| 章 | 1,189 |
| 节 | 31,103（逐章对账：与公认分节仅约翰三书第 1 章差 1 节，见偏离清单） |
| 格式 | JSONL，一行一节，UTF-8 |
| 全经总包 | 约 21 MB（gzip 后约 2.3 MB），见 Release |

每节字段：

| 字段 | 说明 |
|---|---|
| `book` | 中文书名（简体，如「创世记」） |
| `book_en` | 英文書名（如 `Genesis`） |
| `book_code` | 通行三字母码（`GEN`／`EXO`／…／`REV`） |
| `testament` | `OT` 或 `NT` |
| `chapter` / `verse` | 章、节（整数） |
| `text` | 简体经文（由繁体经 OpenCC 机械转换，见偏离清单第五节） |
| `text_trad` | 繁体经文（底本原样） |

样例：

```json
{"book": "创世记", "book_en": "Genesis", "book_code": "GEN", "testament": "OT", "chapter": 1, "verse": 1, "text": "起初，神创造天地。", "text_trad": "起初，神創造天地。"}
```

## 下载

- **按卷**：仓内 `data/books/<CODE>.jsonl`，66 个文件，可直接浏览取用；
- **全经总包**：见本仓 Release（`bible-cuv-dataset-1.0.0.tar.gz` 内含
  `data/cuv-all.jsonl` 全经合集）；
- **验完整性**：Release 与仓内附 `MANIFEST.json`、`SHA256SUMS.txt`，
  下载后运行 `sha256sum -c SHA256SUMS.txt` 即可自证文件未被改动。

## 快速上手

```python
import json
with open("data/books/JHN.jsonl", encoding="utf-8") as f:
    verses = [json.loads(line) for line in f]
print(verses[0]["text"])  # 太初有道，道与神同在，道就是神。
```

```bash
jq -r 'select(.chapter == 1 and .verse == 1) | .text' data/books/GEN.jsonl
```

## 为什么用这个底本

- **权利干净**：1919 年译文版权已经期满（public domain）。1988 年新标点本
  的标点、分段、人名修订是圣经公会系统的受版权编辑成果，不能开放再分发，
  故不作底本；本数据集保证其成果零混入，审计方法与计数证据公开在
  provenance 中，任何人可复查。
- **诚实标示**：市面流通的「和合本全文」没有一份是 1919 印本逐字原貌。
  本数据集不冒称原貌——与印本的全部已知差异（字形四项＋节次一项）
  逐项写在 DEVIATIONS.md 里，计数可由仓内脚本复现。

## 校验

- 逐章对账：1,189 章逐章与公认分节参考表比对，结果与裁定见
  `docs/provenance.md` 第四节；
- 全量逐字：生成数据每一节均与锁定底本逐字比对（31,103 节全量，非抽样）；
- 底本锁定：来源仓 commit 与文件 SHA-256 记录于 MANIFEST.json。

## 许可

- **数据**（`data/`、`books.json`、`MANIFEST.json`）：**CC BY 4.0**——
  可自由使用、复制、再分发与改作（包括商业用途），条件是署名：
  `数据来源：bible-cuv-dataset（1919 年和合本译文·圣经公会电子本字形），CC BY 4.0`。
  详见 [DATASET-LICENSE.md](DATASET-LICENSE.md)。
- **构建脚本**（`scripts/`）：MIT，见 [LICENSE](LICENSE)。
- 1919 年译文本身属公有领域（public domain），上述 CC BY 署名要求针对
  本数据集的结构化成果与汇编，不改变译文本身的公版状态。

## 路线（v2 规划）

- 人名地名索引（节级出处）；
- Strong 编号节级映射（源数据 STEPBible-Data，CC BY 4.0，署名随附；
  映射由原文词项按节聚合派生，非中文逐词对齐）。

勘误请开 issue：附书卷章、节、底本原文与本数据现文，核实后以 v1.x 发布。

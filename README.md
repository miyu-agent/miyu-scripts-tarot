# 塔罗

Miyu 脚本包，带一件工具 `tarot`：抽塔罗牌、排牌阵，交回每张牌的位置、正逆位和关键词。只出牌，解读归 AI。

| 参数 | 说明 |
|---|---|
| `spread` | 牌阵：`single`（1 张）、`three_card`（过去/现在/未来）、`yes_no`（支持/反对/综合）、`relationship`（4 张）、`celtic_cross`（凯尔特十字，10 张）、`custom`。默认 `single`；给了 `positions` 没写牌阵的当 `custom` |
| `positions` | 只给 `custom`：位置名，或 `{name, hint}`，至多 78 个 |
| `question` | 问的事，原样带回，不参与抽牌 |
| `reversal` | 每张牌逆位的概率，0–1，默认 0.3；0 是不用逆位 |
| `keywords` | 带不带关键词，默认带 |

整副 78 张洗一次从上往下发，同一次不会重复。随机数取自系统熵源，**故意没有种子参数**：AI 不能挑种子来挑结果。

`Clicall: no`：只能直接调，AI 不能在命令里经 `miyu call` 反复重抽；每一次抽牌都在时间线上单独一条。

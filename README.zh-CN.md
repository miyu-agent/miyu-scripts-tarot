<p align="center">
  <a href="README.md">English</a> | 简体中文
</p>

# 塔罗

> <sub>本文档由 Anthropic 的 Claude Fable 5.2 生成。</sub>

这是 Miyu 的一个脚本软件包，提供一件工具 `tarot`。它抽塔罗牌、排牌阵，返回每张牌的位置、正逆位和关键词。工具只负责出牌，解读由 AI 完成。

| 参数 | 说明 |
|---|---|
| `spread` | 牌阵：`single`（1 张）、`three_card`（过去/现在/未来）、`yes_no`（支持/反对/综合）、`relationship`（4 张）、`celtic_cross`（凯尔特十字，10 张）、`custom`。默认是 `single`；如果给了 `positions` 而没有写牌阵，就按 `custom` 处理 |
| `positions` | 只用于 `custom`：位置的名字，或者 `{name, hint}`，最多 78 个 |
| `question` | 要问的事，工具会原样带回，不参与抽牌 |
| `reversal` | 每张牌出现逆位的概率，0–1，默认 0.3；0 表示不使用逆位 |
| `keywords` | 是否附带关键词，默认附带 |

整副 78 张牌洗一次以后从上往下发，同一次抽牌里不会出现重复的牌。随机数取自系统熵源，**有意不提供种子参数**：AI 不能通过挑选种子来挑选结果。

脚本开头的声明里写着 `Clicall: no`，所以这件工具只能由 AI 直接调用，AI 不能在命令里通过 `miyu call` 反复重抽；每一次抽牌都会在时间线上单独显示为一条。

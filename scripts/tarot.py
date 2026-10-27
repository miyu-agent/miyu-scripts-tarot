#!/usr/bin/env python3
# Display name: Tarot
# 显示名称：塔罗
# Description: Draw tarot cards into a spread and return each card, its position, upright or reversed, and its keywords; the reading is yours.
# 描述：抽塔罗牌：牌阵、每张牌的位置、正逆位和关键词，只出牌，不解读。
# Timeout: 10
# Clicall: no
# Parameters:
# {"type": "object", "properties": {
#   "spread": {"type": "string", "enum": ["single", "three_card", "yes_no", "relationship", "celtic_cross", "custom"], "description": "single: 1 card; three_card: past, present, future; yes_no: for, against, overall; relationship: 4 cards; celtic_cross: 10 cards; custom: your own positions. Default single."},
#   "positions": {"type": "array", "description": "Only for spread=custom: position names, or {name, hint} objects. At most 78.", "items": {"oneOf": [{"type": "string"}, {"type": "object", "properties": {"name": {"type": "string"}, "hint": {"type": "string"}}, "required": ["name"]}]}},
#   "question": {"type": "string", "description": "The question asked; echoed back, never used in the draw."},
#   "reversal": {"type": "number", "description": "Chance each card comes out reversed, 0 to 1. Default 0.3; 0 means no reversals."},
#   "keywords": {"type": "boolean", "description": "Attach the card's keywords. Default true."}
# }}
"""Lay tarot cards into a spread. The tool draws; the caller reads."""

import json
import secrets
import sys

RANKS = ["王牌", "二", "三", "四", "五", "六", "七", "八", "九", "十",
         "侍从", "骑士", "王后", "国王"]

# (num, name, upright keywords, reversed keywords)
MAJORS = [
    (0,  "愚者",     ["新的开始", "冒险", "纯真", "自由", "信任直觉"],
                     ["鲁莽", "逃避责任", "盲目乐观", "停滞不前"]),
    (1,  "魔术师",   ["行动力", "资源整合", "显化", "自信", "技能"],
                     ["空谈", "操控", "才能未展", "欺瞒"]),
    (2,  "女祭司",   ["直觉", "潜意识", "静观", "秘密", "内在智慧"],
                     ["忽视直觉", "表里不一", "压抑情绪", "信息隐瞒"]),
    (3,  "皇后",     ["丰饶", "滋养", "母性", "感性", "创造力"],
                     ["过度依赖", "溺爱", "创造力受阻", "忽视自我"]),
    (4,  "皇帝",     ["权威", "秩序", "责任", "稳定", "掌控"],
                     ["专制", "僵化", "缺乏自律", "权力斗争"]),
    (5,  "教皇",     ["传统", "指引", "信念", "教诲", "体制"],
                     ["墨守成规", "反叛", "教条", "错误的建议"]),
    (6,  "恋人",     ["结合", "选择", "契合", "吸引", "价值观一致"],
                     ["失衡", "犹豫不决", "诱惑", "价值观冲突"]),
    (7,  "战车",     ["意志", "前进", "胜利", "掌控方向", "行动"],
                     ["失控", "方向不明", "停滞", "鲁莽"]),
    (8,  "力量",     ["勇气", "耐心", "温柔的坚定", "自制", "内在力量"],
                     ["自我怀疑", "失控", "软弱", "勉强硬撑"]),
    (9,  "隐士",     ["内省", "独处", "求索", "指引", "沉淀"],
                     ["孤立", "逃避", "固步自封", "拒绝求助"]),
    (10, "命运之轮", ["转机", "循环", "命运", "时来运转", "变化"],
                     ["时运不济", "恶性循环", "抗拒变化", "延迟"]),
    (11, "正义",     ["公正", "平衡", "因果", "责任", "真相"],
                     ["不公", "失衡", "逃避责任", "偏见"]),
    (12, "倒吊人",   ["换位思考", "暂停", "牺牲", "顿悟", "顺其自然"],
                     ["拖延", "无谓牺牲", "停滞", "固执"]),
    (13, "死神",     ["结束", "蜕变", "断舍离", "重生", "过渡"],
                     ["抗拒结束", "停滞", "藕断丝连", "恐惧改变"]),
    (14, "节制",     ["平衡", "调和", "耐心", "中道", "疗愈"],
                     ["失衡", "极端", "急躁", "消耗"]),
    (15, "恶魔",     ["束缚", "欲望", "执念", "诱惑", "物质主义"],
                     ["挣脱", "觉察", "戒断", "重获自由"]),
    (16, "高塔",     ["剧变", "崩塌", "真相揭露", "破而后立"],
                     ["延缓的灾难", "恐惧改变", "内部崩塌", "勉强维持"]),
    (17, "星星",     ["希望", "疗愈", "指引", "宁静", "信心"],
                     ["绝望", "失去信心", "迷茫", "自我怀疑"]),
    (18, "月亮",     ["幻象", "不安", "潜意识", "模糊", "直觉预警"],
                     ["真相浮现", "摆脱恐惧", "澄清", "情绪平复"]),
    (19, "太阳",     ["成功", "喜悦", "活力", "坦率", "光明"],
                     ["短暂的低落", "过度乐观", "虚荣", "延迟的快乐"]),
    (20, "审判",     ["觉醒", "召唤", "重生", "清算", "抉择"],
                     ["自我否定", "逃避审视", "悔恨", "迟迟不决"]),
    (21, "世界",     ["完成", "圆满", "整合", "抵达", "成就"],
                     ["未竟", "差临门一脚", "循环未闭合", "拖延"]),
]

# (suit id, suit name, element, 14 x (upright, reversed))
SUITS = [
    ("wands", "权杖", "火", [
        (["灵感", "新契机", "热情点燃", "行动力"], ["动力不足", "计划受阻", "热情消退", "拖延"]),
        (["规划", "远见", "抉择", "走出舒适圈"], ["犹豫", "计划落空", "恐惧未知", "目光短浅"]),
        (["展望", "扩张", "等待成果", "远行"], ["受阻", "目光受限", "延迟", "合作不畅"]),
        (["庆祝", "稳定", "归属", "里程碑"], ["缺乏归属感", "动荡", "庆祝推迟", "家庭矛盾"]),
        (["竞争", "分歧", "混战", "磨合"], ["回避冲突", "内耗", "无谓争执", "和解"]),
        (["胜利", "认可", "凯旋", "自信"], ["骄傲自满", "认可落空", "虚名", "信心受挫"]),
        (["坚守", "防御", "立场", "压力下的坚持"], ["力不从心", "放弃抵抗", "四面楚歌", "妥协"]),
        (["迅速", "进展", "消息", "顺势而为"], ["延迟", "停滞", "混乱", "错过时机"]),
        (["韧性", "戒备", "最后一搏", "坚持到底"], ["疲惫", "疑神疑鬼", "濒临放弃", "过度防御"]),
        (["重担", "责任", "接近终点", "透支"], ["卸下重担", "拒绝承担", "崩溃边缘", "学会放手"]),
        (["好奇", "新想法", "热情初起", "探索"], ["三分钟热度", "幼稚", "坏消息", "方向不定"]),
        (["冲劲", "冒险", "热情行动", "魅力"], ["冲动", "鲁莽", "半途而废", "急躁"]),
        (["自信", "热情", "感染力", "独立"], ["善妒", "强势", "缺乏自信", "情绪化"]),
        (["领导力", "远见", "魄力", "创业"], ["独断", "急躁", "好大喜功", "缺乏耐心"]),
    ]),
    ("cups", "圣杯", "水", [
        (["新的感情", "爱的萌芽", "直觉", "心灵丰盈"], ["情感封闭", "空虚", "错失良缘", "压抑"]),
        (["契合", "双向", "真诚交流", "结盟"], ["失衡", "误解", "关系裂痕", "各怀心思"]),
        (["友谊", "庆祝", "分享", "社群"], ["圈子消耗", "八卦", "被排挤", "过度放纵"]),
        (["倦怠", "视而不见", "需要沉淀", "静观"], ["重燃兴趣", "抓住机会", "走出麻木", "觉醒"]),
        (["失落", "遗憾", "哀悼", "只看失去的"], ["接受", "走出阴霾", "重新看见", "释怀"]),
        (["怀旧", "童真", "旧友", "纯粹的善意"], ["困于过去", "拒绝长大", "旧伤复发", "幻想滤镜"]),
        (["幻想", "选择过多", "迷惑", "白日梦"], ["认清现实", "做出选择", "清醒", "拨云见日"]),
        (["转身离开", "追寻更深的意义", "放下"], ["不敢离开", "徘徊", "恐惧未知", "拖延决断"]),
        (["满足", "愿望达成", "享受", "知足"], ["空虚的满足", "贪婪", "炫耀", "愿望落空"]),
        (["圆满的情感", "家庭和睦", "归属", "幸福"], ["家庭失和", "表面的圆满", "价值观分歧", "疏离"]),
        (["感性", "灵感", "温柔", "好消息"], ["情绪化", "逃避现实", "幼稚", "感情用事"]),
        (["浪漫", "追求", "体贴", "理想主义"], ["空头承诺", "情绪不稳", "沉溺幻想", "逃避"]),
        (["共情", "温柔", "直觉敏锐", "包容"], ["情绪泛滥", "依赖", "自我牺牲过度", "界限模糊"]),
        (["情感成熟", "包容", "沉稳", "疗愈他人"], ["压抑情绪", "情绪操控", "外冷内乱", "逃避感受"]),
    ]),
    ("swords", "宝剑", "风", [
        (["清晰", "真相", "突破", "决断", "新的认知"], ["混乱", "误判", "思绪不清", "言语伤人"]),
        (["僵持", "回避抉择", "权衡", "蒙眼"], ["打破僵局", "被迫面对", "信息浮现", "决断"]),
        (["心碎", "痛苦", "背叛", "直言伤人"], ["疗愈", "走出伤痛", "释怀", "压下的痛"]),
        (["休整", "静养", "暂停", "恢复"], ["被迫行动", "失眠焦虑", "拒绝休息", "复出"]),
        (["争执余波", "放下", "和解的余地"], ["耿耿于怀", "口舌之灾", "廉价的胜利"]),
        (["过渡", "离开困境", "平缓前行", "疗伤之旅"], ["走不出去", "旧问题跟随", "抗拒改变", "滞留"]),
        (["策略", "隐瞒", "独自行动", "取巧"], ["败露", "坦白", "自我欺骗被戳破", "归还"]),
        (["自我设限", "受困", "无力感", "视野狭窄"], ["挣脱束缚", "看清出路", "重获自由", "松绑"]),
        (["焦虑", "失眠", "过度担忧", "梦魇"], ["走出焦虑", "求助", "面对恐惧", "缓解"]),
        (["触底", "终结", "彻底的失败", "背叛之痛"], ["触底反弹", "熬过去", "复原", "拒绝结束"]),
        (["好奇", "求知", "警觉", "直率"], ["口无遮拦", "流言", "多疑", "浮躁"]),
        (["果断", "疾速行动", "直言", "冲锋"], ["鲁莽", "咄咄逼人", "冲动", "不计后果"]),
        (["理性", "洞察", "独立", "边界清晰"], ["尖刻", "冷漠", "苛刻", "伤人于无形"]),
        (["理智", "权威", "公正的判断", "逻辑"], ["专断", "冷酷", "滥用理智", "操控"]),
    ]),
    ("pentacles", "星币", "土", [
        (["新机会", "物质起点", "务实", "富足的开端"], ["机会流失", "计划落空", "财务不稳", "贪小失大"]),
        (["权衡", "灵活", "多线并行", "收支平衡"], ["失衡", "顾此失彼", "手忙脚乱", "入不敷出"]),
        (["协作", "技艺", "分工", "稳步建设"], ["配合不佳", "敷衍", "品质堪忧", "各自为政"]),
        (["保守", "储蓄", "掌控资源", "安全感"], ["吝啬", "过度占有", "固守", "放手"]),
        (["匮乏", "困顿", "被排斥", "物质焦虑"], ["转机", "走出困境", "得到援手", "复苏"]),
        (["施与受", "慷慨", "公平分配", "援助"], ["施舍的不平等", "依赖", "人情债", "被利用"]),
        (["耐心等待", "评估", "长期投入", "耕耘"], ["急于求成", "投入无果", "方向错误", "半途而废"]),
        (["专注", "精进", "手艺", "踏实积累"], ["敷衍了事", "缺乏动力", "重复劳作", "眼高手低"]),
        (["自足", "独立", "享受成果", "优雅"], ["过度依赖物质", "孤独", "挥霍", "表面的安逸"]),
        (["富足", "传承", "家业", "长期的稳定"], ["财务纠纷", "家族矛盾", "短视", "根基不稳"]),
        (["学习", "踏实起步", "求知", "小额机会"], ["拖延", "不切实际", "浪费", "缺乏耐心"]),
        (["稳健", "可靠", "按部就班", "勤恳"], ["僵化", "拖沓", "无趣", "停滞不前"]),
        (["务实", "滋养", "安全感", "经营有方"], ["过度操心", "物质焦虑", "忽视自我", "掌控欲"]),
        (["富足", "稳健", "事业有成", "慷慨的掌控"], ["贪财", "固执", "唯利是图", "固守成规"]),
    ]),
]


# --------------------------------------------------------------------------
# Spreads
# --------------------------------------------------------------------------

# name -> list of (position, hint)
SPREADS = {
    "single": [
        ("指引", "此刻最需要看见的"),
    ],
    "three_card": [
        ("过去", "事情的来处"),
        ("现在", "当下的真实处境"),
        ("未来", "自然的走向"),
    ],
    "yes_no": [
        ("支持", "推动“是”的力量"),
        ("反对", "推动“否”的力量"),
        ("综合", "整体倾向"),
    ],
    "relationship": [
        ("你", "你在关系中的状态"),
        ("对方", "对方的状态"),
        ("关系", "两人之间的实际联结"),
        ("走向", "关系的自然趋势"),
    ],
    "celtic_cross": [
        ("现状", "当下的核心处境"),
        ("挑战", "横亘其上的阻碍或助力"),
        ("根基", "潜意识的根源"),
        ("过去", "刚过去、正在离场的影响"),
        ("目标", "意识层面的期待或目标"),
        ("近期未来", "不久将到来的事"),
        ("自我", "你的态度与姿态"),
        ("环境", "他人与外部条件"),
        ("希望与恐惧", "你最期盼也最害怕的"),
        ("结果", "事情的自然归宿"),
    ],
}

MAX_CARDS = 78
ELEMENTS = ("火", "水", "风", "土")


def build_deck():
    deck = []
    for num, name, up, rev in MAJORS:
        deck.append({"name": name, "label": f"大阿尔卡那 {num}", "element": None, "up": up, "rev": rev})
    for _, suit, element, rows in SUITS:
        for i, (up, rev) in enumerate(rows):
            deck.append({"name": suit + RANKS[i], "label": f"{suit}·{element}", "element": element, "up": up, "rev": rev})
    return deck


def fail(message):
    print(f"错误：{message}")
    sys.exit(1)


def positions_of(args):
    raw = args.get("positions")
    spread = args.get("spread") or ("custom" if raw else "single")
    if spread != "custom":
        if spread not in SPREADS:
            fail(f"没有牌阵 {spread!r}，可选：{'、'.join(SPREADS)}、custom")
        if raw:
            fail("positions 只配 spread=custom 用")
        return spread, SPREADS[spread]
    if not isinstance(raw, list) or not raw:
        fail('spread=custom 要给 positions，例：["现状", "行动", "结果"]')
    if len(raw) > MAX_CARDS:
        fail(f"至多 {MAX_CARDS} 个位置，一副牌只有 {MAX_CARDS} 张")
    out = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.append((item.strip(), None))
        elif isinstance(item, dict) and isinstance(item.get("name"), str) and item["name"].strip():
            hint = item.get("hint")
            out.append((item["name"].strip(), hint.strip() if isinstance(hint, str) and hint.strip() else None))
        else:
            fail(f"位置要写成名字，或 {{name, hint}}：{item!r}")
    return spread, out


def main():
    try:
        args = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        fail(f"参数不是 JSON：{exc}")
    spread, positions = positions_of(args)
    reversal = args.get("reversal", 0.3)
    if isinstance(reversal, bool) or not isinstance(reversal, (int, float)) or not 0 <= reversal <= 1:
        fail("reversal 要是 0 到 1 之间的数")
    keywords = args.get("keywords", True) is not False
    question = str(args.get("question") or "").strip()

    rng = secrets.SystemRandom()
    deck = build_deck()
    rng.shuffle(deck)  # 洗一次，从上往下发：同一次不会重复

    lines = [f"牌阵：{spread}，{len(positions)} 张" + (f"；问题：{question}" if question else "")]
    counts = {e: 0 for e in ELEMENTS}
    majors = reversed_count = 0
    for n, ((position, hint), card) in enumerate(zip(positions, deck), 1):
        is_rev = rng.random() < reversal
        reversed_count += is_rev
        if card["element"]:
            counts[card["element"]] += 1
        else:
            majors += 1
        head = f"{n}. **{position}**" + (f"（{hint}）" if hint else "")
        line = f"{head}：{card['name']} {'逆位' if is_rev else '正位'}　[{card['label']}]"
        if keywords:
            line += "　" + "、".join(card["rev"] if is_rev else card["up"])
        lines.append(line)
    element_text = "、".join(f"{e}{c}" for e, c in counts.items() if c)
    lines.append(f"合计：大阿尔卡那 {majors} 张，逆位 {reversed_count} 张" + (f"；小阿尔卡那元素 {element_text}" if element_text else ""))
    print("\n".join(lines))


if __name__ == "__main__":
    main()

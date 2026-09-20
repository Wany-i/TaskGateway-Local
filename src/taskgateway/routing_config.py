"""Deterministic routing constants for TaskGateway-Local."""

TYPE_WEIGHT = {
    "library": 1.15,
    "connector": 1.10,
    "skill": 1.00,
    "tool": 1.05,
    "ledger": 1.10,
    "standard": 0.85,
    "guard": 0.85,
    "principle": 0.80,
}
STOP_WORDS = {
    "什么", "怎么", "如何", "哪些", "哪个", "一下", "帮我", "看看",
    "是否", "可以", "需要", "想要", "关于", "一个", "我要", "我想",
}
HINTS = (
    (
        ("清理", "磁盘", "空间", "垃圾", "腾出", "瘦身", "c盘", "硬盘"),
        ("windows", "空间", "磁盘", "清理", "垃圾", "trash", "space"),
    ),
    (
        ("任务", "待办", "没做完", "进度", "任务板", "todo"),
        ("任务板", "task", "状态", "台账", "ledger", "board", "债务"),
    ),
    (
        ("多代理", "并行", "调研", "子代理", "团队", "分工"),
        ("团队", "编排", "并行", "调研", "agent-team", "orchestration"),
    ),
    (
        ("资料库", "哪个库", "知识库", "找资料", "文件在"),
        ("资料库", "索引", "检索", "find", "library"),
    ),
)
ALIASES = {
    "速卖通": "aliexpress",
    "淘宝": "taobao",
    "天猫": "tmall",
    "小红书": "xiaohongshu",
    "拼多多": "pinduoduo",
    "抖音": "douyin",
}
TYPE_LABEL = {
    "library": "资料库",
    "connector": "连接器",
    "skill": "技能",
    "tool": "工具",
    "ledger": "台账",
    "standard": "规范",
    "guard": "护栏",
    "principle": "原则",
}
PRIMARY_RULES = (
    ("coding", ("代码", "编程", "开发", "修复", "测试", "python", "git")),
    ("docs", ("文档", "报告", "总结", "写作", "说明")),
    ("browser", ("浏览器", "网页", "网站", "chrome", "抓取")),
    ("automation", ("自动化", "定时", "工作流", "批处理", "脚本")),
    ("sandbox", ("沙箱", "隔离", "临时环境")),
    ("evaluation", ("评估", "验收", "测试集", "命中率")),
    ("research", ("调研", "研究", "查找", "检索", "资料")),
)
READ_ORDER = (
    "norms", "process", "skills_tools", "references", "stop_conditions"
)

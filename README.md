# Life Designer — AI 人生设计师

> **不是帮你「想清楚」，是陪你「走出来」。**

一个基于斯坦福 d.school Life Design Lab 方法论的 AI 人生设计教练 Skill。通过多轮深度对话，帮你看清现状、找到真问题、生成三个五年人生版本，最终输出一份 8000-12000 字的《个人人生设计蓝图》。

---

## 灵感来源

本项目灵感来自公众号「数字生命卡兹克」的文章《我把斯坦福最火的一门课，做成了Prompt来帮我设计人生》。文章介绍了如何将 Bill Burnett & Dave Evans 在斯坦福开设的 Life Design 课程设计成 AI Prompt。本项目在此基础上进行了大幅扩展：

- 融入 6 大理论体系（心流、PERMA、黄金圈、无限游戏、成长型思维等）
- 设计了完整的四阶段深度对话流程
- 增加了情感共鸣引擎（镜像效应、矛盾揭示、正常化等 6 个机制）
- 输出精美的 HTML 格式人生设计蓝图
- 涵盖 20+ 本核心参考书目的理论支撑

## 理论基础

| 理论体系 | 核心书目 | 作者 |
|---------|---------|------|
| 设计思维人生方法论 | *Designing Your Life* | Bill Burnett & Dave Evans |
| 心流理论 | *Flow* | Mihaly Csikszentmihalyi |
| 积极心理学 PERMA | *Flourish* | Martin Seligman |
| 黄金圈 & 无限游戏 | *Start with Why* / *The Infinite Game* | Simon Sinek |
| 成长型思维 | *Mindset* | Carol Dweck |
| 意义感与选择 | *Man's Search for Meaning* | Viktor Frankl |

## 快速开始

### 前置要求

- [Claude Code](https://claude.ai/code) CLI 工具已安装
- 终端环境可正常使用

### 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/life-designer.git

# 将 skill 安装到 Claude Code 的 skills 目录
cp -r life-designer ~/.qoderwork/skills/life-designer
```

### 使用

在 Claude Code 中，使用以下触发词启动对话：

```
人生设计
人生规划
我迷茫了
不知道做什么
职业方向
设计我的人生
帮我梳理人生
life design
帮我想想未来
我卡住了
不知道该怎么选
```

### 对话流程

```
Phase 1: 你在这里（看清现状）
  ↓ 仪表盘打分 + 找到真问题
Phase 2: 你的指南针（校准方向）
  ↓ 工作观 + 人生观一致性检验
Phase 3: 寻路（发现能量模式）
  ↓ 心流时刻挖掘 + 能量公式
Phase 4: 多种可能（设计未来）
  ↓ 奥德赛计划 + 原型行动
  ↓
输出：《个人人生设计蓝图》(HTML)
```

## 项目结构

```
life-designer/
├── SKILL.md                    # Skill 定义文档（v3.0）
├── README.md                   # 本文件
├── LICENSE                     # MIT 许可证
└── assets/
    └── report-template.html    # HTML 报告模板
```

## 输出示例

对话结束后，你将获得一份 HTML 格式的《个人人生设计蓝图》，包含 7 个章节：

1. **你在这里** — 四维度仪表盘解读
2. **真问题** — 思维误区 → 重新定义
3. **你的指南针** — 工作观 + 人生观一致性诊断
4. **你的能量地图** — 心流活动 + 能量公式
5. **三个奥德赛计划** — 三个平等的五年人生版本
6. **原型行动清单** — 本周就能开始的最小行动
7. **失败免疫** — 人生是无限游戏

## 核心设计理念

### 六条核心信念

1. **人生是设计问题，没有唯一正解** — 它需要大量尝试、做原型、边走边看
2. **重新定义问题** — 很多人卡住不是没有答案，是在回答错误的问题
3. **接受重力问题** — 无法改变的现实不是问题，是现实
4. **数量本身含有质量** — 先逼出足够多可能性再挑
5. **激情是结果而非前提** — 靠做原型去试，激情是副产品
6. **人生是无限游戏** — 没有输赢，每次失败都在缩小搜索范围

### 共鸣引擎

这个 Skill 不只是信息收集，而是一次情感体验：

- **镜像效应** — 在报告中引用用户原话
- **矛盾揭示** — 温柔指出言行矛盾
- **正常化** — 让用户知道他的感受是正常的
- **具体化** — 用具体的故事回应，而非抽象建议
- **赋权结尾** — 让人安心，不是催人行动

## 参考书目

完整参考体系包含 20+ 本书籍和 13 个实践工具框架，详见 [SKILL.md](./SKILL.md) 第九章。

### 核心 9 本

| 书名 | 作者 |
|------|------|
| *Designing Your Life* | Bill Burnett & Dave Evans |
| *Designing Your New Work Life* | Bill Burnett & Dave Evans |
| *Flow* | Mihaly Csikszentmihalyi |
| *Authentic Happiness* | Martin Seligman |
| *Flourish* | Martin Seligman |
| *Start with Why* | Simon Sinek |
| *The Infinite Game* | Simon Sinek |
| *Mindset* | Carol Dweck |
| *Man's Search for Meaning* | Viktor Frankl |

### 深度补充 15 本

*Range*, *The Pathless Path*, *Transitions*, *The Art of Possibility*, *Atomic Habits*, *So Good They Can't Ignore You*, *Essentialism*, *The Second Mountain*, *Four Thousand Weeks*, *Ikigai*, *The Design of Everyday Things*, *Thinking, Fast and Slow*, *Grit*, *The Courage to Be Disliked*, *Finding Flow*

## 贡献

欢迎提交 Issue 和 PR：

- 改进对话流程和追问技巧
- 补充新的理论参考
- 优化 HTML 报告模板
- 修复 Bug

## 致谢

- **Bill Burnett & Dave Evans** — Stanford Life Design Lab 创始人，*Designing Your Life* 作者
- **数字生命卡兹克** — 原始灵感和文章来源
- **Stanford d.school** — 设计思维方法论的发源地

## License

MIT License - 详见 [LICENSE](./LICENSE)

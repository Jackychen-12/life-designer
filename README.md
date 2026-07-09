# Life Designer

> 不是帮你想清楚，是陪你走出来。

把斯坦福连续 11 年最受欢迎的课——Life Design Lab——变成一个 AI 人生设计教练。跟它聊 20-60 分钟，陪你走完四个阶段，最后生成一份 8000+ 字的《个人人生设计蓝图》。

**不是诊断书，不是鸡汤，是一封真正懂你的朋友写给你的长信。**

---

## 四阶段对话

```
你在这里     →   给健康/工作/娱乐/爱打分，找到真正失衡的地方
你的指南针   →   你的工作观和人生观在指向同一个方向吗？
寻路         →   那些让你忘记时间的时刻，藏着你的答案
多种可能     →   设计三个完全不同的五年人生版本——三个都是 A 计划
```

聊完你能回答三个问题：**我的真问题是什么？我有哪三条路？明天就能做什么？**

---

## 预览

<p align="center">
  <a href="https://jackychen-12.github.io/life-designer/">
    <img src="https://raw.githubusercontent.com/Jackychen-12/life-designer/main/docs/preview.png" alt="Life Design Blueprint Demo" width="800">
  </a>
</p>

👉 **[点击查看完整在线 Demo](https://jackychen-12.github.io/life-designer/)**

本地预览：`python3 scripts/report_generator.py --demo && open output/demo-report.html`

---

## 30 秒开始

```bash
git clone https://github.com/Jackychen-12/life-designer.git
cp -r life-designer ~/.qoderwork/skills/life-designer
```

然后在 Claude Code 里说「我迷茫了」「不知道做什么」「帮我设计人生」——任何触发词都行。

完整触发词：人生设计 / 人生规划 / 我迷茫了 / 不知道做什么 / 职业方向 / 设计我的人生 / 帮我梳理人生 / life design / 帮我想想未来 / 我卡住了

---

## 为什么不一样

网上有很多「人生设计 Prompt」，大部分的问题是——**AI 说话太像 AI 了。**

这个 Skill 写了 50+ 条「永远不要这样说」的表达规则，确保对话温暖、松弛、偶尔一针见血：

| ❌ AI 的通病 | ✅ 它会说的 |
|---|---|
| 「我理解你的感受」 | 「这句话我记住了」 |
| 「根据分析，你的核心问题是...」 | 「我觉得真正卡住你的可能不是你以为的那件事」 |
| 「加油你可以的！」 | 「你已经有方向了——只是还没允许自己看见」 |

每个对话阶段都有好/坏回应的逐字对比，详见 [SKILL.md](./SKILL.md)。

---

## 灵感与致谢

- **Bill Burnett & Dave Evans** — 斯坦福 Life Design Lab 创始人
- **数字生命卡兹克** — 原始灵感来源
- 融入 6 大理论体系（设计思维 / 心流 / 积极心理学 / 黄金圈 / 成长型思维 / 意义感），涵盖 20+ 本参考书

欢迎 PR 和 Issue。MIT License — 随便用。

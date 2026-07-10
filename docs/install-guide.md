# 安装指南 · 5 分钟开始你的人生设计对话

> 适合完全没用过 Claude Code 的朋友。跟着走，有问题开 Issue。

---

## 你需要准备

- 一台电脑（Mac / Windows / Linux）
- 一个 Anthropic 账号（Claude 的账号，免费注册：https://console.anthropic.com ）
- 大概 5 分钟安装时间 + 20-60 分钟对话时间

---

## 第一步：装 Node.js（已装过的可以跳过）

打开终端，输入：

```bash
node --version
```

如果看到 `v18.x` 或更高版本，直接跳到第二步。

如果没装：去 https://nodejs.org 下载 **LTS 版本**，一路 Next 装完。

---

## 第二步：装 Claude Code

在终端（Mac 叫「终端」，Windows 叫「PowerShell」）里粘贴这行：

```bash
npm install -g @anthropic-ai/claude-code
```

装完之后验证：

```bash
claude --version
```

能看到版本号就成功了。第一次运行 `claude` 会让你登录 Anthropic 账号，跟着提示走即可。

---

## 第三步：下载 Skill

### 方法一：git clone（推荐）

```bash
mkdir -p ~/.qoderwork/skills
git clone https://github.com/Jackychen-12/life-designer.git ~/.qoderwork/skills/life-designer
```

### 方法二：手动下载（不会用 git 的话）

1. 打开 https://github.com/Jackychen-12/life-designer
2. 点绿色的 **Code** 按钮 → **Download ZIP**
3. 解压后，把文件夹重命名为 `life-designer`
4. 移动到这个路径（没有的话先建）：

```bash
# Mac/Linux
mkdir -p ~/.qoderwork/skills
mv ~/Downloads/life-designer ~/.qoderwork/skills/

# Windows（PowerShell）
mkdir "$env:USERPROFILE\.qoderwork\skills" -Force
Move-Item "$env:USERPROFILE\Downloads\life-designer" "$env:USERPROFILE\.qoderwork\skills\"
```

---

## 第四步：开始对话

在终端里输入：

```bash
claude
```

进入 Claude Code 之后，说一句触发词就行。比如：

- 「我最近很迷茫」
- 「帮我设计人生」
- 「不知道自己在做什么」
- 「职业方向想不通」
- 「life design」

AI 会进入人生设计师角色，带你走完四个阶段。全程大概 20-60 分钟。

**一个小建议**：如果可以的话，试试用语音输入（手机开 Claude 网页版或者电脑的语音输入）。说出来比打字更容易碰到真实的想法。

---

## 第五步：拿到你的蓝图 + 时间胶囊

聊完之后会自动生成：

| 文件 | 是什么 | 怎么用 |
|---|---|---|
| `人生设计蓝图_xxx.html` | 8000+ 字的人生设计报告 | 双击用浏览器打开，建议收藏 |
| `人生设计蓝图_xxx.md` | Markdown 版本 | 方便复制、打印、做笔记 |
| `LD-xxxxx.ics` | 日历提醒文件 | **双击导入日历**（Google/Apple/Outlook 都行） |
| `LD-xxxxx-letter.html` | 30天/90天后的时间胶囊信件 | 到时间再打开，没到时间会显示 🔒 封印中 |

### 时间胶囊的用法

30 天和 90 天后，你的日历会弹提醒。到时候：

1. 找到当初保存的 `LD-xxxxx-letter.html`
2. 用浏览器打开
3. 如果日期到了，封印会解开，你会看到一封**那个下午的自己写给未来的你**的信

不是 AI 写的鸡汤。是你自己说过的话、做过的选择，被封存进一封信里。

---

## 常见问题

**Q：npm install 报错怎么办？**

试试用 sudo（Mac/Linux）：`sudo npm install -g @anthropic-ai/claude-code`

**Q：claude 命令找不到？**

可能是 npm 全局路径没加到 PATH。试试关掉终端重新打开。

**Q：我没有 Anthropic 账号/不想付费？**

Skill 的运行需要 Claude API 额度。目前 Anthropic 提供免费额度，足够完成 1-2 次完整对话。

**Q：能不能不装 Claude Code，直接在网页用？**

可以！去 https://claude.ai 创建一个 Project，把 `SKILL.md` 的内容复制粘贴到 Project Instructions 里，然后开始对话。效果一样，只是没有自动生成 HTML 报告的功能。

**Q：报告生成后怎么找到文件？**

文件在 `life-designer/output/` 目录下。或者直接：

```bash
open ~/.qoderwork/skills/life-designer/output/  # Mac
explorer "$env:USERPROFILE\.qoderwork\skills\life-designer\output"  # Windows
```

---

## 还是装不上？

开一个 Issue 告诉我卡在哪一步：https://github.com/Jackychen-12/life-designer/issues

我会尽量在 24 小时内回复。

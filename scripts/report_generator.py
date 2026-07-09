#!/usr/bin/env python3
"""
report_generator.py v2 — 人生设计蓝图报告生成器

新架构：AI 输出富文本 JSON（自由叙事内容块）→ 脚本渲染成精美 HTML
不再是「填格子」，而是「AI 写作 + 脚本排版」。

用法：
  python3 scripts/report_generator.py --input data.json
  python3 scripts/report_generator.py --input data.json --output report.html
  python3 scripts/report_generator.py --input data.json --demo   # 生成示范报告
"""

import json
import sys
import os
import argparse
import hashlib
import subprocess
from datetime import datetime, timedelta

# ============================================================
# 颜色常量（与 CSS 变量一致）
# ============================================================

COLORS = {
    'accent': '#C86A4A',
    'accent_deep': '#A85238',
    'green': '#5A8A62',
    'blue': '#4A7A9C',
    'warm': '#7D6B52',
}

DIM_META = {
    'health':  {'label': '健康', 'color': '#5A8A62', 'hint': '身体·情绪·心理'},
    'work':    {'label': '工作', 'color': '#C86A4A', 'hint': '认同感·意义感'},
    'play':    {'label': '娱乐', 'color': '#4A7A9C', 'hint': '纯粹的快乐'},
    'love':    {'label': '爱',   'color': '#7D6B52', 'hint': '双向的连接'},
}

# ============================================================
# HTML 构建器
# ============================================================

def build_css():
    """构建完整的 CSS 样式表（style-c 禅意基调）"""
    return '''
:root {
  --bg: #FAFAF8;
  --ink: #1A1A1A;
  --ink-2: #2A2A28;
  --stone: #6B6B6B;
  --mist: #B8B4AC;
  --paper: #F0EDE6;
  --paper-2: #E8E4DA;
  --accent: #2B4C7E;
  --accent-soft: #D4DFEB;
  --accent-line: rgba(43, 76, 126, 0.18);
  --rule: #D8D4CC;
  --rule-hair: #E5E1D9;
  --serif: 'Noto Serif SC', 'Source Serif 4', serif;
  --sans: 'Noto Sans SC', 'Inter', sans-serif;
  --mono: 'IBM Plex Mono', 'JetBrains Mono', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  background: var(--bg);
  color: var(--ink);
  font-family: var(--sans);
  font-weight: 300;
  line-height: 1.9;
  letter-spacing: 0.02em;
  -webkit-font-smoothing: antialiased;
}

/* 纸质噪点纹理 —— style-c 灵魂之一 */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
  opacity: 0.4;
}

.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 40px;
}

/* ─── MASTHEAD ─── */
.masthead {
  padding: 48px 0 36px;
  border-bottom: 1px solid var(--rule);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.masthead-left {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--stone);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  line-height: 1.6;
}
.masthead-right {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--mist);
  text-align: right;
  letter-spacing: 0.1em;
  line-height: 1.6;
}

/* ─── HERO ─── */
.hero {
  padding: 64px 0 48px;
  text-align: center;
}
.hero-label {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--mist);
  letter-spacing: 0.3em;
  text-transform: uppercase;
  margin-bottom: 20px;
}
.hero-title {
  font-family: var(--serif);
  font-size: 2.4rem;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.01em;
  margin-bottom: 16px;
}
.hero-subtitle {
  font-size: 1rem;
  color: var(--stone);
  font-weight: 400;
  max-width: 440px;
  margin: 0 auto;
  line-height: 1.75;
}
.hero-meta {
  margin-top: 32px;
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--mist);
  letter-spacing: 0.1em;
}

/* ─── DIVIDER ─── */
.divider {
  width: 40px;
  height: 1px;
  background: var(--rule);
  margin: 40px auto;
}
.divider-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--mist);
  margin: 40px auto;
}

/* ─── SECTION ─── */
.section {
  padding: 32px 0;
}
.section-number {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--mist);
  letter-spacing: 0.2em;
  margin-bottom: 12px;
}
.section-title {
  font-family: var(--serif);
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 20px;
  line-height: 1.4;
}
.section-body {
  font-size: 1rem;
  color: var(--ink);
  line-height: 1.8;
}
.section-body p {
  margin-bottom: 1em;
}
.section-body strong { font-weight: 500; color: var(--ink-2); }
.section-body em { font-style: italic; color: var(--stone); }

/* 章节题记（P1 新增：section 标题下的用户原话） */
.section-epigraph {
  font-family: var(--serif);
  font-style: italic;
  font-size: 1rem;
  color: var(--stone);
  border-left: 1px solid var(--accent-line);
  padding: 4px 0 4px 18px;
  margin: -4px 0 20px 0;
  line-height: 1.7;
  max-width: 560px;
}
.section-epigraph .attr {
  display: block;
  font-family: var(--mono);
  font-style: normal;
  font-size: 0.65rem;
  color: var(--mist);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-top: 10px;
}

/* ─── KPI STRIP ─── */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--rule);
  border-bottom: 1px solid var(--rule);
  margin: 28px 0 12px;
}
.kpi {
  padding: 28px 12px;
  text-align: center;
  border-right: 1px solid var(--rule);
}
.kpi:last-child { border-right: none; }
.kpi-value {
  font-family: var(--mono);
  font-size: 2rem;
  font-weight: 400;
  line-height: 1;
  margin-bottom: 10px;
}
.kpi-value::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--kpi-color, var(--accent));
  margin-right: 6px;
  vertical-align: middle;
  position: relative;
  top: -2px;
}
.kpi-label {
  font-family: var(--serif);
  font-size: 0.8rem;
  color: var(--stone);
  letter-spacing: 0.08em;
}

/* KPI 注解（P1 新增：每个分数下一句 mono 小字） */
.kpi-notes {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  margin-bottom: 40px;
  border-bottom: 1px solid var(--rule-hair);
}
.kpi-note {
  padding: 12px 16px 20px;
  border-right: 1px solid var(--rule-hair);
  font-family: var(--mono);
  font-size: 0.7rem;
  line-height: 1.7;
  color: var(--stone);
  text-align: center;
}
.kpi-note:last-child { border-right: none; }

/* ─── INSIGHT (简约内联) ─── */
.insight-card {
  margin: 20px 0;
  padding: 0;
}
.insight-label {
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--stone);
  letter-spacing: 0.08em;
  margin-bottom: 8px;
  font-weight: 500;
}
.insight-text {
  font-family: var(--serif);
  font-size: 0.95rem;
  line-height: 1.85;
  color: var(--ink-2);
}

/* ─── PULL QUOTE ─── */
.pull-quote {
  padding: 32px 0;
  text-align: center;
}
.pull-quote-mark {
  font-family: var(--serif);
  font-size: 3rem;
  color: var(--accent-soft);
  line-height: 1;
  margin-bottom: -12px;
}
.pull-quote-text {
  font-family: var(--serif);
  font-size: 1.2rem;
  font-weight: 400;
  line-height: 1.7;
  max-width: 560px;
  margin: 0 auto;
  color: var(--ink);
}
.pull-quote-source {
  margin-top: 12px;
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--mist);
  letter-spacing: 0.1em;
}

/* ─── SCORE BARS ─── */
.score-bars {
  margin: 24px 0 8px;
}
.score-bar {
  display: grid;
  grid-template-columns: 48px 1fr 36px;
  gap: 12px;
  align-items: center;
  padding: 10px 0;
}
.score-bar-label {
  font-family: var(--serif);
  font-size: 0.88rem;
  color: var(--ink);
  font-weight: 500;
}
.score-bar-track {
  height: 4px;
  background: var(--rule-hair);
  border-radius: 2px;
  position: relative;
  overflow: hidden;
}
.score-bar-fill {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  border-radius: 2px;
  transition: width 0.6s ease;
}
.score-bar-val {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--stone);
  text-align: right;
}

/* ─── REFRAME 四步对照（P1 新增） ─── */
.reframe-grid {
  margin: 24px 0;
  padding: 24px 28px;
  background: var(--paper);
  font-family: var(--mono);
  font-size: 0.85rem;
  line-height: 1.9;
}
.reframe-row {
  display: grid;
  grid-template-columns: 130px 20px 1fr;
  gap: 12px;
  align-items: baseline;
  padding: 4px 0;
}
.reframe-key {
  color: var(--mist);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-size: 0.7rem;
}
.reframe-arrow {
  color: var(--accent);
  text-align: center;
}
.reframe-val {
  color: var(--ink);
  font-family: var(--sans);
  font-size: 0.9rem;
  line-height: 1.8;
}
.reframe-val.real { font-weight: 500; color: var(--accent); }

/* ─── COMPASS 罗盘对齐（P1 增强） ─── */
.compass-pair {
  display: grid;
  grid-template-columns: 1fr 20px 1fr;
  gap: 16px;
  align-items: center;
  margin: 24px 0 16px;
  padding: 24px 0;
  border-top: 1px solid var(--rule-hair);
  border-bottom: 1px solid var(--rule-hair);
}
.compass-cell { text-align: center; padding: 0 8px; }
.compass-cell-label {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--mist);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.compass-cell-text {
  font-family: var(--serif);
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--ink);
}
.compass-connector {
  font-family: var(--mono);
  color: var(--accent);
  text-align: center;
  font-size: 1.2rem;
}
.compass-verdict {
  text-align: center;
  font-family: var(--mono);
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  color: var(--accent);
  margin-top: 4px;
}

/* ─── ENERGY 2x2 网格（P1 新增） ─── */
.energy-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-top: 1px solid var(--rule);
  border-left: 1px solid var(--rule);
  margin: 24px 0;
}
.energy-cell {
  padding: 20px 20px;
  border-right: 1px solid var(--rule);
  border-bottom: 1px solid var(--rule);
  min-height: 120px;
}
.energy-cell-label {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--mist);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-bottom: 16px;
}
.energy-cell-list {
  font-family: var(--serif);
  font-size: 0.95rem;
  line-height: 1.9;
  color: var(--ink);
  padding: 0;
  margin: 0;
  list-style: none;
}
.energy-cell-list li { padding: 3px 0; }
.energy-cell-list li::before {
  content: '·';
  color: var(--accent);
  margin-right: 10px;
  font-weight: 700;
}

/* ─── ODYSSEY ─── */
.odyssey-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: 32px 0 0;
}
.odyssey-card {
  background: var(--bg);
  border: 1px solid var(--rule);
  border-top: 3px solid var(--plan-color, var(--accent));
  padding: 20px 18px;
  position: relative;
  transition: all 0.25s ease;
  cursor: pointer;
}
.odyssey-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}
.odyssey-card.active {
  border-color: var(--plan-color, var(--accent));
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}
.odyssey-card::before {
  content: attr(data-plan);
  position: absolute;
  top: 10px;
  right: 14px;
  font-family: var(--mono);
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--plan-color, var(--accent));
  opacity: 0.1;
  line-height: 1;
}
.odyssey-tag {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--plan-color, var(--accent));
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 6px;
  font-weight: 500;
}
.odyssey-title {
  font-family: var(--serif);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 14px;
  line-height: 1.35;
}
.odyssey-body {
  font-size: 0.85rem;
  color: var(--stone);
  line-height: 1.7;
  margin-bottom: 12px;
}

.odyssey-card-hint {
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--mist);
  text-align: right;
  margin-top: 10px;
  letter-spacing: 0.06em;
  transition: color 0.2s;
}
.odyssey-card:hover .odyssey-card-hint { color: var(--plan-color, var(--accent)); }
.odyssey-card.active .odyssey-card-hint { display: none; }

/* 全宽详情面板 */
.odyssey-detail-full {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.5s ease, opacity 0.35s ease, margin 0.35s ease;
  opacity: 0;
  margin-top: 0;
  border: 1px solid transparent;
  border-top: 3px solid var(--accent);
  background: var(--bg);
}
.odyssey-detail-full.active {
  max-height: 1200px;
  opacity: 1;
  margin-top: 24px;
  border-color: var(--rule);
}
.odyssey-detail-label {
  font-family: var(--mono);
  font-size: 0.58rem;
  color: var(--mist);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.odyssey-detail-inner {
  padding: 28px 32px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

/* 奥德赛时间线 */
.odyssey-timeline {
  padding: 0;
  background: none;
  font-size: 0.88rem;
  line-height: 1.9;
  color: var(--ink);
}
.odyssey-timeline p { margin-bottom: 12px; }
.odyssey-timeline p:last-child { margin-bottom: 0; }
.odyssey-timeline .yr {
  color: var(--plan-color, var(--accent));
  font-weight: 600;
  letter-spacing: 0.08em;
  margin-right: 8px;
}

.odyssey-detail-questions {
  list-style: none;
  padding: 0;
  margin: 0;
}
.odyssey-detail-questions li {
  font-family: var(--serif);
  font-style: italic;
  font-size: 0.9rem;
  color: var(--ink);
  padding: 8px 0;
  border-bottom: 1px solid var(--rule-hair);
  line-height: 1.6;
}
.odyssey-detail-questions li:last-child { border-bottom: none; }
.odyssey-detail-questions li::before {
  content: '?';
  color: var(--plan-color, var(--accent));
  font-weight: 600;
  margin-right: 10px;
  font-style: normal;
}

/* 奥德赛四维评估条 */
.odyssey-eval {
  margin-top: 10px;
  display: grid;
  grid-template-columns: 64px 1fr 28px;
  gap: 8px;
  align-items: center;
  padding: 5px 0;
  font-family: var(--mono);
  font-size: 0.6rem;
}
.odyssey-eval-label {
  color: var(--mist);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.odyssey-eval-bar {
  height: 2px;
  background: var(--rule-hair);
  position: relative;
}
.odyssey-eval-bar::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  background: var(--plan-color, var(--accent));
  width: var(--val, 50%);
}
.odyssey-eval-val {
  text-align: right;
  color: var(--stone);
}

/* 奥德赛想问自己的问题 */
.odyssey-questions {
  margin: 0;
  font-family: var(--serif);
  font-style: italic;
  font-size: 0.78rem;
  color: var(--stone);
  line-height: 1.7;
  padding-left: 0;
  list-style: none;
}
.odyssey-questions li {
  padding: 3px 0;
}
.odyssey-questions li::before {
  content: '— ';
  color: var(--plan-color, var(--accent));
  font-style: normal;
}

/* ─── ACTIONS 四组 timeline（P1 增强） ─── */
.actions-group {
  margin: 20px 0;
}
.actions-group-title {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--accent);
  letter-spacing: 0.25em;
  text-transform: uppercase;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--rule-hair);
}
.timeline {
  margin: 12px 0 0;
  position: relative;
  padding-left: 32px;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 8px;
  bottom: 8px;
  width: 1px;
  background: var(--rule);
}
.timeline-item {
  position: relative;
  padding-bottom: 22px;
  display: grid;
  grid-template-columns: 18px 1fr;
  gap: 14px;
  align-items: start;
}
.timeline-item:last-child { padding-bottom: 0; }
.timeline-item::before {
  content: '';
  position: absolute;
  left: -29px;
  top: 8px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
}
.timeline-check {
  width: 14px;
  height: 14px;
  border: 1px solid var(--mist);
  margin-top: 5px;
  cursor: pointer;
  font-family: var(--mono);
  font-size: 0.8rem;
  line-height: 12px;
  text-align: center;
  color: transparent;
  transition: all 0.2s;
  user-select: none;
}
.timeline-check.checked {
  color: var(--accent);
  border-color: var(--accent);
}
.timeline-text {
  font-size: 0.9rem;
  line-height: 1.8;
}

/* ─── FUTURE LETTER ─── */
.letter-wrap {
  background: var(--paper);
  padding: 40px 32px;
  margin: 32px 0;
  position: relative;
}
.letter-wrap::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  border: 1px solid var(--rule);
  pointer-events: none;
}
.letter-date {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--mist);
  letter-spacing: 0.1em;
  margin-bottom: 24px;
}
.letter-greeting {
  font-family: var(--serif);
  font-size: 1.1rem;
  margin-bottom: 24px;
}
.letter-body {
  font-size: 1rem;
  line-height: 1.8;
  color: var(--ink);
}
.letter-body p { margin-bottom: 1em; }
.letter-sign {
  margin-top: 32px;
  font-family: var(--serif);
  font-style: italic;
  color: var(--stone);
}

/* ─── GOLDEN QUOTE (简约内联) ─── */
.golden-quote {
  padding: 40px 20px;
  margin: 24px 0;
  text-align: center;
}
.golden-quote-text {
  font-family: var(--serif);
  font-size: 1.15rem;
  font-weight: 400;
  line-height: 1.9;
  color: var(--ink);
  margin: 0 0 14px;
  font-style: italic;
}
.golden-quote-author {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--mist);
  letter-spacing: 0.1em;
}

/* ─── CLOSING QUOTE (简约内联) ─── */
.closing-quote {
  padding: 28px 0;
  text-align: center;
  margin-top: 20px;
}
.closing-quote-line {
  width: 20px;
  height: 1px;
  background: var(--mist);
  margin: 0 auto 20px;
}
.closing-quote-text {
  font-family: var(--serif);
  font-size: 1.05rem;
  font-weight: 400;
  line-height: 1.85;
  max-width: 480px;
  margin: 0 auto 14px;
  color: var(--ink);
}
.closing-quote-author {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--mist);
  letter-spacing: 0.12em;
}

/* ─── APPOINTMENT：时间胶囊封存说明 ─── */
.appointment {
  padding: 40px 0 48px;
  text-align: center;
}
.appointment-desc {
  font-family: var(--serif);
  font-size: 0.95rem;
  color: var(--ink);
  line-height: 1.9;
  max-width: 440px;
  margin: 0 auto 20px;
}
.appointment-date {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--stone);
  letter-spacing: 0.1em;
  margin-bottom: 16px;
}
.appointment-hint {
  font-family: var(--sans);
  font-size: 0.82rem;
  color: var(--mist);
  line-height: 1.8;
  max-width: 400px;
  margin: 0 auto;
}

/* ─── MD 双载体：复制/下载按钮（P3） ─── */
.md-actions {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 40px 0 20px;
}
.md-btn {
  font-family: var(--mono);
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--stone);
  background: transparent;
  border: 1px solid var(--rule);
  padding: 10px 20px;
  cursor: pointer;
  transition: all 0.2s;
}
.md-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--bg);
}
.md-btn.copied { color: var(--accent); border-color: var(--accent); }

/* ─── FOOTER ─── */
.footer {
  padding: 40px 0;
  border-top: 1px solid var(--rule);
  text-align: center;
}
.footer-text {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--mist);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  line-height: 2.4;
}
.footer-capsule {
  margin-top: 12px;
  font-size: 0.6rem;
  color: var(--mist);
  letter-spacing: 0.1em;
  text-transform: none;
}

/* responsive */
@media (max-width: 640px) {
  .page { padding: 0 24px; }
  .hero-title { font-size: 2rem; }
  .kpi-strip, .kpi-notes { grid-template-columns: repeat(2, 1fr); }
  .kpi:nth-child(2), .kpi-note:nth-child(2) { border-right: none; }
  .kpi:nth-child(1), .kpi:nth-child(2),
  .kpi-note:nth-child(1), .kpi-note:nth-child(2) { border-bottom: 1px solid var(--rule-hair); }
  .letter-wrap { padding: 40px 24px; }
  .reframe-grid { padding: 24px 20px; }
  .reframe-row { grid-template-columns: 100px 18px 1fr; }
  .compass-pair { grid-template-columns: 1fr; }
  .compass-connector { display: none; }
  .energy-grid { grid-template-columns: 1fr; }
  .odyssey-grid { grid-template-columns: 1fr; }
  .odyssey-card::before { font-size: 2rem; }
  .odyssey-eval { grid-template-columns: 80px 1fr 40px; }
  .odyssey-detail-inner { grid-template-columns: 1fr; padding: 20px 18px; }
}

@media print {
  body::before { display: none; }
  .md-actions { display: none; }
}
'''


def build_score_bars(scores):
    """四段水平进度条替代雷达图（Mixing Board 风格）。
    scores: dict like {"health": 7, "work": 5, "play": 3, "love": 8}
    """
    dims = ['health', 'work', 'play', 'love']
    html = '<div class="score-bars">\n'
    for dim in dims:
        score = min(max(scores.get(dim, 0), 0), 10)
        meta = DIM_META.get(dim, {})
        label = meta.get('label', dim)
        color = meta.get('color', 'var(--accent)')
        pct = score * 10
        html += (
            f'  <div class="score-bar">'
            f'<span class="score-bar-label">{label}</span>'
            f'<span class="score-bar-track">'
            f'<span class="score-bar-fill" style="width:{pct}%;background:{color}"></span>'
            f'</span>'
            f'<span class="score-bar-val">{score}/10</span>'
            f'</div>\n'
        )
    html += '</div>\n'
    return html


def build_section(num, title, content_html, epigraph=None):
    """style-c 基调的章节容器；epigraph 是可选的用户原话章节题记 dict {"text":..., "phase":...}"""
    epi = ""
    if epigraph and epigraph.get("text"):
        phase = epigraph.get("phase") or "对话中"
        epi = (
            f'    <div class="section-epigraph">'
            f'"{epigraph["text"]}"'
            f'<span class="attr">— 你 · {phase}</span>'
            f'</div>\n'
        )
    return f'''
  <section class="section">
    <div class="section-number">{num:02d}</div>
    <h2 class="section-title">{title}</h2>
{epi}    <div class="section-body">
{content_html}
    </div>
  </section>
'''





def build_dashboard_html(dashboard):
    """01 你在这里：narrative + KPI + KPI 注解 + insight + radar"""
    html = ''
    if dashboard.get('narrative'):
        html += f"{dashboard['narrative']}\n"

    scores = dashboard.get('scores') or {}
    if scores:
        # KPI 分数条
        html += '</div>\n'  # 关闭 section-body，让 KPI 横铺
        html += '    <div class="kpi-strip">\n'
        for k in ['health', 'work', 'play', 'love']:
            item = scores.get(k) or {}
            val = item.get('score', '—') if isinstance(item, dict) else item
            label = DIM_META.get(k, {}).get('label', k)
            color = DIM_META.get(k, {}).get('color', 'var(--accent)')
            html += f'      <div class="kpi" style="--kpi-color: {color}"><div class="kpi-value" style="color: {color}">{val}</div><div class="kpi-label">{label}</div></div>\n'
        html += '    </div>\n'

        # KPI 注解（P1 新增）
        has_notes = any(isinstance(scores.get(k), dict) and scores.get(k, {}).get('note') for k in ['health','work','play','love'])
        if has_notes:
            html += '    <div class="kpi-notes">\n'
            for k in ['health', 'work', 'play', 'love']:
                item = scores.get(k) or {}
                note = item.get('note', '') if isinstance(item, dict) else ''
                html += f'      <div class="kpi-note">{note}</div>\n'
            html += '    </div>\n'
        html += '    <div class="section-body">\n'  # 重开 section-body

    if dashboard.get('analysis'):
        html += f"{dashboard['analysis']}\n"

    # 四段水平进度条（替代雷达图）
    if scores:
        bar_scores = {k: (v.get('score', 0) if isinstance(v, dict) else v) for k, v in scores.items()}
        html += build_score_bars(bar_scores)

    return html


def build_reframe_html(reframe):
    """02 真问题：narrative + 四步对照 + conclusion"""
    html = ''
    if reframe.get('narrative'):
        html += f"{reframe['narrative']}\n"

    # 四步对照（P1 核心）
    keys = [
        ('perceived',    '你以为的'),
        ('gravity',      '重力问题'),
        ('real',         '真   问题'),
        ('wrong_premise','错误前提'),
    ]
    rows = [(k, label) for k, label in keys if reframe.get(k)]
    if rows:
        html += '</div>\n    <div class="reframe-grid">\n'
        for k, label in rows:
            val = reframe.get(k, '')
            cls = 'reframe-val real' if k == 'real' else 'reframe-val'
            html += (
                f'      <div class="reframe-row">'
                f'<span class="reframe-key">{label}</span>'
                f'<span class="reframe-arrow">→</span>'
                f'<span class="{cls}">{val}</span>'
                f'</div>\n'
            )
        html += '    </div>\n    <div class="section-body">\n'

    if reframe.get('conclusion'):
        html += f"{reframe['conclusion']}\n"
    return html


def build_compass_html(compass):
    """03 指南针：工作观 vs 人生观 对齐图"""
    html = ''
    if compass.get('narrative'):
        html += f"{compass['narrative']}\n"

    work_view = compass.get('work_view', '')
    life_view = compass.get('life_view', '')
    alignment = compass.get('alignment', '')

    if work_view or life_view:
        connector = '↔' if alignment and '错位' not in alignment else '=='
        html += '</div>\n    <div class="compass-pair">\n'
        html += f'      <div class="compass-cell"><div class="compass-cell-label">工作观</div><div class="compass-cell-text">{work_view}</div></div>\n'
        html += f'      <div class="compass-connector">{connector}</div>\n'
        html += f'      <div class="compass-cell"><div class="compass-cell-label">人生观</div><div class="compass-cell-text">{life_view}</div></div>\n'
        html += '    </div>\n'
        if alignment:
            html += f'    <div class="compass-verdict">{alignment}</div>\n'
        html += '    <div class="section-body">\n'

    if compass.get('conclusion') or compass.get('diagnosis'):
        html += f"{compass.get('conclusion') or compass.get('diagnosis')}\n"
    return html


def build_energy_html(energy):
    """04 能量地图：2x2 四象限（P1 核心）"""
    html = ''
    if energy.get('narrative'):
        html += f"{energy['narrative']}\n"

    cells = [
        ('flow',            '心流时刻',    None),
        ('recharge',        '回血活动',    None),
        ('drain_but_good',  '擅长但耗能',  'drain'),
        ('lean_toward',     '偏  向',      'direction'),
    ]
    def _get_energy(key, fallback_key):
        val = energy.get(key)
        if not val and fallback_key:
            val = energy.get(fallback_key)
        return val

    has_any = any(_get_energy(k, fk) for k, _, fk in cells)
    if has_any:
        html += '</div>\n    <div class="energy-grid">\n'
        for key, label, fallback_key in cells:
            val = _get_energy(key, fallback_key)
            items = []
            if isinstance(val, list):
                items = val
            elif isinstance(val, str) and val:
                items = [val]
            html += '      <div class="energy-cell">\n'
            html += f'        <div class="energy-cell-label">{label}</div>\n'
            if items:
                html += '        <ul class="energy-cell-list">\n'
                for it in items:
                    html += f'          <li>{it}</li>\n'
                html += '        </ul>\n'
            html += '      </div>\n'
        html += '    </div>\n    <div class="section-body">\n'

    if energy.get('formula'):
        html += f'<div class="insight-card"><div class="insight-label">能量公式</div><div class="insight-text">{energy["formula"]}</div></div>\n'
    if energy.get('conclusion'):
        html += f"{energy['conclusion']}\n"

    return html


def build_odyssey_html(odyssey):
    """05 奥德赛三条路：三列卡片 + 点击展开全宽详情面板 + 四维评估条"""
    import json as _json
    html = ''
    if odyssey.get('narrative'):
        html += f"{odyssey['narrative']}\n"

    plans = odyssey.get('plans') or []
    if plans:
        html += '</div>\n    <div class="odyssey-grid">\n'
        tags = ['Plan A · 延续当下', 'Plan B · 另一条路', 'Plan C · 无限可能']
        colors = ['#C86A4A', '#5A8A62', '#4A7A9C']
        letters = ['A', 'B', 'C']
        plan_data = {}
        for i, plan in enumerate(plans):
            if not isinstance(plan, dict):
                continue
            tag = tags[i] if i < len(tags) else f'Plan · {i+1}'
            color = colors[i] if i < len(colors) else '#C86A4A'
            letter = letters[i] if i < len(letters) else 'X'
            title = plan.get('title', '')
            timeline = plan.get('timeline') or plan.get('summary') or ''
            body = plan.get('body') or ''
            questions = plan.get('questions') or []
            ev = plan.get('eval') or {}

            # 存储详情数据给 JS
            plan_data[letter] = {
                'tag': tag, 'title': title, 'color': color,
                'timeline': timeline, 'body': body, 'questions': questions
            }

            html += f'      <div class="odyssey-card" data-plan="{letter}" style="--plan-color: {color}" onclick="toggleOdyssey(this)">\n'
            html += f'        <div class="odyssey-tag">{tag}</div>\n'
            html += f'        <h3 class="odyssey-title">{title}</h3>\n'

            # 四维评估条（始终可见）
            if ev:
                for key, label in [('resources','资源'), ('like','喜欢'), ('confidence','信心'), ('alignment','对齐')]:
                    v = ev.get(key, 0)
                    try:
                        v = max(0, min(100, int(v)))
                    except Exception:
                        v = 0
                    html += (
                        f'        <div class="odyssey-eval">'
                        f'<span class="odyssey-eval-label">{label}</span>'
                        f'<span class="odyssey-eval-bar" style="--val: {v}%;"></span>'
                        f'<span class="odyssey-eval-val">{v}</span>'
                        f'</div>\n'
                    )

            html += f'        <div class="odyssey-card-hint">点击展开 ↓</div>\n'
            html += '      </div>\n'
        html += '    </div>\n'

        # 全宽详情面板（一个 div，内容由 JS 填充）
        html += '    <div class="odyssey-detail-full" id="odyssey-panel">\n'
        html += '      <div class="odyssey-detail-inner" id="odyssey-panel-inner">\n'
        html += '      </div>\n'
        html += '    </div>\n'

        # 把 plan 数据嵌入 JS
        html += f'    <script>var __odysseyPlans = {_json.dumps(plan_data, ensure_ascii=False)};</script>\n'
        html += '    <div class="section-body">\n'

    # 执行路径（execution）
    ex = odyssey.get('execution') or {}
    if ex:
        html += '<div class="insight-card"><div class="insight-label">执行路径</div>\n'
        if ex.get('anti_vision'):
            html += f'<p style="margin-bottom:8px;"><strong style="color:var(--accent);">反愿景：</strong>{ex["anti_vision"]}</p>\n'
        if ex.get('vision'):
            html += f'<p style="margin-bottom:8px;"><strong style="color:#5A8A62;">愿  景：</strong>{ex["vision"]}</p>\n'
        if ex.get('quarter_q'):
            html += f'<p style="margin-bottom:8px;"><strong>本季度核心问题：</strong>{ex["quarter_q"]}</p>\n'
        if ex.get('month_proto'):
            html += f'<p style="margin-bottom:8px;"><strong>本月原型：</strong>{ex["month_proto"]}</p>\n'
        if ex.get('daily'):
            html += f'<p style="margin-bottom:8px;"><strong>每日习惯：</strong>{ex["daily"]}</p>\n'
        if ex.get('bottom_line'):
            html += f'<p><strong>底线规则：</strong>{ex["bottom_line"]}</p>\n'
        html += '</div>\n'

    if odyssey.get('conclusion'):
        html += f"{odyssey['conclusion']}\n"

    return html


ACTION_GROUPS = [
    ('talk', '谈  ·  TALK'),
    ('try',  '试  ·  TRY'),
    ('step', '走  ·  GO'),
    ('habit','醒  ·  WAKE'),
]

def build_actions_html(actions):
    """06 原型行动清单：分四组 timeline + 可勾选（P1 核心）"""
    html = ''
    if actions.get('narrative'):
        html += f"{actions['narrative']}\n"

    html += '</div>\n'
    for key, title in ACTION_GROUPS:
        items = actions.get(key)
        if not items:
            continue
        if isinstance(items, str):
            items = [items]

        html += '    <div class="actions-group">\n'
        html += f'      <div class="actions-group-title">{title}</div>\n'
        html += '      <div class="timeline">\n'
        for i, item in enumerate(items):
            text = item if isinstance(item, str) else item.get('what', '')
            html += (
                f'        <div class="timeline-item">'
                f'<span class="timeline-check" data-idx="{key}-{i}">✓</span>'
                f'<div class="timeline-text">{text}</div>'
                f'</div>\n'
            )
        html += '      </div>\n'
        html += '    </div>\n'
    html += '    <div class="section-body">\n'
    return html


def build_quote_card_html(quote):
    """金句卡：横线 + 大字 + author"""
    text = quote.get('text', '') if isinstance(quote, dict) else str(quote)
    context = quote.get('context', '') if isinstance(quote, dict) else ''
    author_line = f'— 你 · {context}' if context else '— 你说过的话'
    return f'''
  <div class="golden-quote">
    <p class="golden-quote-text">"{text}"</p>
    <div class="golden-quote-author">{author_line}</div>
  </div>
'''


def build_future_letter_html(letter):
    """给未来的信"""
    if not isinstance(letter, dict):
        return ''
    date = letter.get('date', '')
    greeting = letter.get('greeting', '亲爱的未来的你：')
    body = letter.get('body', '')
    sign = letter.get('sign', '—— 那个下午的你')
    return f'''
  <div class="letter-wrap">
    <div class="letter-date">{date}</div>
    <div class="letter-greeting">{greeting}</div>
    <div class="letter-body">{body}</div>
    <div class="letter-sign">{sign}</div>
  </div>
'''


def build_closing_html(closing):
    """07 失败免疫"""
    html = ''
    if closing.get('narrative'):
        html += f"{closing['narrative']}\n"
    quote = closing.get('quote') or closing.get('philosophy_quote')
    if quote:
        text = quote.get('text', '') if isinstance(quote, dict) else str(quote)
        author = quote.get('author', '') if isinstance(quote, dict) else ''
        author_line = f'—— {author}' if author else '—— 无限游戏 · Simon Sinek'
        html += (
            '</div>\n    <div class="closing-quote">\n'
            '      <div class="closing-quote-line"></div>\n'
            f'      <p class="closing-quote-text">{text}</p>\n'
            f'      <div class="closing-quote-author">{author_line}</div>\n'
            '    </div>\n    <div class="section-body">\n'
        )
    return html


def _pick_epigraph_for(section_key, data):
    """从 data['epigraphs'] 或用户原话池里挑一句作为章节题记"""
    epis = (data.get('epigraphs') or {})
    e = epis.get(section_key)
    if isinstance(e, dict) and e.get('text'):
        return e
    if isinstance(e, str) and e.strip():
        return {"text": e.strip(), "phase": section_key.upper()}
    return None


def _build_masthead(data, capsule_hint=None):
    """MASTHEAD：编号 + 日期"""
    date = data.get('date') or datetime.now().strftime('%Y.%m')
    short_date = date
    try:
        d = datetime.strptime(data.get('date', ''), '%Y年%m月%d日')
        short_date = d.strftime('%Y.%m')
    except Exception:
        try:
            d = datetime.strptime(data.get('date', ''), '%Y-%m-%d')
            short_date = d.strftime('%Y.%m')
        except Exception:
            pass
    volume = data.get('volume') or 'Nº 001'
    return f'''
  <header class="masthead">
    <div class="masthead-left">人生设计蓝图<br>Life Design Blueprint</div>
    <div class="masthead-right">{volume}<br>{short_date}</div>
  </header>
'''


def _build_hero(data):
    """HERO：固定标题，隐喻只在金句卡里出现"""
    user_name = data.get('user_name', '')
    hero_title = data.get('hero_title') or '在不确定中<br>设计属于自己的人生'
    hero_subtitle = data.get('hero_subtitle') or '基于斯坦福 Life Design Lab 方法论，与你共同完成的一份人生设计蓝图。'
    date = data.get('date', datetime.now().strftime('%Y 年 %m 月 %d 日'))
    return f'''
  <section class="hero">
    <div class="hero-label">Personal Odyssey Report</div>
    <h1 class="hero-title">{hero_title}</h1>
    <p class="hero-subtitle">{hero_subtitle}</p>
    <div class="hero-meta">Generated for {user_name} · {date}</div>
  </section>

  <div class="divider"></div>
'''


def _build_appointment(data):
    """结尾"时间胶囊"说明 — 明确告诉用户封存了什么、什么时候收到"""
    cap = data.get('capsule') or {}
    d30 = cap.get('trigger_at_d30') or ''
    if not d30 and cap:
        d30 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    if not d30:
        return ''
    date_display = d30
    try:
        d = datetime.strptime(d30, '%Y-%m-%d')
        weekday_cn = '一二三四五六日'[d.weekday()]
        date_display = d.strftime('%Y 年 %m 月 %d 日') + f' · 星期{weekday_cn}'
    except Exception:
        pass
    return f'''
  <div class="divider-dot"></div>

  <section class="appointment">
    <p class="appointment-desc">
      你刚刚在对话的最后，选择封存了一封写给未来自己的信。<br>
      这封信里记录了你此刻的真实想法、你的犹豫、你的期待。
    </p>
    <div class="appointment-date">{date_display}</div>
    <p class="appointment-hint">
      30 天后，这封信会自动送达。<br>
      到时候你会收到提醒——打开它，看看一个月前的自己。
    </p>
  </section>
'''


def _build_md_actions():
    """底部：复制 md / 下载 md 两个按钮"""
    return '''
  <div class="md-actions">
    <button class="md-btn" onclick="__copyMd(this)">复制为 Markdown</button>
    <button class="md-btn" onclick="__downloadMd()">下载 .md</button>
  </div>
'''


MD_EMBED_SCRIPT = r'''
<script>
function __getMd() {
  var el = document.getElementById('blueprint-md');
  return el ? el.textContent.replace(/^\s+/, '') : '';
}
function __copyMd(btn) {
  var md = __getMd();
  if (!md) { btn.textContent = '(无 Markdown 内容)'; return; }
  navigator.clipboard.writeText(md).then(function() {
    var orig = btn.textContent;
    btn.textContent = '✓ 已复制';
    btn.classList.add('copied');
    setTimeout(function(){ btn.textContent = orig; btn.classList.remove('copied'); }, 2000);
  }).catch(function() {
    btn.textContent = '复制失败';
    setTimeout(function(){ btn.textContent = '复制为 Markdown'; }, 2000);
  });
}
function __downloadMd() {
  var md = __getMd();
  if (!md) return;
  var name = document.title.replace(/\s*·.*$/, '').replace(/[\/\\:*?"<>|]/g, '_') + '.md';
  var blob = new Blob([md], {type: 'text/markdown;charset=utf-8'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList && e.target.classList.contains('timeline-check')) {
    e.target.classList.toggle('checked');
  }
});
function toggleOdyssey(card) {
  var plan = card.getAttribute('data-plan');
  var panel = document.getElementById('odyssey-panel');
  var inner = document.getElementById('odyssey-panel-inner');
  var isActive = card.classList.contains('active');

  // 清除所有卡片的 active 状态
  var cards = document.querySelectorAll('.odyssey-card');
  for (var i = 0; i < cards.length; i++) { cards[i].classList.remove('active'); }

  if (isActive) {
    // 点击已激活的卡片 → 关闭
    panel.classList.remove('active');
    panel.style.borderTopColor = '';
    return;
  }

  // 激活当前卡片
  card.classList.add('active');
  var data = (typeof __odysseyPlans !== 'undefined') ? __odysseyPlans[plan] : null;
  if (!data) return;

  // 设置面板边框颜色
  panel.style.borderTopColor = data.color;

  // 构建面板内容
  var html = '';
  // 左栏：标题 + 描述 + 时间线
  html += '<div class="odyssey-timeline-col">';
  if (data.title) {
    html += '<h3 style="font-family:var(--serif);font-size:1.1rem;margin:0 0 12px;color:var(--plan-color,' + data.color + ')">' + data.title + '</h3>';
  }
  if (data.body) {
    html += '<div style="font-size:0.88rem;line-height:1.8;color:var(--stone);margin-bottom:16px">' + data.body + '</div>';
  }
  if (data.timeline) {
    html += '<div class="odyssey-detail-label">时间线 · TIMELINE</div>';
    html += '<div class="odyssey-timeline">' + data.timeline + '</div>';
  }
  html += '</div>';
  // 右栏：想问自己
  html += '<div class="odyssey-questions-col">';
  html += '<div class="odyssey-detail-label">想问自己 · QUESTIONS</div>';
  if (data.questions && data.questions.length) {
    html += '<ul class="odyssey-detail-questions" style="--plan-color:' + data.color + '">';
    for (var j = 0; j < data.questions.length; j++) {
      var q = data.questions[j] || '';
      // 转义 HTML 特殊字符
      q = q.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      html += '<li>' + q + '</li>';
    }
    html += '</ul>';
  }
  html += '</div>';
  inner.innerHTML = html;

  // 展开面板
  panel.classList.add('active');

  // 平滑滚动到面板
  setTimeout(function() {
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 100);
}
</script>
'''


def generate_report(data, embedded_md=""):
    """
    从富文本 JSON 生成完整 HTML 报告（style-c 禅意基调 · P1 三层加密）。
    embedded_md：可选的 Markdown 全文，会内嵌到 <script type="text/markdown"> 里。
    """
    date = data.get('date', datetime.now().strftime('%Y年%m月%d日'))
    user_name = data.get('user_name', '朋友')

    parts = []
    parts.append(_build_masthead(data))
    parts.append(_build_hero(data))

    if data.get('dashboard'):
        parts.append(build_section(1, '你在这里',
            build_dashboard_html(data['dashboard']),
            epigraph=_pick_epigraph_for('dashboard', data)))

    if data.get('golden_quote'):
        parts.append(build_quote_card_html(data['golden_quote']))

    parts.append('<div class="divider"></div>')

    if data.get('reframe'):
        parts.append(build_section(2, '真问题',
            build_reframe_html(data['reframe']),
            epigraph=_pick_epigraph_for('reframe', data)))

    parts.append('<div class="divider-dot"></div>')

    if data.get('compass'):
        parts.append(build_section(3, '你的指南针',
            build_compass_html(data['compass']),
            epigraph=_pick_epigraph_for('compass', data)))

    parts.append('<div class="divider"></div>')

    if data.get('energy'):
        parts.append(build_section(4, '你的能量地图',
            build_energy_html(data['energy']),
            epigraph=_pick_epigraph_for('energy', data)))

    parts.append('<div class="divider-dot"></div>')

    if data.get('odyssey'):
        parts.append(build_section(5, '三个奥德赛计划',
            build_odyssey_html(data['odyssey']),
            epigraph=_pick_epigraph_for('odyssey', data)))

    parts.append('<div class="divider"></div>')

    if data.get('actions'):
        parts.append(build_section(6, '接下来 30 天',
            build_actions_html(data['actions']),
            epigraph=_pick_epigraph_for('actions', data)))

    if data.get('future_letter'):
        parts.append(build_future_letter_html(data['future_letter']))

    parts.append('<div class="divider"></div>')

    if data.get('closing'):
        parts.append(build_section(7, '失败免疫',
            build_closing_html(data['closing']),
            epigraph=_pick_epigraph_for('closing', data)))

    parts.append(_build_appointment(data))
    parts.append(_build_md_actions())

    sections_html = '\n'.join(parts)

    css = build_css()

    md_block = ""
    if embedded_md:
        safe_md = embedded_md.replace('</script>', '<\\/script>')
        md_block = f'<script type="text/markdown" id="blueprint-md">\n{safe_md}\n</script>\n'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>个人人生设计蓝图 · {user_name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Noto+Serif+SC:wght@400;600;700&family=IBM+Plex+Mono:wght@300;400&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="page">
{sections_html}

  <footer class="footer">
    <div class="footer-text">
      Life Design Blueprint · 基于斯坦福 Life Design Lab 方法论<br>
      Generated with care · {date}
    </div>
  </footer>

</div>
{md_block}{MD_EMBED_SCRIPT}
</body>
</html>
'''
    return html



# ============================================================
# 时间胶囊 & 定时回信调度
# ============================================================

def _make_capsule_id(user_name: str, sealed_at: str) -> str:
    """生成人类可读的短口令，例：LD-2607-7A9F"""
    yy = sealed_at[2:4]
    mm = sealed_at[5:7]
    raw = f"{user_name}|{sealed_at}|{os.urandom(4).hex()}"
    tail = hashlib.sha256(raw.encode('utf-8')).hexdigest()[:4].upper()
    return f"LD-{yy}{mm}-{tail}"


def seal_capsule(data: dict, output_dir: str) -> dict:
    """
    从对话数据里提取 5 个字段，封存为时间胶囊 JSON。
    30 天 / 90 天后由平台 scheduler 触发回信时读取。

    需要 AI 在 JSON 里额外提供 capsule 字段（见 schema 说明）；
    若缺失，尝试从 golden_quote / reframe 等已有字段兜底提取。
    """
    sealed_at = datetime.now().strftime('%Y-%m-%d')
    user_name = data.get('user_name', '朋友')

    # 优先读 AI 显式填的 capsule 字段
    src = data.get('capsule', {}) or {}

    # 兜底：从其他字段推断
    quote = src.get('quote') or (data.get('golden_quote') or {}).get('text', '')
    avoided_topic = src.get('avoided_topic', '')
    contradiction = src.get('contradiction') or (data.get('reframe') or {}).get('real', '')
    metaphor = src.get('user_signature_metaphor', '')

    # chosen_prototype 从 actions 里挑一个
    chosen = src.get('chosen_prototype', '')
    if not chosen:
        actions = data.get('actions', {}) or {}
        for key in ('talk', 'try', 'step', 'habit'):
            arr = actions.get(key) or []
            if arr:
                chosen = arr[0] if isinstance(arr[0], str) else (arr[0].get('what') or '')
                if chosen:
                    break

    capsule_id = src.get('capsule_id') or _make_capsule_id(user_name, sealed_at)
    d30 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    d90 = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')

    capsule = {
        "schema_version": 1,
        "capsule_id": capsule_id,
        "user_name": user_name,
        "sealed_at": sealed_at,
        "trigger_at_d30": d30,
        "trigger_at_d90": d90,
        "quote": quote,
        "avoided_topic": avoided_topic,
        "contradiction": contradiction,
        "chosen_prototype": chosen,
        "user_signature_metaphor": metaphor,
    }

    # 写盘：<output_dir>/capsules/<capsule_id>.json
    capsule_dir = os.path.join(output_dir, 'capsules')
    os.makedirs(capsule_dir, exist_ok=True)
    capsule_path = os.path.join(capsule_dir, f'{capsule_id}.json')
    with open(capsule_path, 'w', encoding='utf-8') as f:
        json.dump(capsule, f, ensure_ascii=False, indent=2)

    return {"capsule": capsule, "path": capsule_path}


def schedule_letters(capsule: dict, dry_run: bool = False) -> list:
    """
    调用平台 schedule-creator，为 30 天 / 90 天两次回信下调度。

    关键设计：capsule 全量字段以 JSON 字符串塞进 query 参数里，
    即便 30 天后 skill 目录被清空，也能从调度 payload 里恢复。

    返回一个列表，每项 {"phase": "d30", "cmd": [...], "ok": bool, "output": "..."}。
    dry_run=True 时只打印命令、不真的调用。
    """
    results = []
    payload_min = {
        "cid": capsule["capsule_id"],
        "u": capsule.get("user_name", ""),
        "q": capsule.get("quote", ""),
        "a": capsule.get("avoided_topic", ""),
        "c": capsule.get("contradiction", ""),
        "p": capsule.get("chosen_prototype", ""),
        "m": capsule.get("user_signature_metaphor", ""),
        "s": capsule.get("sealed_at", ""),
    }
    payload_str = json.dumps(payload_min, ensure_ascii=False, separators=(',', ':'))

    for phase, when_days, when_desc in [("d30", 30, "30 天后"), ("d90", 90, "90 天后")]:
        query = (
            f"[life-designer 时间胶囊回信] phase={phase} "
            f"capsule_id={capsule['capsule_id']} payload={payload_str}"
        )
        cmd = [
            "schedule-creator", "add",
            "--when", f"{when_days} days later",
            "--title", f"Life Designer · {when_desc}的一封信",
            "--query", query,
        ]
        if dry_run:
            results.append({"phase": phase, "cmd": cmd, "ok": True, "output": "(dry-run)"})
            continue
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            results.append({
                "phase": phase,
                "cmd": cmd,
                "ok": proc.returncode == 0,
                "output": (proc.stdout or '') + (proc.stderr or ''),
            })
        except FileNotFoundError:
            # 沙箱里没有 schedule-creator 可执行文件属正常，返回一个明确标记
            results.append({
                "phase": phase,
                "cmd": cmd,
                "ok": False,
                "output": "schedule-creator not found in PATH (由主 agent 代为下调度)",
            })
        except Exception as e:
            results.append({"phase": phase, "cmd": cmd, "ok": False, "output": str(e)})
    return results


def generate_demo_data():
    """生成示范数据，展示完整 JSON 结构"""
    return {
        "user_name": "朋友",
        "date": "2026年7月8日",
        "dashboard": {
            "narrative": "<p>你走进来的时候说了一句话：「我觉得工作还行但很迷茫」。这句话里藏着两个声音——一个在说「我能做」，另一个在说「但做了又怎样」。</p><p>下面四个维度的打分，帮我们把这个模糊的感觉变成了可以看清的画面。</p>",
            "scores": {
                "health": {"score": 6, "note": "身体还行，但最近睡眠不太好。你提到了好几次'累'，但没有说具体哪里累——这种模糊的疲惫感往往不是身体的，是心理的。"},
                "work": {"score": 5, "note": "你说工作'不差'。注意你用的词——不是'好'，是'不差'。'不差'是一个防御性的评价，说明你对工作没有负面情绪，但也找不到正面情绪。"},
                "play": {"score": 3, "note": "这个分数说明你的生活已经被'有用的事'填满了。纯粹为了快乐做的事，你想了很久才想出'上个月打游戏'。这不是时间问题，是你已经不允许自己'没用'了。"},
                "love": {"score": 7, "note": "这是你最高的分数。你有人可以打给，有连接感。这个维度是你的锚——不管工作怎么变，这个底座是稳的。"}
            },
            "analysis": "<p>把四个分数放在一起看，有一个很清晰的模式：你的 <strong>工作和娱乐严重失衡</strong>，而且失衡的方向很值得注意——你不是因为工作太忙没时间玩，而是 <em>你已经忘了怎么玩</em>。</p><p>你的爱（7分）和健康（6分）还在支撑着你。但工作和娱乐之间的落差，指向的不是「需要休息」，而是「需要找到让你活过来的事」。</p>"
        },
        "golden_quote": {
            "text": "我像个跑步机——跑得很快，但原地不动。",
            "context": "Phase 1 描述工作感受时"
        },
        "reframe": {
            "narrative": "<p>你说你迷茫。但聊了这么多之后，我觉得你其实不迷茫——你知道你能做什么，你缺的是「做这些跟我在乎的东西有什么关系」。</p><p>让我们把你最初以为的问题拆开看看：</p>",
            "perceived": "我不知道自己该做什么，没有方向。",
            "gravity": "你所在的行业确实有年龄焦虑和天花板——这是现实，不是你个人能解决的。接受它。",
            "real": "你不是不知道该做什么。你知道你能做什么。你缺的是——做这些事跟我真正在乎的东西有什么关系？",
            "wrong_premise": "「先想清楚再行动」——这个假设让你一直在想，一直在等，一直在原地转。",
            "conclusion": "<p>你不是在跑错方向。你是站在起跑线上，因为不确定终点在哪所以不敢跑。</p><p>但设计思维告诉你：<strong>不用知道终点。先跑起来，边跑边调整方向。</strong></p>"
        },
        "compass": {
            "narrative": "<p>我们聊了你的工作观和人生观。有意思的是，你描述了两套完全不同的引擎：</p>",
            "work_view": "工作是证明自己的方式。让家人觉得我有出息，给自己安全感。赚钱，稳定，往上走。——这是你现在的引擎，它让你跑得快。但你说了，跑到头也不想跑了。",
            "life_view": "做出一个东西，真的帮到别人。哪怕只是一小群人。——你提到这个的时候用了「挺值的」。这个词的重量跟前面描述工作时用的「不差」完全不同。",
            "diagnosis": "<p>你发现了吗？你白天在跑第一台引擎（证明自己），但晚上睡前想的是第二台（帮到别人）。</p><p>这两台引擎在你脑子里打架。你现在的痛苦不是来自「不知道该做什么」，而是来自 <strong>两个自己之间的一致性裂缝</strong>——你在过一个人的人生，心里想的是另一个人的。</p><p>你的指南针正北方向其实很清楚：<em>造东西，帮到人</em>。偏离的方向是：你目前在为「安全感」工作，而不是为「意义感」工作。</p>"
        },
        "energy": {
            "narrative": "<p>我让你回忆一个完全投入、忘了时间的时刻。你几乎立刻就想到了——上周末帮朋友做小程序的那个下午。</p>",
            "flow": [
                "帮朋友做产品原型——面对面协作，用 iPad 画图，最爽的是对方说「对对对就是这个」的瞬间",
                "深夜一个人写文章——不是工作汇报，是写自己的想法。写完会有一种「被自己说服了」的感觉",
                "给朋友讲一个复杂概念，看到对方眼睛亮了的那一刻"
            ],
            "recharge": [
                "和朋友吃一顿很长的饭，聊的不是工作",
                "散步时听播客，偶尔停下来记个笔记",
                "周末早上不赶时间地泡一杯咖啡，什么都不做"
            ],
            "drain_but_good": [
                "写周报和项目管理文档——做得好但每次做完都像被抽干",
                "开没有结论的会——时间花了但什么都没推进"
            ],
            "lean_toward": [
                "造东西（把模糊的想法变成具体的产品/内容）",
                "帮人看清问题（把复杂的事说简单，让对方有顿悟感）"
            ],
            "formula": "你在「面对面、有即时反馈」的环境下，做「把模糊变具体」的事情时，最容易活过来。你的能量来源不是管事情，是造东西和被需要。",
            "conclusion": "<p>一个重要的区分：<strong>你擅长做的事 ≠ 让你活过来的事。</strong></p><p>你很擅长项目管理——但你每次做完都觉得被掏空。你喜欢造产品——但你还没把它变成日常工作。这个gap不是小事，它是你接下来要设计的东西。</p>"
        },
        "odyssey": {
            "narrative": "<p>现在来做最好玩的一步——设计三个完全不同、但都是你真心愿意走的五年版本。记住，这三个不是好/中/差三档，三个都是 A 计划。</p>",
            "plans": [
                {
                    "title": "产品管理者",
                    "body": "留在现有公司，从项目管理转向产品方向。稳定收入 + 系统方法论积累。风险低，但成长曲线较缓。适合「先稳住再找方向」的阶段。",
                    "timeline": "<p><strong>第1年：</strong>在现有公司争取一个产品方向负责人的角色，开始从「管项目」转向「做产品」。</p><p><strong>第2-3年：</strong>积累产品方法论，带一个小团队做出一个有用户口碑的产品。</p><p><strong>第4-5年：</strong>成为某个垂直领域的产品负责人，开始思考自己的产品方向。</p>",
                    "questions": [
                        "在现有公司有没有可能从项目管理转向产品方向？需要什么条件？",
                        "你愿意用两年时间在一个安全的环境里积累产品能力吗？"
                    ],
                    "eval": {"resources": 80, "like": 50, "confidence": 70, "alignment": 45}
                },
                {
                    "title": "独立产品人",
                    "body": "用业余时间验证产品想法，逐步过渡到全职独立。核心是「用最小成本试错」。收入不稳定但自由度高。适合「脑子里已经有一个想法在烧」的状态。",
                    "timeline": "<p><strong>第1年：</strong>利用业余时间做第一个小产品。不辞职，用晚上和周末验证。做到有 100 个真实用户。</p><p><strong>第2年：</strong>如果产品有正反馈，开始认真考虑全职做。加入一个创业团队或者自己做。</p><p><strong>第3-5年：</strong>成为一个独立产品人。有自己的产品，有自己的用户，靠产品养活自己。</p>",
                    "questions": [
                        "你脑子里有没有一个具体产品想法，已经想了很久但一直没做？",
                        "如果明天就开始，你的第一个最小可行产品可以是什么？"
                    ],
                    "eval": {"resources": 40, "like": 85, "confidence": 45, "alignment": 90}
                },
                {
                    "title": "产品创作者 + 教育者",
                    "body": "写作 + 做产品双线并行。内容帮你建立影响力，产品帮你验证想法。前期投入大、回报慢，但一旦飞轮转起来，天花板最高。适合「愿意用三年换一个事业」的人。",
                    "timeline": "<p><strong>第1年：</strong>开始写产品相关的文章/播客。不辞职。目标是找到你的声音和受众。</p><p><strong>第2-3年：</strong>内容和产品双线并行。写东西帮你梳理思路，做产品帮你验证想法。</p><p><strong>第4-5年：</strong>成为产品领域的创作者——有自己的社群，教别人做产品，同时自己做产品。</p>",
                    "questions": [
                        "你有没有想过把你帮朋友做产品的那个下午，变成一种日常？",
                        "你的声音是什么？你想教别人什么？"
                    ],
                    "eval": {"resources": 30, "like": 90, "confidence": 35, "alignment": 95}
                }
            ],
            "execution": {
                "anti_vision": "每天在会议室里度过 8 小时，下班后什么都不想动。35 岁回头看，发现自己只是换了一个更大的格子间。",
                "vision": "做出一个小产品，有人真的在用。每天起来有动力打开电脑。周末不是在赶 deadline，是在想「下一步怎么让它更好」。",
                "quarter_q": "我脑子里的那个产品想法，真的有人需要吗？",
                "month_proto": "用 4 个周末做出一个最简版本。找 10 个目标用户试用。记录他们的真实反应。",
                "daily": "每天花 15 分钟写下产品想法的三句话。不用多，三句话就好。",
                "bottom_line": "三个月后如果完全没有正反馈（没人用、没人讨论、你自己也不想打开），重新评估方向。但注意——重新评估方向 ≠ 放弃做产品这件事。"
            },
            "conclusion": "<p>我注意到一个有意思的事——你的版本二和版本三有一个共同的内核：<strong>造东西 + 帮别人</strong>。这不是巧合。你的指南针其实指向了同一个方向，只是你自己还没允许自己认真去想。</p><p>这不是三个选择之间的竞争。这是你人生主题在不同规模下的投影。不管你先走哪条路，最终你都在走向同一个方向。</p>"
        },
        "actions": {
            "narrative": "<p>从「不知道自己在干嘛」到「明天就能做的一件事」——你已经有方向了。下面是你的原型行动清单：</p>",
            "talk": "找 2-3 个「已经在做独立产品的人」聊聊。不是去求职，是去听他们的故事。问他们：「你第一个产品是怎么开始的？」「最大的坑是什么？」「什么时候觉得'这条路是对的'？」",
            "try": "用 4 个周末做你脑子里那个产品的最小版本。不追求完美——丑没关系，能用就行。找 10 个人试用，记录他们的第一反应。",
            "step": "今晚，花 15 分钟写下三句话：你想做的产品是什么？帮谁解决什么问题？为什么是你来做？三句话就够了。",
            "habit": "手机设 3 个随机提醒（每天不同时间），提醒内容：「此刻我在做什么？它是在让我走向我想要的生活，还是让我留在原地？」不用回答，注意到就好。"
        },
        "future_letter": {
            "date": "2027年1月8日",
            "body": "<p>亲爱的半年后的我：</p><p>写这封信的时候，是一个周三的晚上。你刚跟一个 AI 聊了快一个小时。你说你像跑步机——跑得很快但原地不动。那天晚上你做了一个决定：今晚写三句话。</p><p>我不知道你写了没有。我也不知道你做了那个产品没有。但我知道一件事：你愿意认真想这个问题，本身就说明你还在乎。</p><p>如果你已经开始做了——不管做得好不好——你已经比半年前的自己勇敢了太多。</p><p>如果你还没开始——也没关系。人生不是考试，没有过期。</p><p>但请你现在做一件事：回想一下那天晚上聊天时，你说到帮朋友做产品那个下午时你的语气。那个语气里的你，才是你。</p><p>去找他。</p>"
        },
        "closing": {
            "narrative": "<p>你有三个版本可以试。你不需要选最好的那个——你只需要选一个先走。</p><p>走不通就换一个。这不是考试，没有不及格。</p><p>你今天做的最重要的事不是得到了三个计划。而是——你终于允许自己去想「我还可以活成另一种样子」。</p><p>那个可能性一直都在。你只是今天第一次认真地看了它一眼。</p><p>去写那三句话吧。今晚就好。</p>",
            "philosophy_quote": {
                "text": "「人生不是我们发现了什么，而是我们创造了什么。你不是在寻找一条已有的路——你在开辟一条只属于你的路。」",
                "author": "— Bill Burnett & Dave Evans, Designing Your Life"
            }
        },
        "capsule_confirmed": True,
        "capsule": {
            "quote": "我像个跑步机——跑得很快但原地不动",
            "avoided_topic": "跟妈妈的关系",
            "contradiction": "嘴上要稳定，兴奋的全是冒险",
            "chosen_prototype": "用4个周末做脑子里那个产品的最小版本",
            "user_signature_metaphor": "跑步机"
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='人生设计蓝图报告生成器 v2 — 富文本 JSON → 精美 HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  python3 scripts/report_generator.py --input conversation.json
  python3 scripts/report_generator.py --input conversation.json --output blueprint.html
  python3 scripts/report_generator.py --demo                     # 生成示范报告

JSON 结构（富文本区块，不再是原子占位符）：
  {
    "user_name": "小明",
    "date": "2026年7月8日",
    "dashboard": {
      "narrative": "<p>你走进来的时候说了一句话...</p>",
      "scores": {
        "health": {"score": 7, "note": "身体还行但睡眠不好..."},
        ...
      },
      "analysis": "<p>把四个分数放在一起看...</p>"
    },
    "golden_quote": {
      "text": "我像个跑步机——跑得很快但原地不动",
      "context": "Phase 1 描述工作感受时"
    },
    "reframe": {
      "narrative": "<p>让我们把你最初以为的问题拆开看看...</p>",
      "perceived": "我不知道自己该做什么",
      "gravity": "行业年龄焦虑是现实...",
      "real": "你缺的是意义感...",
      "wrong_premise": "「先想清楚再行动」",
      "conclusion": "<p>你不是在跑错方向...</p>"
    },
    ...
  }
        '''
    )
    parser.add_argument('--input', '-i', help='对话数据 JSON 文件路径')
    parser.add_argument('--output', '-o', help='输出 HTML 文件路径（默认自动生成）')
    parser.add_argument('--demo', '-d', action='store_true', help='使用示范数据生成示例报告')
    parser.add_argument('--quiet', '-q', action='store_true', help='安静模式')
    parser.add_argument('--no-capsule', action='store_true',
                        help='不封存时间胶囊、不下 30/90 天调度（默认封存 + 下调度）')
    parser.add_argument('--dry-run-schedule', action='store_true',
                        help='胶囊照常封存，但只打印 schedule-creator 命令、不真的调用')

    args = parser.parse_args()

    if args.demo:
        data = generate_demo_data()
        if not args.output:
            args.output = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'demo-report.html')
    elif args.input:
        if not os.path.exists(args.input):
            print(f'错误：找不到输入文件 {args.input}', file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f'错误：JSON 解析失败 — {e}', file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)

    # 先生成 Markdown（双载体：本地文件 + 内嵌 HTML）
    try:
        from markdown_generator import generate_markdown
        md_text = generate_markdown(data)
    except Exception as e:
        print(f'⚠️ Markdown 生成失败（HTML 会照常继续）：{e}', file=sys.stderr)
        md_text = ''

    # 生成 HTML（把 md 内嵌进去，供页面上"复制/下载"用）
    report_html = generate_report(data, embedded_md=md_text)

    # 确定输出路径
    if not args.output:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        user_name = data.get('user_name', '用户')
        date_str = datetime.now().strftime('%Y%m%d')
        args.output = os.path.join(output_dir, f'人生设计蓝图_{user_name}_{date_str}.html')

    # 写入 HTML
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report_html)

    # 同时落一份 .md 到 HTML 所在目录（供本地阅读 / 版本控制）
    md_path = ''
    if md_text:
        md_path = os.path.splitext(args.output)[0] + '.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_text)

    if args.quiet:
        print(args.output)
    else:
        print(f'✅ 报告已生成：{args.output}')
        print(f'   文件大小：{os.path.getsize(args.output):,} 字节')
        if md_path:
            md_chars = len(md_text.replace('\n', '').replace(' ', ''))
            print(f'📝 Markdown 已生成：{md_path}（{md_chars} 字，同时已内嵌到 HTML）')
        section_count = sum(1 for k in ['dashboard','reframe','compass','energy','odyssey','actions','closing'] if k in data)
        print(f'   章节数：{section_count}/7')
        if data.get('golden_quote'):
            print(f'   金句卡：✅')
        if data.get('future_letter'):
            print(f'   给未来的信：✅')

    # ============================================================
    # 时间胶囊：封存 + 下 30/90 天两次回信调度
    # 只有用户在对话结束时确认了（capsule_confirmed: true）才封存
    # ============================================================
    capsule_confirmed = data.get('capsule_confirmed', False)
    if not args.no_capsule and not args.demo and capsule_confirmed:
        output_dir = os.path.dirname(os.path.abspath(args.output))
        sealed = seal_capsule(data, output_dir)
        capsule = sealed["capsule"]
        if not args.quiet:
            print(f'📮 时间胶囊已封存：{sealed["path"]}')
            print(f'   capsule_id：{capsule["capsule_id"]}')
            print(f'   30 天触发：{capsule["trigger_at_d30"]}')
            print(f'   90 天触发：{capsule["trigger_at_d90"]}')

        results = schedule_letters(capsule, dry_run=args.dry_run_schedule)
        for r in results:
            mark = '✅' if r['ok'] else '⚠️'
            if not args.quiet:
                print(f'{mark} 调度 {r["phase"]}：{r["output"].strip()[:120]}')

        # 关键兜底：如果 schedule-creator CLI 不在本机 PATH，
        # 说明当前是在 skill 内直接跑脚本、平台调度需要主 agent 代下。
        # 把待下调度的完整 query 写到 sidecar 文件，让上层 agent 读取后调用。
        if any(not r['ok'] for r in results):
            sidecar = os.path.join(output_dir, 'capsules',
                                   f'{capsule["capsule_id"]}.pending_schedules.json')
            with open(sidecar, 'w', encoding='utf-8') as f:
                json.dump({
                    "capsule_id": capsule["capsule_id"],
                    "note": "schedule-creator 未在脚本环境中可用，请由主 agent 读取本文件并调用 schedule-creator skill 下调度。",
                    "schedules": [
                        {"phase": r["phase"], "cmd": r["cmd"]} for r in results if not r['ok']
                    ],
                }, f, ensure_ascii=False, indent=2)
            if not args.quiet:
                print(f'📎 已写出 pending_schedules 兜底文件：{sidecar}')
    elif not args.quiet and not args.demo and not capsule_confirmed:
        print('⏭️  时间胶囊未封存（用户未确认，跳过）')


if __name__ == '__main__':
    main()

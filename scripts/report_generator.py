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
from datetime import datetime

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

PLAN_COLORS = {
    'A': COLORS['accent'],
    'B': COLORS['green'],
    'C': COLORS['blue'],
}

PLAN_LABELS = {
    'A': 'VERSION A — 延续当下',
    'B': 'VERSION B — 另一条路',
    'C': 'VERSION C — 无限可能',
}

DIM_META = {
    'health': {'label': '健康', 'color': COLORS['green'], 'hint': '身体·情绪·心理'},
    'work':   {'label': '工作', 'color': COLORS['accent'], 'hint': '认同感·意义感'},
    'play':   {'label': '娱乐', 'color': COLORS['blue'], 'hint': '纯粹的快乐'},
    'love':   {'label': '爱',   'color': COLORS['warm'], 'hint': '双向的连接'},
}

# ============================================================
# HTML 构建器
# ============================================================

def build_css():
    """构建完整的 CSS 样式表"""
    return '''
:root {
  --bg: #FAFAF8;
  --bg-alt: #F5F0EB;
  --bg-panel: #FFFFFF;
  --bg-code: #F0EDE8;
  --bg-hover: #EFEBE5;
  --ink: #1A1A18;
  --ink-80: #2A2A28;
  --ink-60: #555249;
  --ink-40: #8B867E;
  --ink-20: #B0ACA4;
  --ink-10: #CBC7C0;
  --ink-05: #E0DCD6;
  --accent: #C86A4A;
  --accent-deep: #A85238;
  --accent-glow: rgba(200, 106, 74, 0.12);
  --accent-soft: rgba(200, 106, 74, 0.06);
  --accent-border: rgba(200, 106, 74, 0.22);
  --green: #5A8A62;
  --green-soft: rgba(90, 138, 98, 0.06);
  --green-border: rgba(90, 138, 98, 0.22);
  --warm: #7D6B52;
  --warm-soft: rgba(125, 107, 82, 0.06);
  --warm-border: rgba(125, 107, 82, 0.22);
  --blue: #4A7A9C;
  --blue-soft: rgba(74, 122, 156, 0.06);
  --blue-border: rgba(74, 122, 156, 0.22);
  --hairline: rgba(0, 0, 0, 0.08);
  --hairline-strong: rgba(0, 0, 0, 0.12);
  --serif: "Noto Serif SC", "Source Serif 4", Georgia, serif;
  --sans: "Inter", -apple-system, "PingFang SC", system-ui, sans-serif;
  --ease: cubic-bezier(.2,.8,.2,1);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--sans);
  background: var(--bg);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
  line-height: 1.6;
}

::selection {
  background: var(--accent-glow);
  color: var(--accent-deep);
}

.container {
  max-width: 780px;
  margin: 0 auto;
  padding: 60px 40px 80px;
}

/* ===== Header ===== */
.report-header {
  margin-bottom: 48px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--hairline);
}

.report-header .label {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 2px;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 12px;
}

.report-header h1 {
  font-family: var(--serif);
  font-size: 32px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.02em;
  line-height: 1.3;
  margin-bottom: 8px;
}

.report-header .subtitle {
  font-size: 14px;
  color: var(--ink-40);
  font-weight: 300;
}

.report-header .meta {
  margin-top: 16px;
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: var(--ink-40);
}

.accent-line {
  width: 32px;
  height: 1.5px;
  background: var(--accent);
  margin-top: 16px;
  opacity: 0.7;
}

/* ===== Section ===== */
.section {
  margin-bottom: 56px;
}

.section-number {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 1.5px;
  color: var(--accent);
  margin-bottom: 8px;
}

.section h2 {
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 24px;
  letter-spacing: -0.01em;
  padding-left: 16px;
  position: relative;
  line-height: 1.3;
}

.section h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 3px;
  bottom: 3px;
  width: 3px;
  background: linear-gradient(180deg, var(--accent) 0%, var(--accent-deep) 100%);
  border-radius: 2px;
}

.section h3 {
  font-family: var(--serif);
  font-size: 16px;
  font-weight: 600;
  color: var(--ink-80);
  margin-top: 32px;
  margin-bottom: 14px;
}

.section p {
  font-size: 14px;
  line-height: 1.9;
  color: var(--ink-60);
  margin-bottom: 16px;
}

.section strong { color: var(--ink); font-weight: 600; }
.section em { color: var(--accent-deep); font-style: italic; }

/* ===== Dashboard ===== */
.dashboard {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 28px 0;
}

.dashboard-item {
  background: var(--bg-panel);
  border: 1px solid var(--hairline);
  border-radius: 3px;
  padding: 18px 22px;
  transition: all 0.25s var(--ease);
}

.dashboard-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transform: translateY(-1px);
}

.dim-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: var(--ink-40);
  margin-bottom: 4px;
}

.dim-hint {
  font-size: 10px;
  color: var(--ink-20);
  margin-bottom: 8px;
}

.dim-score {
  font-family: var(--serif);
  font-size: 30px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 4px;
}

.dim-score span {
  font-size: 14px;
  color: var(--ink-20);
  font-weight: 400;
}

.dim-bar {
  height: 3px;
  background: var(--ink-05);
  border-radius: 2px;
  margin-top: 10px;
  overflow: hidden;
}

.dim-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s var(--ease);
}

.dim-note {
  font-size: 12px;
  color: var(--ink-40);
  margin-top: 10px;
  line-height: 1.7;
}

/* ===== Rich Content ===== */
.narrative {
  font-size: 14px;
  line-height: 1.95;
  color: var(--ink-60);
  margin: 20px 0;
}

.narrative p {
  margin-bottom: 16px;
}

.narrative p:last-child {
  margin-bottom: 0;
}

blockquote {
  border-left: 2.5px solid var(--accent);
  padding: 16px 22px;
  margin: 24px 0;
  color: var(--ink-60);
  font-size: 13.5px;
  line-height: 1.85;
  font-style: italic;
  background: var(--accent-soft);
  border-radius: 0 3px 3px 0;
}

blockquote p { margin-bottom: 8px; color: var(--ink-60); }
blockquote p:last-child { margin-bottom: 0; }

/* ===== Quote Card（对话金句卡） ===== */
.quote-card {
  background: linear-gradient(135deg, #FAF5F0 0%, #F5EDE5 100%);
  border: 1px solid var(--accent-border);
  border-radius: 6px;
  padding: 32px 36px;
  margin: 32px 0;
  position: relative;
  text-align: center;
}

.quote-card::before {
  content: '\\201C';
  font-family: var(--serif);
  font-size: 72px;
  color: var(--accent);
  opacity: 0.15;
  position: absolute;
  top: 8px;
  left: 24px;
  line-height: 1;
}

.quote-card .quote-text {
  font-family: var(--serif);
  font-size: 18px;
  font-weight: 500;
  color: var(--ink);
  line-height: 1.7;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.quote-card .quote-context {
  font-size: 12px;
  color: var(--ink-40);
  font-style: italic;
}

.quote-card .quote-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1.5px;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 16px;
}

/* ===== Reframe Card ===== */
.reframe-card {
  background: var(--bg-panel);
  border: 1px solid var(--hairline);
  border-left: 3px solid var(--accent);
  border-radius: 3px;
  padding: 22px 26px;
  margin: 24px 0;
}

.reframe-row {
  display: flex;
  gap: 14px;
  margin-bottom: 14px;
  align-items: flex-start;
}

.reframe-row:last-child { margin-bottom: 0; }

.reframe-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--ink-40);
  min-width: 80px;
  padding-top: 2px;
  flex-shrink: 0;
}

.reframe-value {
  font-size: 13.5px;
  color: var(--ink-60);
  line-height: 1.75;
}

.reframe-value.highlight {
  color: var(--accent-deep);
  font-weight: 500;
}

/* ===== Compass ===== */
.compass {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 28px 0;
}

.compass-item {
  background: var(--bg-panel);
  border: 1px solid var(--hairline);
  border-radius: 3px;
  padding: 22px;
  transition: all 0.25s var(--ease);
}

.compass-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.compass-item:nth-child(1) { border-top: 2.5px solid var(--accent); }
.compass-item:nth-child(2) { border-top: 2.5px solid var(--green); }

.compass-title {
  font-family: var(--serif);
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--hairline);
}

.compass-text {
  font-size: 13px;
  color: var(--ink-60);
  line-height: 1.85;
}

/* ===== Radar Chart (SVG) ===== */
.radar-container {
  display: flex;
  justify-content: center;
  margin: 32px 0;
}

.radar-container svg {
  max-width: 340px;
  width: 100%;
}

/* ===== Energy Map ===== */
.energy-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 28px 0;
}

.energy-card {
  background: var(--bg-panel);
  border: 1px solid var(--hairline);
  border-radius: 3px;
  padding: 18px 22px;
  transition: all 0.25s var(--ease);
}

.energy-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.04); }

.energy-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--hairline);
}

.energy-card:nth-child(1) .energy-label { color: var(--green); }
.energy-card:nth-child(2) .energy-label { color: var(--accent); }
.energy-card:nth-child(3) .energy-label { color: var(--blue); }
.energy-card:nth-child(4) .energy-label { color: var(--warm); }

.energy-item {
  font-size: 13px;
  color: var(--ink-60);
  line-height: 1.75;
  padding: 4px 0 4px 16px;
  position: relative;
}

.energy-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 13px;
  width: 6px;
  height: 1.5px;
  background: var(--ink-20);
}

/* ===== Odyssey Plans ===== */
.odyssey-plans {
  display: flex;
  flex-direction: column;
  gap: 22px;
  margin: 28px 0;
}

.odyssey-card {
  background: var(--bg-panel);
  border: 1px solid var(--hairline);
  border-radius: 3px;
  padding: 26px;
  transition: all 0.25s var(--ease);
  position: relative;
}

.odyssey-card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  transform: translateY(-1px);
}

.odyssey-card.plan-a { border-left: 3px solid var(--accent); }
.odyssey-card.plan-b { border-left: 3px solid var(--green); }
.odyssey-card.plan-c { border-left: 3px solid var(--blue); }

.odyssey-tag {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.plan-a .odyssey-tag { color: var(--accent); }
.plan-b .odyssey-tag { color: var(--green); }
.plan-c .odyssey-tag { color: var(--blue); }

.odyssey-title {
  font-family: var(--serif);
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 16px;
}

.odyssey-timeline {
  font-size: 13.5px;
  color: var(--ink-60);
  line-height: 1.9;
  margin-bottom: 18px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--hairline);
}

.odyssey-questions {
  margin-bottom: 18px;
}

.q-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--ink-40);
  letter-spacing: 0.3px;
  margin-bottom: 8px;
}

.q-item {
  font-size: 13px;
  color: var(--ink-60);
  line-height: 1.75;
  padding: 3px 0 3px 16px;
  position: relative;
}

.q-item::before {
  content: '?';
  position: absolute;
  left: 0;
  color: var(--ink-20);
  font-weight: 600;
  font-size: 12px;
}

/* ===== Eval Bars ===== */
.eval-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 18px;
}

.eval-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.eval-name {
  font-size: 11px;
  color: var(--ink-40);
  min-width: 44px;
}

.eval-bar {
  flex: 1;
  height: 4px;
  background: var(--ink-05);
  border-radius: 2px;
  overflow: hidden;
}

.eval-bar-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--accent);
}

.eval-value {
  font-size: 11px;
  color: var(--ink-60);
  font-weight: 500;
  min-width: 24px;
  text-align: right;
}

/* ===== Execution Table ===== */
.exec-table {
  width: 100%;
  border-collapse: collapse;
  margin: 24px 0;
  font-size: 13px;
}

.exec-table th {
  background: var(--bg-code);
  color: var(--ink);
  font-weight: 600;
  text-align: left;
  padding: 11px 16px;
  border-bottom: 1.5px solid var(--accent-border);
  font-size: 12px;
  letter-spacing: 0.3px;
}

.exec-table td {
  padding: 11px 16px;
  border-bottom: 1px solid var(--hairline);
  color: var(--ink-60);
  vertical-align: top;
  line-height: 1.7;
}

.exec-table td:first-child {
  font-weight: 500;
  color: var(--ink-80);
  white-space: nowrap;
  width: 120px;
}

.exec-table tbody tr:hover { background: var(--bg-hover); }
.exec-table tbody tr:hover td { color: var(--ink); }

/* ===== Action List ===== */
.action-list { margin: 24px 0; }

.action-item {
  display: flex;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--hairline);
  align-items: flex-start;
}

.action-item:last-child { border-bottom: none; }

.action-icon {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 2px;
}

.action-icon.talk { background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent-border); }
.action-icon.try { background: var(--green-soft); color: var(--green); border: 1px solid var(--green-border); }
.action-icon.step { background: var(--blue-soft); color: var(--blue); border: 1px solid var(--blue-border); }
.action-icon.habit { background: var(--warm-soft); color: var(--warm); border: 1px solid var(--warm-border); }

.action-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 4px;
}

.action-desc {
  font-size: 12.5px;
  color: var(--ink-40);
  line-height: 1.75;
}

/* ===== Future Letter（给6个月后自己的一封信） ===== */
.future-letter {
  background: linear-gradient(180deg, #FAF8F5 0%, #F5F0EB 100%);
  border: 1px solid var(--hairline);
  border-radius: 6px;
  padding: 36px 40px;
  margin: 36px 0;
  position: relative;
}

.future-letter::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent) 0%, var(--green) 50%, var(--blue) 100%);
  border-radius: 6px 6px 0 0;
}

.future-letter .letter-date {
  font-size: 11px;
  color: var(--ink-40);
  letter-spacing: 0.5px;
  margin-bottom: 20px;
}

.future-letter .letter-body {
  font-family: var(--serif);
  font-size: 15px;
  line-height: 2;
  color: var(--ink-60);
}

.future-letter .letter-body p {
  margin-bottom: 16px;
  font-size: 15px;
  line-height: 2;
  color: var(--ink-60);
}

.future-letter .letter-sig {
  margin-top: 24px;
  font-size: 13px;
  color: var(--ink-40);
  font-style: italic;
  text-align: right;
}

/* ===== Closing ===== */
.closing {
  background: var(--bg-alt);
  border-radius: 3px;
  padding: 32px 36px;
  margin: 36px 0;
  border: 1px solid var(--hairline);
}

.closing p {
  font-size: 14.5px;
  line-height: 2;
  color: var(--ink-60);
  margin-bottom: 12px;
}

.closing p:last-child { margin-bottom: 0; }

.closing .closing-sig {
  margin-top: 24px;
  font-size: 12px;
  color: var(--ink-40);
  font-style: italic;
}

/* ===== Philosophy Quote ===== */
.philosophy-quote {
  text-align: center;
  padding: 40px 32px;
  margin: 40px 0;
  position: relative;
}

.philosophy-quote .pq-text {
  font-family: var(--serif);
  font-size: 16px;
  color: var(--ink-60);
  line-height: 1.8;
  font-style: italic;
  margin-bottom: 12px;
}

.philosophy-quote .pq-author {
  font-size: 12px;
  color: var(--ink-40);
  letter-spacing: 0.5px;
}

.philosophy-quote .pq-line {
  width: 40px;
  height: 1px;
  background: var(--accent);
  margin: 16px auto 0;
  opacity: 0.5;
}

/* ===== Footer ===== */
.report-footer {
  margin-top: 56px;
  padding-top: 24px;
  border-top: 1px solid var(--hairline);
  font-size: 11px;
  color: var(--ink-20);
  text-align: center;
  letter-spacing: 0.5px;
}

/* ===== Responsive ===== */
@media (max-width: 640px) {
  .container { padding: 32px 20px 60px; }
  .report-header h1 { font-size: 26px; }
  .dashboard { grid-template-columns: 1fr; }
  .compass { grid-template-columns: 1fr; }
  .energy-grid { grid-template-columns: 1fr; }
  .eval-grid { grid-template-columns: 1fr; }
  .future-letter { padding: 28px 24px; }
  .quote-card { padding: 24px 20px; }
}

/* ===== Print ===== */
@media print {
  body { background: #fff; }
  .container { max-width: none; padding: 20px; }
  .odyssey-card:hover, .dashboard-item:hover, .energy-card:hover {
    transform: none;
    box-shadow: none;
  }
  .section { page-break-inside: avoid; }
}
'''


def build_radar_svg(scores):
    """
    构建 SVG 雷达图。
    scores: dict like {"health": 7, "work": 5, "play": 3, "love": 8}
    """
    dims = ['health', 'work', 'play', 'love']
    labels = ['健康', '工作', '娱乐', '爱']
    colors = [COLORS['green'], COLORS['accent'], COLORS['blue'], COLORS['warm']]

    cx, cy, r = 170, 160, 110
    import math

    def point_at(angle_deg, radius):
        rad = math.radians(angle_deg - 90)
        return (cx + radius * math.cos(rad), cy + radius * math.sin(rad))

    # Grid circles
    grid_lines = ''
    for pct in [0.25, 0.5, 0.75, 1.0]:
        gr = r * pct
        grid_lines += f'<circle cx="{cx}" cy="{cy}" r="{gr}" fill="none" stroke="#E0DCD6" stroke-width="0.5" />\n'

    # Axis lines
    axis_lines = ''
    for i in range(4):
        angle = i * 90
        px, py = point_at(angle, r)
        axis_lines += f'<line x1="{cx}" y1="{cy}" x2="{px:.1f}" y2="{py:.1f}" stroke="#E0DCD6" stroke-width="0.5" />\n'

    # Data polygon
    data_points = []
    for i, dim in enumerate(dims):
        score = min(max(scores.get(dim, 0), 0), 10)
        angle = i * 90
        pr = r * (score / 10)
        px, py = point_at(angle, pr)
        data_points.append(f'{px:.1f},{py:.1f}')

    data_polygon = ' '.join(data_points)

    # Data dots and labels
    dots = ''
    label_els = ''
    for i, dim in enumerate(dims):
        score = min(max(scores.get(dim, 0), 0), 10)
        angle = i * 90
        pr = r * (score / 10)
        px, py = point_at(angle, pr)
        dots += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{colors[i]}" stroke="white" stroke-width="1.5" />\n'

        # Label (outside the circle)
        lx, ly = point_at(angle, r + 24)
        score_text = f'{score}/10'
        label_els += f'<text x="{lx:.1f}" y="{ly - 6:.1f}" text-anchor="middle" font-family="Noto Serif SC, serif" font-size="13" font-weight="600" fill="{colors[i]}">{labels[i]}</text>\n'
        label_els += f'<text x="{lx:.1f}" y="{ly + 10:.1f}" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" fill="#8B867E">{score_text}</text>\n'

    svg = f'''<svg viewBox="0 0 340 320" xmlns="http://www.w3.org/2000/svg">
  {grid_lines}
  {axis_lines}
  <polygon points="{data_polygon}" fill="rgba(200,106,74,0.08)" stroke="{COLORS['accent']}" stroke-width="1.5" stroke-linejoin="round" />
  {dots}
  {label_els}
</svg>'''
    return svg


def build_section(num, title, content_html):
    """构建一个章节"""
    return f'''
  <section class="section">
    <div class="section-number">{num:02d}</div>
    <h2>{title}</h2>
    {content_html}
  </section>
'''


def build_dashboard_html(dashboard):
    """构建仪表盘 HTML"""
    html = ''

    if 'narrative' in dashboard:
        html += f'<div class="narrative">{dashboard["narrative"]}</div>\n'

    scores = dashboard.get('scores', {})
    html += '<div class="dashboard">\n'
    for dim in ['health', 'work', 'play', 'love']:
        meta = DIM_META[dim]
        s = scores.get(dim, {})
        score = s.get('score', '—')
        note = s.get('note', '')
        try:
            pct = int(float(score) * 10)
        except (ValueError, TypeError):
            pct = 0

        html += f'''    <div class="dashboard-item">
      <div class="dim-label">{meta['label']}</div>
      <div class="dim-hint">{meta['hint']}</div>
      <div class="dim-score">{score} <span>/ 10</span></div>
      <div class="dim-bar"><div class="dim-bar-fill" style="width: {pct}%; background: {meta['color']}"></div></div>
      <div class="dim-note">{note}</div>
    </div>
'''
    html += '  </div>\n'

    # Radar chart
    score_vals = {}
    for dim in ['health', 'work', 'play', 'love']:
        s = scores.get(dim, {})
        try:
            score_vals[dim] = float(s.get('score', 0))
        except (ValueError, TypeError):
            score_vals[dim] = 0

    html += f'  <div class="radar-container">\n    {build_radar_svg(score_vals)}\n  </div>\n'

    if 'analysis' in dashboard:
        html += f'<div class="narrative">{dashboard["analysis"]}</div>\n'

    return html


def build_reframe_html(reframe):
    """构建真问题 HTML"""
    html = ''
    if 'narrative' in reframe:
        html += f'<div class="narrative">{reframe["narrative"]}</div>\n'

    html += '  <div class="reframe-card">\n'
    rows = [
        ('你以为的', reframe.get('perceived', ''), False),
        ('重力问题', reframe.get('gravity', ''), False),
        ('真问题', reframe.get('real', ''), True),
        ('错误前提', reframe.get('wrong_premise', ''), False),
    ]
    for label, value, highlight in rows:
        cls = ' highlight' if highlight else ''
        html += f'    <div class="reframe-row">\n'
        html += f'      <div class="reframe-label">{label}</div>\n'
        html += f'      <div class="reframe-value{cls}">{value}</div>\n'
        html += f'    </div>\n'
    html += '  </div>\n'

    if 'conclusion' in reframe:
        html += f'<div class="narrative">{reframe["conclusion"]}</div>\n'

    return html


def build_compass_html(compass):
    """构建指南针 HTML"""
    html = ''
    if 'narrative' in compass:
        html += f'<div class="narrative">{compass["narrative"]}</div>\n'

    html += '  <div class="compass">\n'
    html += f'    <div class="compass-item">\n'
    html += f'      <div class="compass-title">工作观</div>\n'
    html += f'      <div class="compass-text">{compass.get("work_view", "")}</div>\n'
    html += f'    </div>\n'
    html += f'    <div class="compass-item">\n'
    html += f'      <div class="compass-title">人生观</div>\n'
    html += f'      <div class="compass-text">{compass.get("life_view", "")}</div>\n'
    html += f'    </div>\n'
    html += '  </div>\n'

    if 'diagnosis' in compass:
        html += f'<div class="narrative">{compass["diagnosis"]}</div>\n'

    return html


def build_energy_html(energy):
    """构建能量地图 HTML"""
    html = ''
    if 'narrative' in energy:
        html += f'<div class="narrative">{energy["narrative"]}</div>\n'

    cards = [
        ('心流时刻', energy.get('flow', [])),
        ('回血活动', energy.get('recharge', [])),
        ('擅长但耗能', energy.get('drain', [])),
        ('设计偏向', energy.get('direction', [])),
    ]

    html += '  <div class="energy-grid">\n'
    for label, items in cards:
        html += f'    <div class="energy-card">\n'
        html += f'      <div class="energy-label">{label}</div>\n'
        for item in items:
            html += f'      <div class="energy-item">{item}</div>\n'
        html += f'    </div>\n'
    html += '  </div>\n'

    if 'formula' in energy:
        html += f'  <blockquote><p>{energy["formula"]}</p></blockquote>\n'

    if 'conclusion' in energy:
        html += f'<div class="narrative">{energy["conclusion"]}</div>\n'

    return html


def build_odyssey_html(odyssey):
    """构建奥德赛计划 HTML"""
    html = ''
    if 'narrative' in odyssey:
        html += f'<div class="narrative">{odyssey["narrative"]}</div>\n'

    plans = odyssey.get('plans', [])
    if plans:
        html += '  <div class="odyssey-plans">\n'
        for i, plan in enumerate(plans):
            key = ['a', 'b', 'c'][i] if i < 3 else 'a'
            html += f'    <div class="odyssey-card plan-{key}">\n'
            html += f'      <div class="odyssey-tag">{PLAN_LABELS.get(key.upper(), "")}</div>\n'
            html += f'      <div class="odyssey-title">{plan.get("title", "")}</div>\n'
            html += f'      <div class="odyssey-timeline">{plan.get("timeline", "")}</div>\n'

            questions = plan.get('questions', [])
            if questions:
                html += '      <div class="odyssey-questions">\n'
                html += '        <div class="q-label">值得测试的问题</div>\n'
                for q in questions:
                    html += f'        <div class="q-item">{q}</div>\n'
                html += '      </div>\n'

            eval_data = plan.get('eval', {})
            if eval_data:
                html += '      <div class="eval-grid">\n'
                eval_items = [
                    ('物力', 'resources'),
                    ('喜欢', 'like'),
                    ('自信', 'confidence'),
                    ('一致性', 'alignment'),
                ]
                color = PLAN_COLORS.get(key.upper(), COLORS['accent'])
                for label, field in eval_items:
                    val = eval_data.get(field, 0)
                    try:
                        pct = int(float(val))
                    except (ValueError, TypeError):
                        pct = 0
                    val_label = eval_data.get(f'{field}_label', f'{pct}%')
                    html += f'        <div class="eval-item">\n'
                    html += f'          <span class="eval-name">{label}</span>\n'
                    html += f'          <div class="eval-bar"><div class="eval-bar-fill" style="width: {pct}%; background: {color}"></div></div>\n'
                    html += f'          <span class="eval-value">{val_label}</span>\n'
                    html += f'        </div>\n'
                html += '      </div>\n'

            html += '    </div>\n'
        html += '  </div>\n'

    # Execution structure
    exec_data = odyssey.get('execution')
    if exec_data:
        html += '  <h3>可执行结构（你选择先试的那条路）</h3>\n'
        html += '  <table class="exec-table">\n    <tbody>\n'
        exec_rows = [
            ('反愿景', 'anti_vision'),
            ('愿景', 'vision'),
            ('本季度核心问题', 'quarter_q'),
            ('一个月原型', 'month_proto'),
            ('每日微行动', 'daily'),
            ('底线', 'bottom_line'),
        ]
        for label, field in exec_rows:
            val = exec_data.get(field, '')
            if val:
                html += f'      <tr><td>{label}</td><td>{val}</td></tr>\n'
        html += '    </tbody>\n  </table>\n'

    if 'conclusion' in odyssey:
        html += f'<div class="narrative">{odyssey["conclusion"]}</div>\n'

    return html


def build_actions_html(actions):
    """构建行动清单 HTML"""
    html = ''
    if 'narrative' in actions:
        html += f'<div class="narrative">{actions["narrative"]}</div>\n'

    action_types = [
        ('talk', '谈', '原型对话'),
        ('try', '试', '原型体验'),
        ('step', '走', '本周第一步'),
        ('habit', '醒', '随身练习'),
    ]

    html += '  <div class="action-list">\n'
    for i, (icon_cls, icon_text, title) in enumerate(action_types):
        key = ['talk', 'try', 'step', 'habit'][i]
        desc = actions.get(key, '')
        if desc:
            html += f'    <div class="action-item">\n'
            html += f'      <div class="action-icon {icon_cls}">{icon_text}</div>\n'
            html += f'      <div class="action-content">\n'
            html += f'        <div class="action-title">{title}</div>\n'
            html += f'        <div class="action-desc">{desc}</div>\n'
            html += f'      </div>\n'
            html += f'    </div>\n'
    html += '  </div>\n'

    return html


def build_quote_card_html(quote):
    """构建对话金句卡"""
    html = '  <div class="quote-card">\n'
    html += '    <div class="quote-label">你在对话中说的一句话</div>\n'
    html += f'    <div class="quote-text">{quote.get("text", "")}</div>\n'
    if quote.get('context'):
        html += f'    <div class="quote-context">{quote["context"]}</div>\n'
    html += '  </div>\n'
    return html


def build_future_letter_html(letter):
    """构建给未来的信"""
    future_date = letter.get('date', '')
    body = letter.get('body', '')
    html = '  <div class="future-letter">\n'
    html += f'    <div class="letter-date">写给 {future_date} 的你</div>\n'
    html += f'    <div class="letter-body">{body}</div>\n'
    html += '    <div class="letter-sig">— 此刻的你</div>\n'
    html += '  </div>\n'
    return html


def build_closing_html(closing):
    """构建失败免疫 HTML"""
    html = ''
    if 'narrative' in closing:
        html += f'  <div class="closing">\n'
        html += f'    {closing["narrative"]}\n'
        html += '    <div class="closing-sig">— 你的人生设计师</div>\n'
        html += '  </div>\n'

    quote = closing.get('philosophy_quote')
    if quote:
        html += '  <div class="philosophy-quote">\n'
        html += f'    <div class="pq-text">{quote.get("text", "")}</div>\n'
        html += f'    <div class="pq-author">{quote.get("author", "")}</div>\n'
        html += '    <div class="pq-line"></div>\n'
        html += '  </div>\n'

    return html


def generate_report(data):
    """
    从富文本 JSON 生成完整 HTML 报告。

    JSON 结构使用内容区块（narrative），不再是原子占位符。
    AI 自由写作的叙事文本会被包裹在精美的样式中。
    """
    date = data.get('date', datetime.now().strftime('%Y年%m月%d日'))
    user_name = data.get('user_name', '')

    sections_html = ''

    # 01 - 你在这里
    dashboard = data.get('dashboard', {})
    if dashboard:
        sections_html += build_section(1, '你在这里', build_dashboard_html(dashboard))

    # 对话金句卡（如果有）
    golden_quote = data.get('golden_quote')
    if golden_quote:
        sections_html += build_quote_card_html(golden_quote)

    # 02 - 真问题
    reframe = data.get('reframe', {})
    if reframe:
        sections_html += build_section(2, '真问题', build_reframe_html(reframe))

    # 03 - 你的指南针
    compass = data.get('compass', {})
    if compass:
        sections_html += build_section(3, '你的指南针', build_compass_html(compass))

    # 04 - 你的能量地图
    energy = data.get('energy', {})
    if energy:
        sections_html += build_section(4, '你的能量地图', build_energy_html(energy))

    # 05 - 三个奥德赛计划
    odyssey = data.get('odyssey', {})
    if odyssey:
        sections_html += build_section(5, '三个奥德赛计划', build_odyssey_html(odyssey))

    # 06 - 原型行动清单
    actions = data.get('actions', {})
    if actions:
        sections_html += build_section(6, '原型行动清单', build_actions_html(actions))

    # 给6个月后自己的一封信
    future_letter = data.get('future_letter')
    if future_letter:
        sections_html += build_future_letter_html(future_letter)

    # 07 - 失败免疫
    closing = data.get('closing', {})
    if closing:
        sections_html += build_section(7, '失败免疫', build_closing_html(closing))

    css = build_css()

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>个人人生设计蓝图 — {user_name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="container">

  <header class="report-header">
    <div class="label">LIFE DESIGN BLUEPRINT</div>
    <h1>个人人生设计蓝图</h1>
    <div class="subtitle">基于斯坦福 Life Design Lab 方法论的深度自我探索报告</div>
    <div class="accent-line"></div>
    <div class="meta">
      <span>{user_name}</span>
      <span>{date}</span>
    </div>
  </header>

{sections_html}

  <footer class="report-footer">
    LIFE DESIGN BLUEPRINT · Based on Stanford d.school Life Design Lab Methodology · {date}
  </footer>

</div>
</body>
</html>
'''
    return html


def generate_demo_data():
    """生成示范数据，展示完整 JSON 结构"""
    return {
        "user_name": "陈柯宇",
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
            "drain": [
                "写周报和项目管理文档——做得好但每次做完都像被抽干",
                "开没有结论的会——时间花了但什么都没推进"
            ],
            "direction": [
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
                    "timeline": "<p><strong>第1年：</strong>在现有公司争取一个产品方向负责人的角色，开始从「管项目」转向「做产品」。</p><p><strong>第2-3年：</strong>积累产品方法论，带一个小团队做出一个有用户口碑的产品。</p><p><strong>第4-5年：</strong>成为某个垂直领域的产品负责人，开始思考自己的产品方向。</p>",
                    "questions": [
                        "在现有公司有没有可能从项目管理转向产品方向？需要什么条件？",
                        "你愿意用两年时间在一个安全的环境里积累产品能力吗？"
                    ],
                    "eval": {"resources": 80, "like": 50, "confidence": 70, "alignment": 45}
                },
                {
                    "title": "独立产品人",
                    "timeline": "<p><strong>第1年：</strong>利用业余时间做第一个小产品。不辞职，用晚上和周末验证。做到有 100 个真实用户。</p><p><strong>第2年：</strong>如果产品有正反馈，开始认真考虑全职做。加入一个创业团队或者自己做。</p><p><strong>第3-5年：</strong>成为一个独立产品人。有自己的产品，有自己的用户，靠产品养活自己。</p>",
                    "questions": [
                        "你脑子里有没有一个具体产品想法，已经想了很久但一直没做？",
                        "如果明天就开始，你的第一个最小可行产品可以是什么？"
                    ],
                    "eval": {"resources": 40, "like": 85, "confidence": 45, "alignment": 90}
                },
                {
                    "title": "产品创作者 + 教育者",
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
            "body": "<p>亲爱的半年后的我：</p><p>如果你正在读这封信，说明你至少活了六个月。</p><p>六个月前的你，在一个周三的晚上，跟一个 AI 聊了快一个小时。你说你像跑步机——跑得很快但原地不动。那天晚上你做了一个决定：今晚写三句话。</p><p>我不知道你写了没有。我也不知道你做了那个产品没有。但我知道一件事：你愿意认真想这个问题，本身就说明你还在乎。</p><p>如果你已经开始做了——不管做得好不好——你已经比六个月前的自己勇敢了太多。</p><p>如果你还没开始——也没关系。你还有下一个六个月。人生不是考试，没有过期。</p><p>但请你现在做一件事：回想一下那天晚上聊天时，你说到帮朋友做产品那个下午时你的语气。那个语气里的你，才是你。</p><p>去找他。</p>"
        },
        "closing": {
            "narrative": "<p>你有三个版本可以试。你不需要选最好的那个——你只需要选一个先走。</p><p>走不通就换一个。这不是考试，没有不及格。</p><p>你今天做的最重要的事不是得到了三个计划。而是——你终于允许自己去想「我还可以活成另一种样子」。</p><p>那个可能性一直都在。你只是今天第一次认真地看了它一眼。</p><p>去写那三句话吧。今晚就好。</p>",
            "philosophy_quote": {
                "text": "「人生不是我们发现了什么，而是我们创造了什么。你不是在寻找一条已有的路——你在开辟一条只属于你的路。」",
                "author": "— Bill Burnett & Dave Evans, Designing Your Life"
            }
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

    # 生成报告
    report_html = generate_report(data)

    # 确定输出路径
    if not args.output:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        user_name = data.get('user_name', '用户')
        date_str = datetime.now().strftime('%Y%m%d')
        args.output = os.path.join(output_dir, f'人生设计蓝图_{user_name}_{date_str}.html')

    # 写入
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report_html)

    if args.quiet:
        print(args.output)
    else:
        print(f'✅ 报告已生成：{args.output}')
        print(f'   文件大小：{os.path.getsize(args.output):,} 字节')
        section_count = sum(1 for k in ['dashboard','reframe','compass','energy','odyssey','actions','closing'] if k in data)
        print(f'   章节数：{section_count}/7')
        if data.get('golden_quote'):
            print(f'   金句卡：✅')
        if data.get('future_letter'):
            print(f'   给未来的信：✅')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
markdown_generator.py — 人生设计蓝图 Markdown 版本生成器

同一份富文本 JSON → 一份 md 文件。用途：
  1. 本地阅读（Obsidian / Logseq / Bear / VS Code / Cursor）
  2. 内嵌到 HTML 里做双载体（<script type="text/markdown" id="blueprint-md">）
  3. 用户复制粘贴发朋友圈 / 发给朋友 / 喂给其他 AI

设计约束（沿用 style-c 的禅意克制）：
  - 大量留白，章节间用 --- 分隔
  - 用户原话用 blockquote + em 强调
  - 数字用 mono 感的对齐表格
  - 不加装饰性 emoji（唯一例外：结尾的 ✉ 信封）

用法：
  python3 scripts/markdown_generator.py --input data.json
  python3 scripts/markdown_generator.py --input data.json --output blueprint.md
  python3 scripts/markdown_generator.py --demo
"""

import json
import re
import sys
import os
import argparse
from datetime import datetime


DIM_LABELS = {
    'health': '健康',
    'work':   '工作',
    'play':   '娱乐',
    'love':   '爱',
}


def strip_html(s):
    """把 HTML 段落还原成 md 兼容的纯文本。
    <p>…</p>  → 段落
    <strong>…</strong> → **…**
    <em>…</em> → *…*
    其他标签直接剥掉。
    """
    if not s:
        return ''
    s = s.replace('\r', '')
    # 段落
    s = re.sub(r'</p>\s*<p[^>]*>', '\n\n', s, flags=re.IGNORECASE)
    s = re.sub(r'<p[^>]*>', '', s, flags=re.IGNORECASE)
    s = re.sub(r'</p>', '', s, flags=re.IGNORECASE)
    # 换行
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.IGNORECASE)
    # 强调
    s = re.sub(r'<(strong|b)>', '**', s, flags=re.IGNORECASE)
    s = re.sub(r'</(strong|b)>', '**', s, flags=re.IGNORECASE)
    s = re.sub(r'<(em|i)>', '*', s, flags=re.IGNORECASE)
    s = re.sub(r'</(em|i)>', '*', s, flags=re.IGNORECASE)
    # 剩余的所有标签
    s = re.sub(r'<[^>]+>', '', s)
    # 常见 HTML 实体
    s = s.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    # 收缩多余空白
    lines = [ln.rstrip() for ln in s.split('\n')]
    # 折叠三个及以上换行为两个
    out = '\n'.join(lines)
    out = re.sub(r'\n{3,}', '\n\n', out)
    return out.strip()


def md_epigraph(data, key):
    """章节题记（用户原话）→ blockquote"""
    epis = data.get('epigraphs') or {}
    e = epis.get(key)
    if isinstance(e, dict) and e.get('text'):
        phase = e.get('phase') or '对话中'
        return f'> *"{e["text"]}"*\n> — 你 · {phase}\n\n'
    if isinstance(e, str) and e.strip():
        return f'> *"{e.strip()}"*\n> — 你\n\n'
    return ''


def md_masthead_hero(data):
    user_name = data.get('user_name', '朋友')
    date = data.get('date') or datetime.now().strftime('%Y-%m-%d')
    volume = data.get('volume') or 'Nº 001'
    hero_title = data.get('hero_title') or '在不确定中，设计属于自己的人生'
    subtitle = data.get('hero_subtitle') or '一份关于选择、意义与不确定性的私人蓝图'
    return (
        f'# {hero_title}\n\n'
        f'### {subtitle}\n\n'
        f'> LIFE DESIGN BLUEPRINT · {volume} · {date} · {user_name}\n\n'
        f'---\n\n'
    )


def md_dashboard(data):
    d = data.get('dashboard') or {}
    if not d:
        return ''
    out = ['## 01 · 你在这里\n']
    epi = md_epigraph(data, 'dashboard')
    if epi:
        out.append(epi)
    if d.get('narrative'):
        out.append(strip_html(d['narrative']) + '\n\n')

    scores = d.get('scores') or {}
    if scores:
        out.append('|  维度  | 分数 | 一句话 |\n')
        out.append('|:------:|:----:|:------|\n')
        for k in ['health', 'work', 'play', 'love']:
            item = scores.get(k) or {}
            if isinstance(item, dict):
                score = item.get('score', '—')
                note = item.get('note', '')
            else:
                score = item
                note = ''
            out.append(f'| {DIM_LABELS.get(k, k)} | {score}/10 | {note} |\n')
        out.append('\n')

    if d.get('analysis'):
        out.append(strip_html(d['analysis']) + '\n\n')

    out.append('---\n\n')
    return ''.join(out)


def md_golden_quote(data):
    q = data.get('golden_quote')
    if not q:
        return ''
    text = q.get('text', '') if isinstance(q, dict) else str(q)
    ctx = q.get('context', '') if isinstance(q, dict) else ''
    attr = f'— 你 · {ctx}' if ctx else '— 你说过的话'
    return f'> **"{text}"**\n>\n> {attr}\n\n---\n\n'


def md_reframe(data):
    r = data.get('reframe') or {}
    if not r:
        return ''
    out = ['## 02 · 重构问题\n']
    epi = md_epigraph(data, 'reframe')
    if epi:
        out.append(epi)
    if r.get('narrative'):
        out.append(strip_html(r['narrative']) + '\n\n')

    # 四步对照
    rows = [
        ('perceived',    '你以为的'),
        ('gravity',      '重力问题'),
        ('real',         '真  问 题'),
        ('wrong_premise','错误前提'),
    ]
    has = any(r.get(k) for k, _ in rows)
    if has:
        out.append('```\n')
        for k, label in rows:
            v = r.get(k, '')
            if v:
                marker = ' ★' if k == 'real' else '  '
                out.append(f'{label}{marker}   →   {v}\n')
        out.append('```\n\n')

    if r.get('conclusion'):
        out.append(strip_html(r['conclusion']) + '\n\n')

    out.append('---\n\n')
    return ''.join(out)


def md_compass(data):
    c = data.get('compass') or {}
    if not c:
        return ''
    out = ['## 03 · 你的内在罗盘\n']
    epi = md_epigraph(data, 'compass')
    if epi:
        out.append(epi)
    if c.get('narrative'):
        out.append(strip_html(c['narrative']) + '\n\n')

    work = c.get('work_view', '')
    life = c.get('life_view', '')
    align = c.get('alignment', '')
    if work or life:
        out.append(f'**工作观**  →  {work}\n\n')
        out.append(f'**人生观**  →  {life}\n\n')
        if align:
            out.append(f'*对齐状态：{align}*\n\n')

    conclusion = c.get('conclusion') or c.get('diagnosis')
    if conclusion:
        out.append(strip_html(conclusion) + '\n\n')
    out.append('---\n\n')
    return ''.join(out)


def md_energy(data):
    e = data.get('energy') or {}
    if not e:
        return ''
    out = ['## 04 · 能量地图\n']
    epi = md_epigraph(data, 'energy')
    if epi:
        out.append(epi)
    if e.get('narrative'):
        out.append(strip_html(e['narrative']) + '\n\n')

    quadrants = [
        ('flow',            '心流时刻',    None),
        ('recharge',        '回血活动',    None),
        ('drain_but_good',  '擅长但耗能',  'drain'),
        ('lean_toward',     '偏  向',      'direction'),
    ]
    for key, label, fallback in quadrants:
        val = e.get(key) or (e.get(fallback) if fallback else None)
        if not val:
            continue
        items = val if isinstance(val, list) else [val]
        out.append(f'**{label}**\n')
        for it in items:
            out.append(f'- {it}\n')
        out.append('\n')

    if e.get('formula'):
        out.append(f'**能量公式**  →  {e["formula"]}\n\n')
    if e.get('conclusion'):
        out.append(strip_html(e['conclusion']) + '\n\n')

    out.append('---\n\n')
    return ''.join(out)


def md_odyssey(data):
    o = data.get('odyssey') or {}
    if not o:
        return ''
    out = ['## 05 · 三个奥德赛计划\n']
    epi = md_epigraph(data, 'odyssey')
    if epi:
        out.append(epi)
    if o.get('narrative'):
        out.append(strip_html(o['narrative']) + '\n\n')

    plans = o.get('plans') or []
    tags = ['Plan A · 延续当下', 'Plan B · 另一条路', 'Plan C · 无限可能']
    for i, p in enumerate(plans):
        if not isinstance(p, dict):
            continue
        tag = tags[i] if i < len(tags) else f'Plan · {i+1}'
        title = p.get('title', '')
        # 如果 title 已经出现在 tag 里，就不重复显示
        heading = tag if (title and title in tag) else f'{tag} — {title}'
        out.append(f'### {heading}\n\n')
        if p.get('body'):
            out.append(strip_html(p['body']) + '\n\n')
        if p.get('timeline'):
            out.append('**时间线**\n\n')
            out.append(strip_html(p['timeline']) + '\n\n')
        if p.get('questions'):
            out.append('**想问自己**\n\n')
            for q in p['questions']:
                out.append(f'- *{q}*\n')
            out.append('\n')
        ev = p.get('eval') or {}
        if ev:
            out.append('| 资源 | 喜欢程度 | 信心 | 与人生观对齐 |\n')
            out.append('|:----:|:--------:|:----:|:-----------:|\n')
            out.append(f'| {ev.get("resources", 0)} | {ev.get("like", 0)} | {ev.get("confidence", 0)} | {ev.get("alignment", 0)} |\n\n')

    # 六层执行结构
    ex = o.get('execution') or {}
    if ex:
        out.append('### 执行路径\n\n')
        if ex.get('anti_vision'):
            out.append(f'**反愿景**  →  {ex["anti_vision"]}\n\n')
        if ex.get('vision'):
            out.append(f'**愿景**  →  {ex["vision"]}\n\n')
        if ex.get('quarter_q'):
            out.append(f'**本季度核心问题**  →  {ex["quarter_q"]}\n\n')
        if ex.get('month_proto'):
            out.append(f'**本月原型**  →  {ex["month_proto"]}\n\n')
        if ex.get('daily'):
            out.append(f'**每日习惯**  →  {ex["daily"]}\n\n')
        if ex.get('bottom_line'):
            out.append(f'**底线规则**  →  {ex["bottom_line"]}\n\n')

    if o.get('conclusion'):
        out.append(strip_html(o['conclusion']) + '\n\n')

    out.append('---\n\n')
    return ''.join(out)


def md_actions(data):
    a = data.get('actions') or {}
    if not a:
        return ''
    out = ['## 06 · 接下来 30 天\n']
    epi = md_epigraph(data, 'actions')
    if epi:
        out.append(epi)
    if a.get('narrative'):
        out.append(strip_html(a['narrative']) + '\n\n')

    groups = [
        ('talk', '谈  ·  TALK'),
        ('try',  '试  ·  TRY'),
        ('step', '走  ·  GO'),
        ('habit','醒  ·  WAKE'),
    ]
    seen = set()
    for key, title in groups:
        if key in seen:
            continue
        items = a.get(key)
        if not items:
            continue
        if isinstance(items, str):
            items = [items]
        seen.add(key)

        out.append(f'**{title}**\n\n')
        for it in items:
            text = it if isinstance(it, str) else it.get('what', '')
            out.append(f'- [ ] {text}\n')
        out.append('\n')

    out.append('---\n\n')
    return ''.join(out)


def md_closing(data):
    c = data.get('closing') or {}
    if not c:
        return ''
    out = ['## 07 · 失败免疫\n']
    epi = md_epigraph(data, 'closing')
    if epi:
        out.append(epi)
    if c.get('narrative'):
        out.append(strip_html(c['narrative']) + '\n\n')
    quote = c.get('quote') or c.get('philosophy_quote')
    if quote:
        text = quote.get('text', '') if isinstance(quote, dict) else str(quote)
        author = quote.get('author', '') if isinstance(quote, dict) else ''
        author_line = f'— {author}' if author else '— 无限游戏 · Simon Sinek'
        out.append(f'> **{text}**\n>\n> {author_line}\n\n')
    out.append('---\n\n')
    return ''.join(out)


def md_appointment(data):
    cap = data.get('capsule') or {}
    d30 = cap.get('trigger_at_d30') or ''
    # 如果 capsule 里没有 trigger_at_d30，但至少存在 capsule 字段，就动态推算
    if not d30 and cap:
        from datetime import timedelta
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
    return (
        '## ✉ 一封来自 30 天前的信\n\n'
        f'**将在 {date_display} 到达。**\n\n'
        '那不是我写的，是那天下午的你写的。\n\n'
        '到时候见。\n\n'
        '---\n\n'
    )


def md_future_letter(data):
    """给未来的信（future_letter）"""
    letter = data.get('future_letter')
    if not isinstance(letter, dict) or not letter:
        return ''
    out = ['## 一封写给未来的信\n\n']
    date = letter.get('date', '')
    if date:
        out.append(f'*{date}*\n\n')
    greeting = letter.get('greeting', '亲爱的未来的你：')
    out.append(f'{greeting}\n\n')
    body = letter.get('body', '')
    if body:
        out.append(strip_html(body) + '\n\n')
    sign = letter.get('sign', '—— 那个下午的你')
    out.append(f'{sign}\n\n')
    out.append('---\n\n')
    return ''.join(out)


def md_footer(data):
    cap = data.get('capsule') or {}
    sealed = cap.get('sealed_at', '')
    cid = cap.get('capsule_id', '')
    tail = ['*Life Design Blueprint · Based on Stanford d.school Life Design Lab*\n']
    if cid:
        tail.append(f'*Sealed at {sealed} · Capsule ID: {cid}*\n')
    return ''.join(tail)


def generate_markdown(data):
    """把富文本 JSON 渲染成完整的 md 字符串。"""
    parts = [
        md_masthead_hero(data),
        md_dashboard(data),
        md_golden_quote(data),
        md_reframe(data),
        md_compass(data),
        md_energy(data),
        md_odyssey(data),
        md_actions(data),
        md_future_letter(data),
        md_closing(data),
        md_appointment(data),
        md_footer(data),
    ]
    return ''.join(parts)


def main():
    parser = argparse.ArgumentParser(description='人生设计蓝图 Markdown 生成器')
    parser.add_argument('--input', '-i', help='对话数据 JSON 文件路径')
    parser.add_argument('--output', '-o', help='输出 md 文件路径（默认放到 output/）')
    parser.add_argument('--demo', '-d', action='store_true', help='使用示范数据')
    parser.add_argument('--stdout', action='store_true', help='直接输出到 stdout，不写文件')
    args = parser.parse_args()

    if args.demo:
        # 从 report_generator 借示范数据，保持一致
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from report_generator import generate_demo_data
        data = generate_demo_data()
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        parser.print_help()
        sys.exit(0)

    md = generate_markdown(data)

    if args.stdout:
        sys.stdout.write(md)
        return

    if not args.output:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        user_name = data.get('user_name', '用户')
        date_str = datetime.now().strftime('%Y%m%d')
        args.output = os.path.join(output_dir, f'人生设计蓝图_{user_name}_{date_str}.md')

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f'✅ Markdown 已生成：{args.output}')
    print(f'   字数：{len(md.replace(chr(10), "").replace(" ", ""))}')


if __name__ == '__main__':
    main()

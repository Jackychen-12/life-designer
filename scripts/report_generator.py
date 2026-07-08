#!/usr/bin/env python3
"""
report_generator.py — 人生设计蓝图报告生成器

将对话数据（JSON）填入 HTML 模板，生成可双击打开的《个人人生设计蓝图》。

用法：
  python3 scripts/report_generator.py --input data.json --output report.html
  python3 scripts/report_generator.py --input data.json   # 自动生成到 output/ 目录
  python3 scripts/report_generator.py --input data.json --template assets/report-template.html

数据来源：
  对话结束后，由 AI 根据对话内容整理为 JSON 格式，传入此脚本。
"""

import json
import sys
import os
import argparse
from datetime import datetime


def load_json(path):
    """加载对话数据 JSON 文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template(path):
    """加载 HTML 模板"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def safe_str(val, default=""):
    """安全转换为字符串，None 返回默认值"""
    if val is None:
        return default
    return str(val)


def generate_report(data, template):
    """
    将对话数据填入模板占位符，返回完整 HTML 字符串。

    处理规则：
    - {{KEY}} → 直接替换为 data["KEY"] 的值
    - 未提供的 key → 替换为空字符串
    - 百分比字段（HEALTH_PCT 等）→ 分数 × 10
    - 动态处理多条目（能量卡片、奥德赛问题等）
    """
    result = template

    # 注入生成日期（如数据中未提供）
    if 'DATE' not in data:
        data['DATE'] = datetime.now().strftime('%Y年%m月%d日')

    # 自动计算百分比（如果未提供）
    for dim in ['HEALTH', 'WORK', 'PLAY', 'LOVE']:
        score_key = f'{dim}_SCORE'
        pct_key = f'{dim}_PCT'
        if score_key in data and pct_key not in data:
            try:
                score = float(data[score_key])
                data[pct_key] = str(int(score * 10))
            except (ValueError, TypeError):
                data[pct_key] = '0'

    # 处理所有 {{KEY}} 占位符
    # 使用正则或简单替换
    import re
    placeholder_pattern = re.compile(r'\{\{(\w+)\}\}')

    def replace_placeholder(match):
        key = match.group(1)
        value = data.get(key, '')
        return safe_str(value)

    result = placeholder_pattern.sub(replace_placeholder, result)

    return result


def validate_data(data):
    """
    校验关键数据是否完整，返回 (is_valid, warnings)。
    不阻断生成，只输出警告。
    """
    warnings = []

    # 必要字段
    required = ['USER_NAME']
    for key in required:
        if key not in data or not data[key]:
            warnings.append(f'缺少必要字段: {key}')

    # 推荐字段（四维度分数）
    recommended_scores = ['HEALTH_SCORE', 'WORK_SCORE', 'PLAY_SCORE', 'LOVE_SCORE']
    for key in recommended_scores:
        if key not in data:
            dim = key.replace('_SCORE', '')
            warnings.append(f'缺少维度分数: {dim}（{key}）')

    # 推荐字段（奥德赛计划）
    for plan in ['A', 'B', 'C']:
        title_key = f'PLAN_{plan}_TITLE'
        if title_key not in data or not data[title_key]:
            warnings.append(f'缺少奥德赛计划 {plan} 标题（{title_key}）')

    is_valid = len([w for w in warnings if '缺少必要字段' in w]) == 0
    return is_valid, warnings


def main():
    parser = argparse.ArgumentParser(
        description='人生设计蓝图报告生成器 — 将对话数据填入 HTML 模板',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  python3 scripts/report_generator.py --input conversation.json
  python3 scripts/report_generator.py --input conversation.json --output blueprint.html
  python3 scripts/report_generator.py --input conversation.json --template assets/report-template.html

JSON 数据结构示例：
  {
    "USER_NAME": "小明",
    "HEALTH_SCORE": "7", "HEALTH_NOTE": "身体还行，但睡眠不太好",
    "WORK_SCORE": "8", "WORK_NOTE": "工作投入但有点透支",
    ...
    "PLAN_A_TITLE": "继续深耕AI产品",
    "PLAN_A_TIMELINE": "第一年...第二年...",
    ...
  }
        '''
    )
    parser.add_argument('--input', '-i', required=True, help='对话数据 JSON 文件路径')
    parser.add_argument('--output', '-o', help='输出 HTML 文件路径（默认自动生成）')
    parser.add_argument('--template', '-t', help='HTML 模板路径（默认自动查找）')
    parser.add_argument('--quiet', '-q', action='store_true', help='安静模式，只输出文件路径')

    args = parser.parse_args()

    # 1. 校验输入文件
    if not os.path.exists(args.input):
        print(f'错误：找不到输入文件 {args.input}', file=sys.stderr)
        sys.exit(1)

    # 2. 加载数据
    try:
        data = load_json(args.input)
    except json.JSONDecodeError as e:
        print(f'错误：JSON 解析失败 — {e}', file=sys.stderr)
        sys.exit(1)

    # 3. 查找模板
    if args.template:
        template_path = args.template
    else:
        # 按优先级查找模板
        search_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'report-template.html'),
            os.path.expanduser('~/.qoderwork/skills/life-designer/assets/report-template.html'),
            'assets/report-template.html',
        ]
        template_path = None
        for path in search_paths:
            normalized = os.path.normpath(path)
            if os.path.exists(normalized):
                template_path = normalized
                break

        if template_path is None:
            print('错误：找不到 HTML 模板，请用 --template 指定路径', file=sys.stderr)
            print('搜索过以下位置：', file=sys.stderr)
            for path in search_paths:
                print(f'  - {os.path.normpath(path)}', file=sys.stderr)
            sys.exit(1)

    # 4. 加载模板
    try:
        template = load_template(template_path)
    except Exception as e:
        print(f'错误：模板加载失败 — {e}', file=sys.stderr)
        sys.exit(1)

    # 5. 数据校验
    is_valid, warnings = validate_data(data)
    if not args.quiet:
        for w in warnings:
            print(f'⚠️  {w}', file=sys.stderr)

    # 6. 生成报告
    report_html = generate_report(data, template)

    # 7. 确定输出路径
    if args.output:
        output_path = args.output
    else:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        user_name = safe_str(data.get('USER_NAME'), '用户')
        date_str = datetime.now().strftime('%Y%m%d')
        output_path = os.path.join(output_dir, f'人生设计蓝图_{user_name}_{date_str}.html')

    # 8. 写入文件
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_html)

    # 9. 输出结果
    if args.quiet:
        print(output_path)
    else:
        print(f'✅ 报告已生成：{output_path}')
        print(f'   文件大小：{os.path.getsize(output_path):,} 字节')
        # 统计填充了多少个占位符
        filled = len([k for k, v in data.items() if v])
        print(f'   数据字段：{filled} 个有效字段')


if __name__ == '__main__':
    main()

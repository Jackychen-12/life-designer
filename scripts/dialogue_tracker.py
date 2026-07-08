#!/usr/bin/env python3
"""
dialogue_tracker.py — 对话状态追踪器

追踪人生设计对话的当前阶段、已完成步骤、下一步引导。
供 AI 在对话过程中调用，确保不跳步骤、不遗漏关键追问。

用法：
  python3 scripts/dialogue_tracker.py --action init --json '{"user_name":"小明"}'
  python3 scripts/dialogue_tracker.py --action status
  python3 scripts/dialogue_tracker.py --action complete --json '{"step":"1.1"}'
  python3 scripts/dialogue_tracker.py --action next
  python3 scripts/dialogue_tracker.py --action reset
"""

import json
import sys
import os
import argparse
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', '.dialogue_state.json')

# ============================================================
# 对话流程定义
# ============================================================

PHASES = [
    {
        "id": "phase1",
        "name": "你在这里（看清现状）",
        "emotion_goal": "安全感、被看见",
        "steps": [
            {
                "id": "1.1",
                "name": "仪表盘打分",
                "description": "引导用户给健康/工作/娱乐/爱四个维度打分（0-10）",
                "key_listen": "分数之间的落差比分数本身更重要",
                "must_cover": ["四维度各打分", "亮红灯维度追问"],
                "avoid": ["一次问四个维度", "评价分数高低"]
            },
            {
                "id": "1.2",
                "name": "找到核心焦虑",
                "description": "问：现在最想解决、最焦虑的人生问题是什么？",
                "key_listen": "判断是真问题还是重力问题",
                "must_cover": ["真问题/重力问题分类", "思维误区重定义"],
                "avoid": ["急着给建议", "否定用户的焦虑"]
            },
            {
                "id": "1.3",
                "name": "反向推演（可选）",
                "description": "假如五年什么都不变，一个普通周二怎么过？",
                "key_listen": "用户的身体反应——紧张/释然/恐惧",
                "must_cover": ["先征求意愿", "做完立刻转正面"],
                "avoid": ["对低谷用户使用", "做完不转正面"]
            }
        ],
        "completion_check": "用户能说出'我在XX方面最失衡'，至少一个问题被重定义"
    },
    {
        "id": "phase2",
        "name": "你的指南针（校准方向）",
        "emotion_goal": "被理解、顿悟",
        "steps": [
            {
                "id": "2.1",
                "name": "工作观",
                "description": "工作对你意味什么？为什么工作？",
                "key_listen": "工作是手段还是目的？为谁工作？",
                "must_cover": ["工作vs金钱", "工作vs他人", "工作vs世界"],
                "avoid": ["问'想做什么工作'", "预设工作必须有意义"]
            },
            {
                "id": "2.2",
                "name": "人生观",
                "description": "什么样的人生算没白活？",
                "key_listen": "用户在意的是连接、创造、自由还是其他",
                "must_cover": ["意义感来源", "与世界的连接方式"],
                "avoid": ["暗示必须宏大", "评判价值观"]
            },
            {
                "id": "2.3",
                "name": "指南针校准",
                "description": "帮他看工作观和人生观之间有没有冲突",
                "key_listen": "两个观指向同一方向还是互相拉扯",
                "must_cover": ["一致性诊断", "指出偏离方向"],
                "avoid": ["替用户决定哪个对", "说'你应该...'"]
            }
        ],
        "completion_check": "用户能用自己的话说出'我的正北方向大概是XX'"
    },
    {
        "id": "phase3",
        "name": "寻路（心流与能量）",
        "emotion_goal": "被点亮、兴奋",
        "steps": [
            {
                "id": "3.1",
                "name": "心流时刻挖掘",
                "description": "回忆完全投入、忘记时间的时刻，用 AEIOU 追问",
                "key_listen": "具体细节——做什么/在哪/和谁/用什么工具",
                "must_cover": ["AEIOU 五维度拆解", "回血vs耗能区分"],
                "avoid": ["抽象总结", "说'你的激情是XX'"]
            },
            {
                "id": "3.2",
                "name": "能量公式总结",
                "description": "帮用户提炼'什么条件组合让你活过来'",
                "key_listen": "擅长但耗能 vs 热爱但不够擅长",
                "must_cover": ["能量公式", "设计偏向"],
                "avoid": ["建议'多花时间在热爱的事上'（太空泛）"]
            }
        ],
        "completion_check": "用户说出至少两个心流模式，理解擅长≠热爱"
    },
    {
        "id": "phase4",
        "name": "摆脱困境与多种可能（奥德赛计划）",
        "emotion_goal": "解放感、踏实",
        "steps": [
            {
                "id": "4.1",
                "name": "锚问题识别",
                "description": "有没有守了很久但行不通的方案？",
                "key_listen": "沉没成本 vs 真实需求",
                "must_cover": ["识别执念", "找到背后真正的需求"],
                "avoid": ["说'你应该放下'", "否定用户的坚持"]
            },
            {
                "id": "4.2",
                "name": "奥德赛计划",
                "description": "设计三个平等的五年人生版本",
                "key_listen": "版本二最难回答，版本三容易变成躺平",
                "must_cover": ["三个版本都有标题+时间线", "四维评估", "三方案平等"],
                "avoid": ["变成好/中/差三档", "替用户选择"]
            },
            {
                "id": "4.3",
                "name": "可执行结构",
                "description": "如用户已倾向一个版本，落成六层执行结构",
                "key_listen": "用户选的不是'最好的'而是'最想先试的'",
                "must_cover": ["反愿景到每日微行动六层", "明确这是原型不是赌注"],
                "avoid": ["做成终身承诺", "暗示选错就完了"]
            }
        ],
        "completion_check": "三个平等版本 + 四维评估 + 原型行动清单"
    }
]


# ============================================================
# 状态管理
# ============================================================

def load_state():
    """加载当前对话状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_state(state):
    """保存对话状态"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def init_state(user_name=None):
    """初始化对话状态"""
    state = {
        "user_name": user_name or "",
        "started_at": datetime.now().isoformat(),
        "current_phase": "phase1",
        "current_step": "1.1",
        "completed_steps": [],
        "notes": [],
        "gravity_problems": [],
        "real_problems": [],
        "odyssey_plans": {"A": None, "B": None, "C": None}
    }
    save_state(state)
    return state


# ============================================================
# 操作函数
# ============================================================

def get_step_info(step_id):
    """根据步骤 ID 找到完整步骤信息"""
    for phase in PHASES:
        for step in phase["steps"]:
            if step["id"] == step_id:
                return {
                    "phase": phase,
                    "step": step
                }
    return None


def action_init(args):
    """初始化对话"""
    data = json.loads(args.json) if args.json else {}
    state = init_state(data.get('user_name'))
    return {
        "status": "initialized",
        "user_name": state["user_name"],
        "message": "对话已初始化，从 Phase 1 Step 1.1 开始"
    }


def action_status(args):
    """查看当前状态"""
    state = load_state()
    if not state:
        return {"error": "对话尚未初始化，请先执行 init"}

    info = get_step_info(state["current_step"])
    result = {
        "user_name": state["user_name"],
        "current_phase": state["current_phase"],
        "current_step": state["current_step"],
        "completed_steps": state["completed_steps"],
        "progress": f"{len(state['completed_steps'])}/10 步已完成",
    }

    if info:
        result["current_step_detail"] = {
            "name": info["step"]["name"],
            "description": info["step"]["description"],
            "key_listen": info["step"]["key_listen"],
            "must_cover": info["step"]["must_cover"],
            "avoid": info["step"]["avoid"],
        }
        result["phase_emotion_goal"] = info["phase"]["emotion_goal"]
        result["phase_completion_check"] = info["phase"]["completion_check"]

    return result


def action_next(args):
    """获取下一步引导"""
    state = load_state()
    if not state:
        return {"error": "对话尚未初始化，请先执行 init"}

    current = state["current_step"]
    info = get_step_info(current)

    if not info:
        return {"error": f"找不到步骤 {current}"}

    return {
        "step_id": current,
        "step_name": info["step"]["name"],
        "description": info["step"]["description"],
        "key_listen": info["step"]["key_listen"],
        "must_cover": info["step"]["must_cover"],
        "avoid": info["step"]["avoid"],
        "emotion_goal": info["phase"]["emotion_goal"],
        "hint": "完成后执行 --action complete 标记此步完成"
    }


def action_complete(args):
    """标记步骤完成"""
    state = load_state()
    if not state:
        return {"error": "对话尚未初始化"}

    data = json.loads(args.json) if args.json else {}
    step_id = data.get('step', state["current_step"])

    if step_id not in state["completed_steps"]:
        state["completed_steps"].append(step_id)

    # 记录笔记
    if 'note' in data:
        state["notes"].append({
            "step": step_id,
            "note": data["note"],
            "time": datetime.now().isoformat()
        })

    # 记录重力问题/真问题
    if 'gravity_problem' in data:
        state["gravity_problems"].append(data["gravity_problem"])
    if 'real_problem' in data:
        state["real_problems"].append(data["real_problem"])

    # 记录奥德赛计划
    if 'odyssey_plan' in data:
        plan_key = data.get('plan_key', 'A')
        state["odyssey_plans"][plan_key] = data["odyssey_plan"]

    # 计算下一步
    all_steps = []
    for phase in PHASES:
        for step in phase["steps"]:
            all_steps.append((phase["id"], step["id"]))

    current_idx = next((i for i, (_, sid) in enumerate(all_steps) if sid == step_id), -1)

    if current_idx < len(all_steps) - 1:
        next_phase, next_step = all_steps[current_idx + 1]
        state["current_phase"] = next_phase
        state["current_step"] = next_step
        next_info = get_step_info(next_step)
        next_name = next_info["step"]["name"] if next_info else next_step
    else:
        state["current_phase"] = "done"
        state["current_step"] = "done"
        next_name = "所有步骤已完成，可以生成报告"

    save_state(state)

    return {
        "completed": step_id,
        "next_step": state["current_step"],
        "next_step_name": next_name,
        "progress": f"{len(state['completed_steps'])}/10 步已完成",
        "all_done": state["current_step"] == "done"
    }


def action_reset(args):
    """重置对话状态"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    return {"status": "reset", "message": "对话状态已重置"}


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='对话状态追踪器 — 追踪人生设计对话进度',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
操作说明：
  init     初始化对话
  status   查看当前状态和进度
  next     获取下一步引导（当前步骤的详细信息）
  complete 标记当前步骤完成，推进到下一步
  reset    重置对话状态

示例：
  python3 scripts/dialogue_tracker.py --action init --json '{"user_name":"小明"}'
  python3 scripts/dialogue_tracker.py --action next
  python3 scripts/dialogue_tracker.py --action complete --json '{"step":"1.1","note":"健康3分，睡眠差"}'
  python3 scripts/dialogue_tracker.py --action complete --json '{"step":"1.2","gravity_problem":"行业年龄歧视","real_problem":"害怕不被需要"}'
  python3 scripts/dialogue_tracker.py --action status
        '''
    )
    parser.add_argument('--action', '-a', required=True,
                        choices=['init', 'status', 'next', 'complete', 'reset'],
                        help='操作类型')
    parser.add_argument('--json', '-j', help='操作数据（JSON 字符串）')

    args = parser.parse_args()

    actions = {
        'init': action_init,
        'status': action_status,
        'next': action_next,
        'complete': action_complete,
        'reset': action_reset,
    }

    result = actions[args.action](args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

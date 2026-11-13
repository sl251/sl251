#!/usr/bin/env python3
"""生成深浅双色炫酷动态 System Spec 系统架构遥测 SVG（assets/spec-dark.svg 与 spec-light.svg）。

采用“分布式内核拓扑面板 + 独立实时微仪表 + PCB 总线信号流”视觉隐喻：
每张卡片左侧保留清晰可读的中英文工程规格，右侧嵌入 114x64 独立动态微仪表窗口，
卡片之间通过中心与纵向 PCB 走线串联并由纯声明式 SMIL 光点脉冲驱动。
"""

from __future__ import annotations

import html
import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

# 与遥测头图及审计图保持一致的深浅配色体系
THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "card_bg_start": "#0f1621",
        "card_bg_end": "#0a1018",
        "bay_bg": "#060a10",
        "bay_border": "#1b2636",
        "border": "#243042",
        "bus_trace": "#1e2c3f",
        "bus_via": "#334155",
        "text_primary": "#f0f6fc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "track": "#1a2536",
        "cyan": "#38bdf8",
        "emerald": "#34d399",
        "indigo": "#818cf8",
        "amber": "#f59e0b",
        "rose": "#fb7185",
    },
    "light": {
        "card_bg_start": "#ffffff",
        "card_bg_end": "#f4f8fc",
        "bay_bg": "#e9f0f8",
        "bay_border": "#cfd9e4",
        "border": "#cfd7e2",
        "bus_trace": "#d4dee9",
        "bus_via": "#94a3b8",
        "text_primary": "#1f2328",
        "text_secondary": "#57606a",
        "text_muted": "#6e7781",
        "track": "#cbd5e1",
        "cyan": "#0284c7",
        "emerald": "#059669",
        "indigo": "#4f46e5",
        "amber": "#d97706",
        "rose": "#e11d48",
    },
}

# 6 张工程规格模块定义：(标签, 主值, 中文说明, 强调色键名, 微仪表类型键)
CARDS = [
    (
        "RELEASE & ACCESS",
        "Public Preview · Read-Only",
        "持续滚动更新，核心实例不接受外部 PR",
        "emerald",
        "release",
    ),
    (
        "HARDWARE TARGET",
        "Carbon-Based · Single Node",
        "单节点部署，不支持集群化或横向扩容",
        "cyan",
        "hardware",
    ),
    (
        "POWER INPUT",
        "Carbohydrates · Sleep",
        "断供期间触发性能降级与状态告警",
        "emerald",
        "power",
    ),
    (
        "MAINTENANCE WINDOW",
        "6–8h / 24h · Offline",
        "每日离线执行记忆整理与上下文清理",
        "cyan",
        "maintenance",
    ),
    (
        "CONCURRENCY",
        "1 Thread · Preemptive",
        "严格单线程调度，新想法到达时直接抢占",
        "cyan",
        "concurrency",
    ),
    (
        "ROLLBACK & BACKLOG",
        "No Revert · Growing",
        "历史版本不可回滚，待办持续高于清理速率",
        "amber",
        "backlog",
    ),
]


def _widget_release(t: dict[str, str], mono: str) -> str:
    """微仪表 0：持续滚动构建流水线与只读 PR 拦截屏障。"""
    em = t["emerald"]
    cy = t["cyan"]
    rose = t["rose"]
    return f"""
      <text x="7" y="12" fill="{t['text_muted']}" font-family="{mono}" font-size="7.2" letter-spacing="0.8">STREAM // RO</text>
      <!-- 主干滚动发布信道 -->
      <line x1="8" y1="30" x2="78" y2="30" stroke="{t['track']}" stroke-width="2" stroke-linecap="round"/>
      <line class="stream-dash" x1="8" y1="30" x2="78" y2="30" stroke="{em}" stroke-width="1.4" stroke-dasharray="6 5" stroke-linecap="round"/>
      <!-- 沿主干持续滚动的构建胶囊 -->
      <g class="motion-only">
        <rect x="-6" y="-3" width="12" height="6" rx="3" fill="{em}" fill-opacity="0.9">
          <animateMotion dur="2.2s" repeatCount="indefinite" path="M 10 30 L 76 30"/>
          <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.82;1" dur="2.2s" repeatCount="indefinite"/>
        </rect>
        <rect x="-4.5" y="-2.5" width="9" height="5" rx="2.5" fill="{cy}" fill-opacity="0.85">
          <animateMotion dur="2.2s" begin="-1.1s" repeatCount="indefinite" path="M 10 30 L 76 30"/>
          <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.82;1" dur="2.2s" begin="-1.1s" repeatCount="indefinite"/>
        </rect>
      </g>
      <!-- 核心只读保护盾节点 -->
      <g transform="translate(92, 30)">
        <circle class="motion-only" r="8" fill="none" stroke="{em}" stroke-width="1">
          <animate attributeName="r" values="8;16" dur="2.4s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.7;0" dur="2.4s" repeatCount="indefinite"/>
        </circle>
        <circle r="12" fill="none" stroke="{em}" stroke-width="1.1" stroke-dasharray="4 3" stroke-opacity="0.65">
          <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="7s" repeatCount="indefinite"/>
        </circle>
        <circle r="6.5" fill="{em}" fill-opacity="0.22" stroke="{em}" stroke-width="1.2"/>
        <circle r="2.6" fill="{em}"/>
      </g>
      <!-- 外部 PR 分支尝试接入后被只读门禁拦截 -->
      <path d="M 10 49 L 44 49" fill="none" stroke="{t['track']}" stroke-width="1.4" stroke-dasharray="2 2"/>
      <line x1="48" y1="45" x2="48" y2="53" stroke="{rose}" stroke-width="1.4" stroke-linecap="round"/>
      <text x="53" y="51.5" fill="{rose}" font-family="{mono}" font-size="6.8" letter-spacing="0.4">PR LOCK</text>
      <circle class="motion-only" r="2" fill="{rose}">
        <animateMotion dur="2.6s" repeatCount="indefinite" path="M 12 49 L 43 49"/>
        <animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.2;0.75;1" dur="2.6s" repeatCount="indefinite"/>
      </circle>"""


def _widget_hardware(t: dict[str, str], mono: str) -> str:
    """微仪表 1：单节点碳基芯片 die 与不可扩展虚线空槽。"""
    cy = t["cyan"]
    tr = t["track"]
    pins = []
    for offset in (-7, 0, 7):
        pins.append(f'<line x1="{58 + offset}" y1="15" x2="{58 + offset}" y2="19" stroke="{cy}" stroke-width="1.2"/>')
        pins.append(f'<line x1="{58 + offset}" y1="45" x2="{58 + offset}" y2="49" stroke="{cy}" stroke-width="1.2"/>')
        pins.append(f'<line x1="39" y1="{32 + offset}" x2="43" y2="{32 + offset}" stroke="{cy}" stroke-width="1.2"/>')
        pins.append(f'<line x1="73" y1="{32 + offset}" x2="77" y2="{32 + offset}" stroke="{cy}" stroke-width="1.2"/>')

    return f"""
      <text x="7" y="12" fill="{t['text_muted']}" font-family="{mono}" font-size="7.2" letter-spacing="0.8">TOPOLOGY // 1N</text>
      <!-- 两侧不可横向扩容的幽灵虚线空节点 -->
      <line x1="25" y1="32" x2="39" y2="32" stroke="{tr}" stroke-width="1.1" stroke-dasharray="2 2"/>
      <line x1="77" y1="32" x2="91" y2="32" stroke="{tr}" stroke-width="1.1" stroke-dasharray="2 2"/>
      <rect x="10" y="24" width="15" height="16" rx="3" fill="none" stroke="{tr}" stroke-width="1.1" stroke-dasharray="3 2"/>
      <path d="M 15 29 L 20 35 M 20 29 L 15 35" stroke="{t['text_muted']}" stroke-width="1.1" stroke-opacity="0.55" stroke-linecap="round"/>
      <rect x="91" y="24" width="15" height="16" rx="3" fill="none" stroke="{tr}" stroke-width="1.1" stroke-dasharray="3 2"/>
      <path d="M 96 29 L 101 35 M 101 29 L 96 35" stroke="{t['text_muted']}" stroke-width="1.1" stroke-opacity="0.55" stroke-linecap="round"/>
      <!-- 中心唯一活跃碳基核心 -->
      {"".join(pins)}
      <rect x="43" y="19" width="30" height="26" rx="5" fill="{cy}" fill-opacity="0.1" stroke="{cy}" stroke-width="1.3"/>
      <g transform="translate(58, 32)">
        <circle class="motion-only" r="5" fill="none" stroke="{cy}" stroke-width="1">
          <animate attributeName="r" values="4.5;11" dur="2.1s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.75;0" dur="2.1s" repeatCount="indefinite"/>
        </circle>
        <circle r="8.5" fill="none" stroke="{cy}" stroke-width="1" stroke-dasharray="3 2.5" stroke-opacity="0.7">
          <animateTransform attributeName="transform" type="rotate" from="360 0 0" to="0 0 0" dur="5.5s" repeatCount="indefinite"/>
        </circle>
        <rect x="-4" y="-4" width="8" height="8" rx="2" fill="{cy}"/>
      </g>
      <text x="58" y="57.5" text-anchor="middle" fill="{t['text_muted']}" font-family="{mono}" font-size="6.8" letter-spacing="0.6">SCALE-OUT: OFF</text>"""


def _widget_power(t: dict[str, str], mono: str, theme_name: str) -> str:
    """微仪表 2：动态流体能量胶囊槽与续航脉冲波纹。"""
    em = t["emerald"]
    cy = t["cyan"]
    am = t["amber"]
    # 周期 84px（大于电池内腔 80px），双周期 168px 保证平移 -84px 时右端永不露缝
    wave_d = (
        "M 0 10 Q 21 6 42 10 T 84 10 Q 105 6 126 10 T 168 10 L 168 30 L 0 30 Z"
    )
    return f"""
      <text x="7" y="12" fill="{t['text_muted']}" font-family="{mono}" font-size="7.2" letter-spacing="0.8">FUEL // CELL</text>
      <circle class="warn-blink" cx="104" cy="10" r="2.2" fill="{am}"/>
      <!-- 电池正极凸起 -->
      <rect x="96" y="25" width="4" height="12" rx="1.5" fill="{t['track']}" stroke="{em}" stroke-width="0.9"/>
      <!-- 内部液面裁剪区 -->
      <g clip-path="url(#power-clip-{theme_name})">
        <rect x="14" y="19" width="80" height="24" fill="{t['track']}" fill-opacity="0.45"/>
        <g transform="translate(14, 21)">
          <path class="wave-flow" d="{wave_d}" fill="url(#power-grad-{theme_name})" fill-opacity="0.88"/>
          <path class="wave-flow-slow" d="{wave_d}" fill="{cy}" fill-opacity="0.28"/>
        </g>
      </g>
      <!-- 外壳描边与中心闪电符号 -->
      <rect x="13" y="18" width="82" height="26" rx="5.5" fill="none" stroke="{em}" stroke-width="1.3"/>
      <path d="M 55.5 23 L 50 32 H 54.5 L 53.2 39 L 59 30 H 54.5 Z" fill="#ffffff" fill-opacity="0.92"/>
      <!-- 底部多段续航状态指示条 -->
      <rect x="14" y="50" width="18" height="3.2" rx="1.5" fill="{am}" fill-opacity="0.85"/>
      <rect x="35" y="50" width="28" height="3.2" rx="1.5" fill="{em}" fill-opacity="0.85"/>
      <rect x="66" y="50" width="28" height="3.2" rx="1.5" fill="{cy}" fill-opacity="0.55"/>"""


def _widget_maintenance(t: dict[str, str], mono: str) -> str:
    """微仪表 3：24 小时昼夜运行与 6-8h 离线记忆清理轨道环表。"""
    cy = t["cyan"]
    ind = t["indigo"]
    tr = t["track"]
    cx, cy_c, r = 58.0, 34.0, 14.5
    circ = 2.0 * math.pi * r
    sleep_arc = circ * (7.0 / 24.0)
    active_arc = circ - sleep_arc
    return f"""
      <text x="7" y="11.5" fill="{t['text_muted']}" font-family="{mono}" font-size="7.2" letter-spacing="0.8">CYCLE // 24H</text>
      <circle cx="{cx:.0f}" cy="{cy_c:.0f}" r="{r:.1f}" fill="none" stroke="{tr}" stroke-width="3.4"/>
      <!-- 日间运行扇区 -->
      <circle cx="{cx:.0f}" cy="{cy_c:.0f}" r="{r:.1f}" fill="none" stroke="{cy}" stroke-width="3.4" stroke-dasharray="{active_arc - 3:.1f} {sleep_arc + 3:.1f}" stroke-dashoffset="0" stroke-linecap="round" transform="rotate(15 {cx:.0f} {cy_c:.0f})" stroke-opacity="0.82"/>
      <!-- 每日 6-8h 离线记忆清理扇区 -->
      <circle cx="{cx:.0f}" cy="{cy_c:.0f}" r="{r:.1f}" fill="none" stroke="{ind}" stroke-width="4.0" stroke-dasharray="{sleep_arc - 2:.1f} {active_arc + 2:.1f}" stroke-linecap="round" transform="rotate(-100 {cx:.0f} {cy_c:.0f})"/>
      <!-- 中心弯月与微星 -->
      <path d="M 60.2 29.6 A 4.4 4.4 0 1 0 63.6 36.6 A 3.4 3.4 0 1 1 60.2 29.6 Z" fill="{ind}"/>
      <circle class="star-twinkle" cx="53.0" cy="30.8" r="0.95" fill="{cy}"/>
      <!-- 顺时针绕 24 小时圆环运行的实时指针光点 -->
      <g class="motion-only" transform="translate({cx:.0f}, {cy_c:.0f})">
        <g>
          <circle cx="{r:.1f}" cy="0" r="3.1" fill="{cy}" fill-opacity="0.3"/>
          <circle cx="{r:.1f}" cy="0" r="1.6" fill="#ffffff"/>
          <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="7.2s" repeatCount="indefinite"/>
        </g>
      </g>
      <text x="58" y="58.5" text-anchor="middle" fill="{t['text_muted']}" font-family="{mono}" font-size="6.8" letter-spacing="0.5">GC: 6–8H</text>"""


def _widget_concurrency(t: dict[str, str], mono: str) -> str:
    """微仪表 4：单线程调度通道与实时抢占中断注入流。"""
    cy = t["cyan"]
    ind = t["indigo"]
    am = t["amber"]
    tr = t["track"]
    return f"""
      <text x="7" y="12" fill="{t['text_muted']}" font-family="{mono}" font-size="7.2" letter-spacing="0.8">EXEC // 1T</text>
      <!-- 常规主任务队列轨道 -->
      <line x1="10" y1="42" x2="106" y2="42" stroke="{tr}" stroke-width="2.2" stroke-linecap="round"/>
      <!-- 上方新想法抢占支路 -->
      <path d="M 10 21 Q 38 21 50 42" fill="none" stroke="{am}" stroke-width="1.3" stroke-dasharray="3 2" stroke-opacity="0.72"/>
      <!-- 主通道执行中的任务块 -->
      <rect class="motion-only" x="-7" y="-3.5" width="14" height="7" rx="2" fill="{ind}" fill-opacity="0.75">
        <animateMotion dur="2.8s" repeatCount="indefinite" path="M 12 42 L 104 42"/>
        <animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.12;0.86;1" dur="2.8s" repeatCount="indefinite"/>
      </rect>
      <!-- 新想法中断脉冲沿支路直接抢占主线程 -->
      <circle class="motion-only" r="3.2" fill="{cy}">
        <animateMotion dur="2.8s" begin="-1.4s" repeatCount="indefinite" path="M 12 21 Q 38 21 50 42 L 104 42"/>
        <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.88;1" dur="2.8s" begin="-1.4s" repeatCount="indefinite"/>
      </circle>
      <!-- 抢占点（50, 42）微闪烁信号环 -->
      <circle class="motion-only" cx="50" cy="42" r="3.6" fill="none" stroke="{am}" stroke-width="1.2">
        <animate attributeName="r" values="3;9" dur="1.4s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.85;0" dur="1.4s" repeatCount="indefinite"/>
      </circle>
      <circle cx="50" cy="42" r="2.2" fill="{am}"/>
      <text x="106" y="23.5" text-anchor="end" fill="{am}" font-family="{mono}" font-size="6.8" letter-spacing="0.4">IRQ PREEMPT</text>
      <text x="58" y="57" text-anchor="middle" fill="{t['text_muted']}" font-family="{mono}" font-size="6.8" letter-spacing="0.4">LOCK: MUTEX-1</text>"""


def _widget_backlog(t: dict[str, str], mono: str) -> str:
    """微仪表 5：单向不可逆提交链与持续爬升待办柱状图。"""
    am = t["amber"]
    rose = t["rose"]
    tr = t["track"]
    bars_cfg = [
        (64, 40, 10, 0.45, ""),
        (73, 35, 15, 0.58, ""),
        (82, 29, 21, 0.72, ""),
        (91, 22, 28, 0.88, " bar-p1"),
        (100, 15, 35, 1.0, " bar-p2"),
    ]
    bars_svg = "".join(
        f'<rect class="{cls.strip()}" x="{bx}" y="{by}" width="6" height="{bh}" rx="1.5" fill="{am}" fill-opacity="{op}"/>'
        for bx, by, bh, op, cls in bars_cfg
    )
    return f"""
      <text x="7" y="12" fill="{t['text_muted']}" font-family="{mono}" font-size="7.2" letter-spacing="0.8">LOG // APPEND</text>
      <!-- 左侧不可逆时间线（只进不退） -->
      <line x1="12" y1="27" x2="50" y2="27" stroke="{am}" stroke-width="1.3" stroke-opacity="0.7"/>
      <circle cx="14" cy="27" r="2.4" fill="{tr}" stroke="{am}" stroke-width="1.1"/>
      <circle cx="30" cy="27" r="2.4" fill="{tr}" stroke="{am}" stroke-width="1.1"/>
      <circle cx="46" cy="27" r="2.8" fill="{am}"/>
      <!-- 禁止回滚标记 -->
      <path d="M 42 38 C 36 33 22 33 17 39" fill="none" stroke="{t['track']}" stroke-width="1.2" stroke-dasharray="2 2"/>
      <path d="M 27 33 L 33 39 M 33 33 L 27 39" stroke="{rose}" stroke-width="1.4" stroke-linecap="round"/>
      <text x="12" y="49" fill="{rose}" font-family="{mono}" font-size="6.8">NO REVERT</text>
      <!-- 右侧爬升待办柱状图 -->
      <line x1="62" y1="51" x2="108" y2="51" stroke="{tr}" stroke-width="1"/>
      {bars_svg}
      <circle class="warn-blink" cx="103" cy="10" r="2.1" fill="{am}"/>"""


def _render_widget_bay(
    kind: str, wx: int, wy: int, accent: str, t: dict[str, str], mono: str, theme_name: str
) -> str:
    """渲染嵌入每张 Bento 卡片右侧的 114x64 独立遥测微仪表视口。"""
    inner_map = {
        "release": lambda: _widget_release(t, mono),
        "hardware": lambda: _widget_hardware(t, mono),
        "power": lambda: _widget_power(t, mono, theme_name),
        "maintenance": lambda: _widget_maintenance(t, mono),
        "concurrency": lambda: _widget_concurrency(t, mono),
        "backlog": lambda: _widget_backlog(t, mono),
    }
    inner = inner_map[kind]()
    return f"""    <g transform="translate({wx}, {wy})">
      <rect x="0" y="0" width="114" height="64" rx="8" fill="{t['bay_bg']}" stroke="{t['bay_border']}" stroke-width="1"/>
      <path d="M 0 10 V 3 Q 0 0 3 0 H 10" fill="none" stroke="{accent}" stroke-width="1.2" stroke-opacity="0.72"/>
      <path d="M 104 64 H 111 Q 114 64 114 61 V 54" fill="none" stroke="{accent}" stroke-width="1.2" stroke-opacity="0.72"/>
      {inner}
    </g>"""


def _render_pcb_bus(t: dict[str, str]) -> str:
    """渲染串联 6 个模块间隙的 PCB 总线走线与脉冲光点。"""
    tr = t["bus_trace"]
    via = t["bus_via"]
    bus_paths = [
        "M 463 46 H 497",
        "M 463 152 H 497",
        "M 463 258 H 497",
        "M 480 46 V 258",
        "M 232 107 V 99 H 474 V 46 H 497",
        "M 728 91 V 99 H 486 V 258 H 463",
    ]
    traces = "".join(
        f'<path d="{d}" fill="none" stroke="{tr}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        for d in bus_paths
    )
    vias = "".join(
        f'<circle cx="{vx}" cy="{vy}" r="2.6" fill="{t["card_bg_end"]}" stroke="{via}" stroke-width="1.2"/>'
        for vx, vy in ((480, 46), (480, 152), (480, 258), (232, 99), (728, 99))
    )

    packets = [
        (t["emerald"], "M 232 107 V 99 H 474 V 46 H 497", "3.4s", "0s"),
        (t["cyan"], "M 728 91 V 99 H 486 V 258 H 463", "3.8s", "-1.2s"),
        (t["indigo"], "M 497 152 H 480 V 46 H 463", "2.9s", "-0.7s"),
        (t["amber"], "M 463 258 H 497", "1.8s", "-0.3s"),
    ]
    packet_svg = "".join(
        f'<g class="motion-only">'
        f'<circle r="4.5" fill="{col}" fill-opacity="0.24">'
        f'<animateMotion dur="{dur}" begin="{beg}" repeatCount="indefinite" path="{path}"/>'
        f"</circle>"
        f'<circle r="2.0" fill="{col}">'
        f'<animateMotion dur="{dur}" begin="{beg}" repeatCount="indefinite" path="{path}"/>'
        f"</circle>"
        f"</g>"
        for col, path, dur, beg in packets
    )

    return f"""  <g>
    {traces}
    {vias}
    {packet_svg}
  </g>"""


def render_spec_svg(theme_name: str) -> str:
    """渲染炫酷动态版 System Spec Bento 架构拓扑与微仪表 SVG。"""
    t = THEMES[theme_name]
    mono = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
    sans = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'PingFang SC', sans-serif"

    card_w = 462
    card_h = 90
    col_gap = 34
    row_gap = 16

    cards_svg: list[str] = []
    for idx, (label, value, desc, color_key, widget_kind) in enumerate(CARDS):
        col = idx % 2
        row = idx // 2
        cx = 1 + col * (card_w + col_gap)
        cy = 1 + row * (card_h + row_gap)
        accent = t[color_key]
        wx = cx + card_w - 126
        wy = cy + 13
        bay_svg = _render_widget_bay(widget_kind, wx, wy, accent, t, mono, theme_name)

        cards_svg.append(
            f"""  <g>
    <rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" rx="12" fill="url(#spec-card-{theme_name})" stroke="{t['border']}" stroke-width="1"/>
    <rect class="spec-edge spec-d{idx}" x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" rx="12" fill="none" stroke="{accent}" stroke-width="1" stroke-opacity="0"/>
    <!-- 左侧装饰强调条 -->
    <rect x="{cx + 1}" y="{cy + 18}" width="2.5" height="54" rx="1.2" fill="{accent}" fill-opacity="0.72"/>
    <circle class="spec-dot spec-d{idx}" cx="{cx + 22}" cy="{cy + 21}" r="3.1" fill="{accent}"/>
    <text x="{cx + 32}" y="{cy + 24.5}" fill="{t['text_muted']}" font-family="{mono}" font-size="10.2" letter-spacing="1.1">{html.escape(label)}</text>
    <text x="{cx + 18}" y="{cy + 50}" fill="{t['text_primary']}" font-family="{sans}" font-size="16.8" font-weight="600">{html.escape(value)}</text>
    <text x="{cx + 18}" y="{cy + 72}" fill="{t['text_secondary']}" font-family="{sans}" font-size="11.8">{html.escape(desc)}</text>
{bay_svg}
  </g>"""
        )

    bus_svg = _render_pcb_bus(t)
    joined_cards = "\n".join(cards_svg)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 304" width="960" height="304" role="img" aria-label="sl251 dynamic system specification architecture ({theme_name})">
  <style>
    @keyframes specDotBreathe {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.42; }}
    }}
    @keyframes specEdgeGlow {{
      0%, 100% {{ stroke-opacity: 0; }}
      50% {{ stroke-opacity: 0.34; }}
    }}
    @keyframes streamDash {{
      0% {{ stroke-dashoffset: 0; }}
      100% {{ stroke-dashoffset: -22; }}
    }}
    @keyframes waveFlow {{
      0% {{ transform: translateX(0); }}
      100% {{ transform: translateX(-84px); }}
    }}
    @keyframes starTwinkle {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.25; }}
    }}
    @keyframes barPulse {{
      0%, 100% {{ fill-opacity: 1; }}
      50% {{ fill-opacity: 0.55; }}
    }}
    @keyframes warnBlink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.22; }}
    }}
    .spec-dot {{ animation: specDotBreathe 3.6s ease-in-out infinite; }}
    .spec-edge {{ animation: specEdgeGlow 4.8s ease-in-out infinite; }}
    .spec-d0 {{ animation-delay: 0s; }}
    .spec-d1 {{ animation-delay: -0.8s; }}
    .spec-d2 {{ animation-delay: -1.6s; }}
    .spec-d3 {{ animation-delay: -2.4s; }}
    .spec-d4 {{ animation-delay: -3.2s; }}
    .spec-d5 {{ animation-delay: -4.0s; }}
    .stream-dash {{ animation: streamDash 1.4s linear infinite; }}
    .wave-flow {{ animation: waveFlow 2.6s linear infinite; }}
    .wave-flow-slow {{ animation: waveFlow 4.2s linear infinite; }}
    .star-twinkle {{ animation: starTwinkle 2.2s ease-in-out infinite; }}
    .bar-p1 {{ animation: barPulse 2.0s ease-in-out infinite; }}
    .bar-p2 {{ animation: barPulse 2.0s ease-in-out -1.0s infinite; }}
    .warn-blink {{ animation: warnBlink 1.8s ease-in-out infinite; }}
    @media (prefers-reduced-motion: reduce) {{
      .spec-dot, .spec-edge, .stream-dash, .wave-flow, .wave-flow-slow,
      .star-twinkle, .bar-p1, .bar-p2, .warn-blink {{ animation: none; }}
      .motion-only {{ display: none; }}
    }}
  </style>
  <defs>
    <linearGradient id="spec-card-{theme_name}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t['card_bg_start']}"/>
      <stop offset="100%" stop-color="{t['card_bg_end']}"/>
    </linearGradient>
    <linearGradient id="power-grad-{theme_name}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{t['cyan']}"/>
      <stop offset="100%" stop-color="{t['emerald']}"/>
    </linearGradient>
    <clipPath id="power-clip-{theme_name}">
      <rect x="14" y="19" width="80" height="24" rx="4.5"/>
    </clipPath>
  </defs>
{bus_svg}
{joined_cards}
</svg>
"""


def main() -> None:
    """生成深浅双色 System Spec Bento 架构遥测 SVG 文件。"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        out_path = ASSETS_DIR / f"spec-{theme}.svg"
        out_path.write_text(render_spec_svg(theme), encoding="utf-8")


if __name__ == "__main__":
    main()

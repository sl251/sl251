#!/usr/bin/env python3
"""生成深浅双色炫酷动态工程评估控制台 SVG（assets/audit-dark.svg 与 audit-light.svg）。

采用“战术轨道雷达 + 20 段流光 LED 遥测柱 + 验证流水线门禁控制台”视觉设计，
全部使用纯声明式 CSS @keyframes 与 SMIL 动画，兼容 GitHub 暗/浅主题与无脚本沙箱。
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

# 与遥测头图及 System Spec 保持一致的深浅双色配色体系
THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "bg_start": "#0d1117",
        "bg_end": "#111926",
        "border": "#263040",
        "grid": "#ffffff",
        "grid_opacity": "0.035",
        "divider": "#212a38",
        "panel_bg": "#080c12",
        "panel_bg_opacity": "0.82",
        "panel_border": "#1f2937",
        "track_bg": "#0c131d",
        "text_primary": "#f0f6fc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "ring": "#243246",
        "accent_start": "#38bdf8",
        "accent_end": "#34d399",
        "warn": "#f59e0b",
        "seg_off": "#162030",
        "gate_pass_bg": "#09251e",
        "gate_pass_border": "#10b981",
        "gate_pass_text": "#6ee7b7",
        "gate_fail_bg": "#101722",
        "gate_fail_border": "#2b384b",
        "gate_fail_text": "#64748b",
    },
    "light": {
        "bg_start": "#ffffff",
        "bg_end": "#f4f7fb",
        "border": "#d0d7de",
        "grid": "#0f172a",
        "grid_opacity": "0.035",
        "divider": "#e2e8f0",
        "panel_bg": "#edf2f7",
        "panel_bg_opacity": "0.78",
        "panel_border": "#d8dee4",
        "track_bg": "#e3eaf3",
        "text_primary": "#1f2328",
        "text_secondary": "#57606a",
        "text_muted": "#6e7781",
        "ring": "#cbd5e1",
        "accent_start": "#0284c7",
        "accent_end": "#059669",
        "warn": "#d97706",
        "seg_off": "#d5dde8",
        "gate_pass_bg": "#ecfdf5",
        "gate_pass_border": "#10b981",
        "gate_pass_text": "#047857",
        "gate_fail_bg": "#f6f8fa",
        "gate_fail_border": "#cbd5e1",
        "gate_fail_text": "#6e7781",
    },
}

# 五维评估指标：(中文标签, 英文雷达轴, 评级文本, 分值 0-1, 亮起微段数 /20, 配色类别)
METRICS = [
    ("热更新机制", "HOT-PATCH", "A", 0.92, 18, "good"),
    ("流程自动化", "AUTOMATION", "HIGH", 0.88, 18, "good"),
    ("服务可用性", "AVAILABILITY", "BETA", 0.62, 12, "mid"),
    ("范围收敛度", "SCOPE CTRL", "D+", 0.36, 7, "warn"),
    ("文档覆盖率", "DOCS", "C-", 0.45, 9, "warn"),
]

# 5 项生产就绪门禁：(短标签, 是否通过)
GATES = [
    ("冷启动", True),
    ("异常自愈", True),
    ("持续集成", True),
    ("全量文档", False),
    ("GA / LTS", False),
]


def polygon_points(cx: float, cy: float, radius: float, ratios: list[float]) -> str:
    """按五边形顺时针顶点计算雷达多边形坐标字符串。"""
    pts: list[str] = []
    for idx, ratio in enumerate(ratios):
        angle = math.radians(-90 + idx * 72)
        px = cx + radius * ratio * math.cos(angle)
        py = cy + radius * ratio * math.sin(angle)
        pts.append(f"{px:.1f},{py:.1f}")
    return " ".join(pts)


def closed_polygon_path(cx: float, cy: float, radius: float, ratios: list[float]) -> str:
    """生成闭合的多边形 path 字符串（用于激光描边扫掠动画）。"""
    coords: list[str] = []
    for idx, ratio in enumerate(ratios):
        angle = math.radians(-90 + idx * 72)
        px = cx + radius * ratio * math.cos(angle)
        py = cy + radius * ratio * math.sin(angle)
        cmd = "M" if idx == 0 else "L"
        coords.append(f"{cmd} {px:.1f} {py:.1f}")
    coords.append("Z")
    return " ".join(coords)


def _render_radar_section(t: dict[str, str], theme_name: str, mono: str, sans: str) -> tuple[str, str, str, str, str, str, str]:
    """构建左侧战术雷达与轨道刻度环 SVG 元素。"""
    cx, cy, radius = 222.0, 186.0, 62.0
    outer_r = 70.0

    # 1. 五层同心正五边形网格与径向刻度线
    rings_svg: list[str] = []
    for level in (0.2, 0.4, 0.6, 0.8, 1.0):
        pts = polygon_points(cx, cy, radius, [level] * 5)
        dash = ' stroke-dasharray="2 2"' if level in (0.4, 0.8) else ""
        rings_svg.append(
            f'<polygon points="{pts}" fill="none" stroke="{t["ring"]}" stroke-width="1"{dash}/>'
        )
    for idx in range(5):
        angle = math.radians(-90 + idx * 72)
        x2 = cx + radius * math.cos(angle)
        y2 = cy + radius * math.sin(angle)
        rings_svg.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["ring"]}" stroke-width="1"/>'
        )

    # 外圈战术罗盘刻度环（细虚线顺时针慢转 + 内侧对称弧段逆时针慢转）
    compass_ticks: list[str] = []
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        r1 = outer_r + 1.5
        r2 = outer_r + (4.2 if deg % 90 == 0 else 2.6)
        x1, y1 = cx + r1 * math.cos(rad), cy + r1 * math.sin(rad)
        x2, y2 = cx + r2 * math.cos(rad), cy + r2 * math.sin(rad)
        compass_ticks.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["ring"]}" stroke-width="1"/>'
        )
    compass_svg = (
        f'<g>{"".join(compass_ticks)}</g>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{outer_r:.1f}" fill="none" stroke="{t["accent_start"]}" stroke-opacity="0.28" stroke-width="1" stroke-dasharray="6 4 2 4">'
        f'<animateTransform class="smil-anim" attributeName="transform" type="rotate" from="0 {cx:.1f} {cy:.1f}" to="360 {cx:.1f} {cy:.1f}" dur="26s" repeatCount="indefinite"/>'
        f'</circle>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{outer_r - 3.5:.1f}" fill="none" stroke="{t["accent_end"]}" stroke-opacity="0.22" stroke-width="1.2" stroke-dasharray="28 82">'
        f'<animateTransform class="smil-anim" attributeName="transform" type="rotate" from="360 {cx:.1f} {cy:.1f}" to="0 {cx:.1f} {cy:.1f}" dur="14s" repeatCount="indefinite"/>'
        f'</circle>'
    )

    # 2. 数据多边形、边沿激光扫掠路径、顶点标靶与同步雷达锁定脉冲
    data_ratios = [m[3] for m in METRICS]
    data_pts = polygon_points(cx, cy, radius, data_ratios)
    data_path_d = closed_polygon_path(cx, cy, radius, data_ratios)
    outer_pts = polygon_points(cx, cy, radius, [1.0] * 5)

    dots_svg: list[str] = []
    for idx, ratio in enumerate(data_ratios):
        angle = math.radians(-90 + idx * 72)
        px = cx + radius * ratio * math.cos(angle)
        py = cy + radius * ratio * math.sin(angle)
        # 与 5.0s 雷达扫描臂经过各顶点（每 1.0s 一轴）同步触发脉冲锁定圈
        dots_svg.append(
            f'<circle class="motion-only" cx="{px:.1f}" cy="{py:.1f}" r="3.0" fill="none" stroke="{t["accent_end"]}" stroke-width="1.3" stroke-opacity="0">'
            f'<animate attributeName="r" values="3;10.5;10.5" keyTimes="0;0.28;1" dur="5.0s" begin="{idx * 1.0:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="stroke-opacity" values="0.82;0;0" keyTimes="0;0.28;1" dur="5.0s" begin="{idx * 1.0:.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
        dots_svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.1" fill="{t["accent_end"]}"/>'
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.1" fill="#ffffff"/>'
        )

    # 雷达顺时针扫掠扇形（-136° 到 -90°，46° 扇区）
    sweep_r = radius + 4.0
    tx = cx + sweep_r * math.cos(math.radians(-136))
    ty = cy + sweep_r * math.sin(math.radians(-136))
    lx = cx
    ly = cy - sweep_r
    sweep_d = f"M {cx:.1f} {cy:.1f} L {tx:.2f} {ty:.2f} A {sweep_r:.1f} {sweep_r:.1f} 0 0 1 {lx:.2f} {ly:.2f} Z"
    gx1 = cx + (radius * 0.65) * math.cos(math.radians(-136))
    gy1 = cy + (radius * 0.65) * math.sin(math.radians(-136))
    gx2 = cx
    gy2 = cy - (radius * 0.65)

    # 3. 外部中文标签（精确避开罗盘外缘与面板边线）
    vertex_labels = [
        (222.0, 104.0, "middle", f"{METRICS[0][0]} · {METRICS[0][2]}"),
        (303.0, 165.0, "start", f"{METRICS[1][0]} · {METRICS[1][2]}"),
        (274.0, 268.0, "start", f"{METRICS[2][0]} · {METRICS[2][2]}"),
        (170.0, 268.0, "end", f"{METRICS[3][0]} · {METRICS[3][2]}"),
        (141.0, 165.0, "end", f"{METRICS[4][0]} · {METRICS[4][2]}"),
    ]
    labels_svg = [
        f'<text x="{vx:.1f}" y="{vy:.1f}" text-anchor="{anchor}" fill="{t["text_secondary"]}" '
        f'font-family="{sans}" font-size="11" letter-spacing="0.2">{label}</text>'
        for vx, vy, anchor, label in vertex_labels
    ]

    radar_body = f"""  {compass_svg}
  {"".join(rings_svg)}
  <g class="motion-only" clip-path="url(#radar-clip-{theme_name})">
    <g>
      <path d="{sweep_d}" fill="url(#radar-sweep-{theme_name})"/>
      <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{lx:.2f}" y2="{ly:.2f}" stroke="{t['accent_end']}" stroke-opacity="0.72" stroke-width="1.3"/>
      <animateTransform attributeName="transform" type="rotate" from="0 {cx:.1f} {cy:.1f}" to="360 {cx:.1f} {cy:.1f}" dur="5.0s" repeatCount="indefinite"/>
    </g>
  </g>
  <polygon class="radar-core" points="{data_pts}" fill="url(#radar-fill-{theme_name})" stroke="url(#radar-stroke-{theme_name})" stroke-opacity="0.45" stroke-width="1.8" stroke-linejoin="round"/>
  <path class="radar-edge-sweep" d="{data_path_d}" pathLength="1000" fill="none" stroke="url(#radar-stroke-{theme_name})" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>
  {"".join(dots_svg)}
  {"".join(labels_svg)}"""

    return (
        radar_body,
        outer_pts,
        sweep_d,
        f"{gx1:.1f}",
        f"{gy1:.1f}",
        f"{gx2:.1f}",
        f"{gy2:.1f}",
    )


def render_audit_svg(theme_name: str) -> str:
    """渲染指定配色的工程评估动态控制台 SVG。"""
    t = THEMES[theme_name]
    mono = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
    sans = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'PingFang SC', sans-serif"

    radar_body, outer_pts, _sweep_d, gx1, gy1, gx2, gy2 = _render_radar_section(
        t, theme_name, mono, sans
    )
    idx_score = sum(m[3] for m in METRICS) / len(METRICS) * 100.0

    # 右侧 20 段精细 LED 遥测条（按固定顺序展示）
    display_order = [2, 4, 0, 3, 1]  # 可用性、文档、热更新、范围收敛、流程自动化
    bars_svg: list[str] = []
    for row_idx, m_idx in enumerate(display_order):
        cn_name, _en, grade, _ratio, lit_segs, level_kind = METRICS[m_idx]
        y_row = 111 + row_idx * 24
        active_color = (
            t["accent_end"]
            if level_kind == "good"
            else (t["accent_start"] if level_kind == "mid" else t["warn"])
        )
        bars_svg.append(
            f'<text x="448" y="{y_row}" fill="{t["text_primary"]}" font-family="{sans}" font-size="11.8">{cn_name}</text>'
        )
        # 20 段 LED 底槽边框
        bars_svg.append(
            f'<rect x="529" y="{y_row - 11}" width="283" height="14" rx="3.5" fill="{t["track_bg"]}" stroke="{t["panel_border"]}" stroke-width="0.8"/>'
        )
        for s in range(20):
            sx = 533 + s * 14
            is_lit = s < lit_segs
            fill = active_color if is_lit else t["seg_off"]
            if not is_lit:
                bars_svg.append(
                    f'<rect x="{sx}" y="{y_row - 8.5}" width="10" height="9" rx="1.6" fill="{fill}" fill-opacity="0.72"/>'
                )
            else:
                # 亮起 LED 段按列叠加流水波纹，末格增加峰值保持闪烁
                is_tip = s == lit_segs - 1
                delay = -(s * 0.09 + row_idx * 0.28)
                cls = "led-tip" if is_tip else "led-flow"
                bars_svg.append(
                    f'<rect class="{cls}" style="animation-delay:{delay:.2f}s" x="{sx}" y="{y_row - 8.5}" width="10" height="9" rx="1.6" fill="{fill}"/>'
                )
        # 右侧评级胶囊徽章
        bars_svg.append(
            f'<rect x="852" y="{y_row - 11.5}" width="64" height="15" rx="4" fill="{active_color}" fill-opacity="0.12" stroke="{active_color}" stroke-opacity="0.45" stroke-width="0.8"/>'
        )
        bars_svg.append(
            f'<text x="884" y="{y_row - 0.5}" text-anchor="middle" fill="{active_color}" font-family="{mono}" font-size="10.5" font-weight="600">{grade}</text>'
        )

    # 右下角验证流水线门禁胶囊（顶部总线导轨 + 垂直分接头 + 阻塞校验光点）
    gates_svg: list[str] = [
        f'<line x1="539" y1="240" x2="875" y2="240" stroke="{t["ring"]}" stroke-width="1.5" stroke-dasharray="3 2"/>',
        f'<line x1="539" y1="240" x2="748" y2="240" stroke="{t["accent_end"]}" stroke-width="1.6" stroke-opacity="0.72"/>',
        f'<line x1="748" y1="236.5" x2="748" y2="243.5" stroke="{t["warn"]}" stroke-width="1.4" stroke-linecap="round"/>',
    ]

    for g_idx, (g_label, passed) in enumerate(GATES):
        gx = 500 + g_idx * 84
        g_cx = gx + 39
        tap_col = t["accent_end"] if passed else t["ring"]
        gates_svg.append(
            f'<line x1="{g_cx}" y1="240" x2="{g_cx}" y2="248" stroke="{tap_col}" stroke-width="1.3" stroke-opacity="0.75"/>'
        )
        bg = t["gate_pass_bg"] if passed else t["gate_fail_bg"]
        bd = t["gate_pass_border"] if passed else t["gate_fail_border"]
        tx = t["gate_pass_text"] if passed else t["gate_fail_text"]
        mark = "✓" if passed else "·"
        dash = "" if passed else ' stroke-dasharray="3 2"'
        gates_svg.append(
            f'<rect x="{gx}" y="248" width="78" height="24" rx="5.5" fill="{bg}" stroke="{bd}" stroke-width="1"{dash}/>'
        )
        if not passed and g_idx == 3:
            # 下一项待攻克门禁（全量文档）旁点缀微弱琥珀色阻塞提示灯
            gates_svg.append(
                f'<circle class="gate-wait" cx="{gx + 10}" cy="260" r="2.1" fill="{t["warn"]}"/>'
            )
            gates_svg.append(
                f'<text x="{gx + 43}" y="263.5" text-anchor="middle" fill="{tx}" font-family="{sans}" font-size="10.5">{g_label}</text>'
            )
        else:
            gates_svg.append(
                f'<text x="{gx + 39}" y="263.5" text-anchor="middle" fill="{tx}" font-family="{sans}" font-size="10.5">{mark} {g_label}</text>'
            )

    # 流水线校验信号包：在顶部导轨（y=240）沿通过段滑动，并在第 4 门禁阻塞栅前停止，不遮挡胶囊文字
    gate_probe_svg = f"""  <g class="motion-only">
    <circle r="4.0" fill="{t['accent_end']}" fill-opacity="0.28">
      <animateMotion dur="2.6s" repeatCount="indefinite" path="M 539 240 L 746 240"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.82;1" dur="2.6s" repeatCount="indefinite"/>
    </circle>
    <circle r="1.9" fill="{t['accent_end']}">
      <animateMotion dur="2.6s" repeatCount="indefinite" path="M 539 240 L 746 240"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.82;1" dur="2.6s" repeatCount="indefinite"/>
    </circle>
  </g>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 304" width="960" height="304" role="img" aria-label="sl251 dynamic engineering audit console ({theme_name})">
  <style>
    @keyframes radarEdgeSweep {{
      0% {{ stroke-dashoffset: 1000; }}
      100% {{ stroke-dashoffset: 0; }}
    }}
    @keyframes radarCoreBreathe {{
      0%, 100% {{ fill-opacity: 1; }}
      50% {{ fill-opacity: 0.58; }}
    }}
    @keyframes ledFlow {{
      0%, 100% {{ fill-opacity: 0.96; }}
      50% {{ fill-opacity: 0.52; }}
    }}
    @keyframes ledTipPulse {{
      0%, 100% {{ fill-opacity: 1; }}
      50% {{ fill-opacity: 0.30; }}
    }}
    @keyframes gateWaitBlink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.2; }}
    }}
    @keyframes dividerScan {{
      0% {{ transform: translateX(28px); opacity: 0; }}
      15% {{ opacity: 0.85; }}
      85% {{ opacity: 0.85; }}
      100% {{ transform: translateX(852px); opacity: 0; }}
    }}
    .radar-edge-sweep {{
      stroke-dasharray: 220 780;
      animation: radarEdgeSweep 4.2s linear infinite;
    }}
    .radar-core {{ animation: radarCoreBreathe 4.0s ease-in-out infinite; }}
    .led-flow {{ animation: ledFlow 2.6s ease-in-out infinite; }}
    .led-tip {{ animation: ledTipPulse 1.5s ease-in-out infinite; }}
    .gate-wait {{ animation: gateWaitBlink 1.8s ease-in-out infinite; }}
    .divider-scan {{ animation: dividerScan 4.8s ease-in-out infinite; }}
    @media (prefers-reduced-motion: reduce) {{
      .radar-edge-sweep {{ animation: none; stroke-dasharray: none; }}
      .radar-core, .led-flow, .led-tip, .gate-wait, .divider-scan {{ animation: none; }}
      .motion-only {{ display: none; }}
    }}
  </style>
  <defs>
    <linearGradient id="audit-bg-{theme_name}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t['bg_start']}"/>
      <stop offset="100%" stop-color="{t['bg_end']}"/>
    </linearGradient>
    <linearGradient id="radar-stroke-{theme_name}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t['accent_start']}"/>
      <stop offset="100%" stop-color="{t['accent_end']}"/>
    </linearGradient>
    <linearGradient id="radar-fill-{theme_name}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t['accent_start']}" stop-opacity="0.24"/>
      <stop offset="100%" stop-color="{t['accent_end']}" stop-opacity="0.16"/>
    </linearGradient>
    <linearGradient id="radar-sweep-{theme_name}" gradientUnits="userSpaceOnUse" x1="{gx1}" y1="{gy1}" x2="{gx2}" y2="{gy2}">
      <stop offset="0%" stop-color="{t['accent_end']}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{t['accent_end']}" stop-opacity="0.34"/>
    </linearGradient>
    <linearGradient id="scan-beam-{theme_name}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{t['accent_start']}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{t['accent_end']}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{t['accent_start']}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="audit-grid-{theme_name}" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M 32 0 L 0 0 0 32" fill="none" stroke="{t['grid']}" stroke-opacity="{t['grid_opacity']}" stroke-width="1"/>
    </pattern>
    <clipPath id="audit-clip-{theme_name}">
      <rect x="1" y="1" width="958" height="302" rx="14"/>
    </clipPath>
    <clipPath id="radar-clip-{theme_name}">
      <polygon points="{outer_pts}"/>
    </clipPath>
  </defs>

  <g clip-path="url(#audit-clip-{theme_name})">
    <rect x="1" y="1" width="958" height="302" rx="14" fill="url(#audit-bg-{theme_name})"/>
    <rect x="1" y="1" width="958" height="302" fill="url(#audit-grid-{theme_name})"/>
  </g>
  <rect x="1" y="1" width="958" height="302" rx="14" fill="none" stroke="{t['border']}" stroke-width="1"/>

  <!-- 顶部标题条与流光扫描分割线 -->
  <circle cx="34" cy="30" r="7.5" fill="{t['accent_end']}" fill-opacity="0.18"/>
  <circle class="motion-only" cx="34" cy="30" r="3.6" fill="none" stroke="{t['accent_end']}" stroke-width="1.3" stroke-opacity="0.72">
    <animate attributeName="r" values="3.6;11.5" dur="2.6s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values="0.72;0" dur="2.6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="34" cy="30" r="3.6" fill="{t['accent_end']}"/>
  <text x="50" y="34" fill="{t['text_secondary']}" font-family="{mono}" font-size="11.5" letter-spacing="1.4">SL251 // ENGINEERING AUDIT</text>
  <text x="928" y="34" text-anchor="end" fill="{t['text_muted']}" font-family="{mono}" font-size="11" letter-spacing="0.9">PUBLIC PREVIEW · READINESS 3 / 5 GATES</text>
  <line x1="28" y1="50" x2="932" y2="50" stroke="{t['divider']}" stroke-width="1"/>
  <rect class="motion-only divider-scan" x="0" y="49.2" width="80" height="1.6" rx="0.8" fill="url(#scan-beam-{theme_name})"/>

  <!-- 面板间遥测总线桥接 -->
  <line x1="416" y1="145" x2="432" y2="145" stroke="{t['divider']}" stroke-width="1.5"/>
  <line x1="416" y1="205" x2="432" y2="205" stroke="{t['divider']}" stroke-width="1.5"/>
  <g class="motion-only">
    <circle r="2.2" fill="{t['accent_start']}">
      <animateMotion dur="1.6s" repeatCount="indefinite" path="M 416 145 L 432 145"/>
    </circle>
    <circle r="2.2" fill="{t['accent_end']}">
      <animateMotion dur="1.6s" begin="-0.8s" repeatCount="indefinite" path="M 416 205 L 432 205"/>
    </circle>
  </g>

  <!-- 左侧战术能力雷达面板（带 HUD 边角修饰） -->
  <rect x="28" y="64" width="388" height="222" rx="10" fill="{t['panel_bg']}" fill-opacity="{t['panel_bg_opacity']}" stroke="{t['panel_border']}" stroke-width="1"/>
  <path d="M 28 76 V 67 Q 28 64 31 64 H 40" fill="none" stroke="{t['accent_end']}" stroke-width="1.3" stroke-opacity="0.7"/>
  <path d="M 404 286 H 413 Q 416 286 416 283 V 274" fill="none" stroke="{t['accent_start']}" stroke-width="1.3" stroke-opacity="0.7"/>
  <text x="44" y="83" fill="{t['text_muted']}" font-family="{mono}" font-size="10.2" letter-spacing="1.1">CAPABILITY RADAR</text>
  <rect x="336" y="72" width="64" height="16" rx="4" fill="{t['accent_end']}" fill-opacity="0.12" stroke="{t['accent_end']}" stroke-opacity="0.4" stroke-width="0.8"/>
  <text x="368" y="83.2" text-anchor="middle" fill="{t['accent_end']}" font-family="{mono}" font-size="9" letter-spacing="0.6">IDX {idx_score:.1f}</text>
{radar_body}

  <!-- 右侧 20 段流光 LED 条与生产就绪流水线面板 -->
  <rect x="432" y="64" width="500" height="222" rx="10" fill="{t['panel_bg']}" fill-opacity="{t['panel_bg_opacity']}" stroke="{t['panel_border']}" stroke-width="1"/>
  <path d="M 432 76 V 67 Q 432 64 435 64 H 444" fill="none" stroke="{t['accent_start']}" stroke-width="1.3" stroke-opacity="0.7"/>
  <path d="M 920 286 H 929 Q 932 286 932 283 V 274" fill="none" stroke="{t['accent_end']}" stroke-width="1.3" stroke-opacity="0.7"/>
  <text x="448" y="83" fill="{t['text_muted']}" font-family="{mono}" font-size="10.2" letter-spacing="1.1">AUDIT METRICS</text>
  <text x="916" y="83" text-anchor="end" fill="{t['text_muted']}" font-family="{mono}" font-size="10.2" letter-spacing="0.8">20-SEG LED · SCALE D — A</text>
  {"".join(bars_svg)}

  <line x1="448" y1="231" x2="916" y2="231" stroke="{t['divider']}" stroke-width="1"/>
  <text x="448" y="263.5" fill="{t['text_muted']}" font-family="{mono}" font-size="10.2" letter-spacing="1.0">GATES</text>
  {"".join(gates_svg)}
{gate_probe_svg}
</svg>
"""


def main() -> None:
    """生成深浅双色工程评估动态控制台 SVG 文件。"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        out_path = ASSETS_DIR / f"audit-{theme}.svg"
        out_path.write_text(render_audit_svg(theme), encoding="utf-8")


if __name__ == "__main__":
    main()

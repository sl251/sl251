#!/usr/bin/env python3
"""生成深浅双色自托管工程评估可视化 SVG（assets/audit-dark.svg 与 audit-light.svg）。"""

from __future__ import annotations

import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

# 与遥测头图保持一致的深浅双色配色体系
THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "bg_start": "#0d1117",
        "bg_end": "#111926",
        "border": "#263040",
        "grid": "#ffffff",
        "grid_opacity": "0.035",
        "divider": "#212a38",
        "panel_bg": "#080c12",
        "panel_bg_opacity": "0.78",
        "panel_border": "#1f2937",
        "text_primary": "#f0f6fc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "ring": "#263244",
        "accent_start": "#38bdf8",
        "accent_end": "#34d399",
        "warn": "#f59e0b",
        "seg_off": "#17202e",
        "gate_pass_bg": "#0b2922",
        "gate_pass_border": "#10b981",
        "gate_pass_text": "#6ee7b7",
        "gate_fail_bg": "#111824",
        "gate_fail_border": "#283446",
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
        "panel_bg_opacity": "0.75",
        "panel_border": "#d8dee4",
        "text_primary": "#1f2328",
        "text_secondary": "#57606a",
        "text_muted": "#6e7781",
        "ring": "#cbd5e1",
        "accent_start": "#0284c7",
        "accent_end": "#059669",
        "warn": "#d97706",
        "seg_off": "#dde4ed",
        "gate_pass_bg": "#ecfdf5",
        "gate_pass_border": "#10b981",
        "gate_pass_text": "#047857",
        "gate_fail_bg": "#f6f8fa",
        "gate_fail_border": "#d0d7de",
        "gate_fail_text": "#6e7781",
    },
}

# 五维评估指标：(中文标签, 英文雷达轴, 评级文本, 分值 0-1, 亮起格数 /10, 配色类别)
METRICS = [
    ("热更新机制", "HOT-PATCH", "A", 0.92, 9, "good"),
    ("流程自动化", "AUTOMATION", "HIGH", 0.88, 9, "good"),
    ("服务可用性", "AVAILABILITY", "BETA", 0.62, 6, "mid"),
    ("范围收敛度", "SCOPE CTRL", "D+", 0.36, 4, "warn"),
    ("文档覆盖率", "DOCS", "C-", 0.45, 5, "warn"),
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


def render_audit_svg(theme_name: str) -> str:
    """渲染指定配色的工程评估可视化卡片 SVG。"""
    t = THEMES[theme_name]
    mono = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
    sans = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'PingFang SC', sans-serif"

    cx, cy, radius = 222.0, 186.0, 68.0

    # 1. 五层同心正五边形网格与轴线
    rings_svg: list[str] = []
    for level in (0.2, 0.4, 0.6, 0.8, 1.0):
        pts = polygon_points(cx, cy, radius, [level] * 5)
        rings_svg.append(
            f'<polygon points="{pts}" fill="none" stroke="{t["ring"]}" stroke-width="1"/>'
        )
    for idx in range(5):
        angle = math.radians(-90 + idx * 72)
        x2 = cx + radius * math.cos(angle)
        y2 = cy + radius * math.sin(angle)
        rings_svg.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["ring"]}" stroke-width="1"/>'
        )

    # 2. 数据多边形与顶点圆点
    data_ratios = [m[3] for m in METRICS]
    data_pts = polygon_points(cx, cy, radius, data_ratios)
    dots_svg: list[str] = []
    for idx, ratio in enumerate(data_ratios):
        angle = math.radians(-90 + idx * 72)
        px = cx + radius * ratio * math.cos(angle)
        py = cy + radius * ratio * math.sin(angle)
        dots_svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.0" fill="{t["accent_end"]}"/>'
        )

    # 3. 雷达轴外部标签（精确避开图形边界）
    vertex_labels = [
        (222.0, 106.0, "middle", f"{METRICS[0][1]} · {METRICS[0][2]}"),
        (300.0, 166.0, "start", f"{METRICS[1][1]} · {METRICS[1][2]}"),
        (270.0, 260.0, "start", f"{METRICS[2][1]} · {METRICS[2][2]}"),
        (174.0, 260.0, "end", f"{METRICS[3][1]} · {METRICS[3][2]}"),
        (144.0, 166.0, "end", f"{METRICS[4][1]} · {METRICS[4][2]}"),
    ]
    labels_svg: list[str] = []
    for lx, ly, anchor, text in vertex_labels:
        labels_svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="{t["text_secondary"]}" '
            f'font-family="{mono}" font-size="10.2" letter-spacing="0.5">{text}</text>'
        )

    # 4. 右侧分段式审计评分条（按固定顺序展示）
    display_order = [2, 4, 0, 3, 1]  # 可用性、文档、热更新、范围收敛、流程自动化
    bars_svg: list[str] = []
    for row_idx, m_idx in enumerate(display_order):
        cn_name, _en, grade, _ratio, segs, level_kind = METRICS[m_idx]
        y_row = 112 + row_idx * 25
        active_color = (
            t["accent_end"]
            if level_kind == "good"
            else (t["accent_start"] if level_kind == "mid" else t["warn"])
        )
        bars_svg.append(
            f'<text x="448" y="{y_row}" fill="{t["text_primary"]}" font-family="{sans}" font-size="12">{cn_name}</text>'
        )
        for s in range(10):
            sx = 542 + s * 30
            fill = active_color if s < segs else t["seg_off"]
            opacity = "0.92" if s < segs else "1"
            bars_svg.append(
                f'<rect x="{sx}" y="{y_row - 9}" width="25" height="9" rx="2" fill="{fill}" fill-opacity="{opacity}"/>'
            )
        bars_svg.append(
            f'<text x="916" y="{y_row}" text-anchor="end" fill="{active_color}" font-family="{mono}" font-size="11.5" font-weight="600">{grade}</text>'
        )

    # 5. 右下角生产就绪门禁胶囊
    gates_svg: list[str] = []
    for g_idx, (g_label, passed) in enumerate(GATES):
        gx = 502 + g_idx * 84
        bg = t["gate_pass_bg"] if passed else t["gate_fail_bg"]
        bd = t["gate_pass_border"] if passed else t["gate_fail_border"]
        tx = t["gate_pass_text"] if passed else t["gate_fail_text"]
        mark = "✓" if passed else "·"
        dash = "" if passed else ' stroke-dasharray="3 2"'
        gates_svg.append(
            f'<rect x="{gx}" y="250" width="78" height="24" rx="5" fill="{bg}" stroke="{bd}" stroke-width="1"{dash}/>'
        )
        gates_svg.append(
            f'<text x="{gx + 39}" y="266" text-anchor="middle" fill="{tx}" font-family="{sans}" font-size="10.8">{mark} {g_label}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 304" width="960" height="304" role="img" aria-label="sl251 engineering audit chart ({theme_name})">
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
    <pattern id="audit-grid-{theme_name}" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M 32 0 L 0 0 0 32" fill="none" stroke="{t['grid']}" stroke-opacity="{t['grid_opacity']}" stroke-width="1"/>
    </pattern>
    <clipPath id="audit-clip-{theme_name}">
      <rect x="1" y="1" width="958" height="302" rx="14"/>
    </clipPath>
  </defs>

  <g clip-path="url(#audit-clip-{theme_name})">
    <rect x="1" y="1" width="958" height="302" rx="14" fill="url(#audit-bg-{theme_name})"/>
    <rect x="1" y="1" width="958" height="302" fill="url(#audit-grid-{theme_name})"/>
  </g>
  <rect x="1" y="1" width="958" height="302" rx="14" fill="none" stroke="{t['border']}" stroke-width="1"/>

  <!-- 顶部标题条 -->
  <circle cx="34" cy="30" r="7.5" fill="{t['accent_end']}" fill-opacity="0.18"/>
  <circle cx="34" cy="30" r="3.6" fill="{t['accent_end']}"/>
  <text x="50" y="34" fill="{t['text_secondary']}" font-family="{mono}" font-size="11.5" letter-spacing="1.4">SL251 // ENGINEERING AUDIT</text>
  <text x="928" y="34" text-anchor="end" fill="{t['text_muted']}" font-family="{mono}" font-size="11" letter-spacing="0.9">PUBLIC PREVIEW · READINESS 3 / 5 GATES</text>
  <line x1="28" y1="50" x2="932" y2="50" stroke="{t['divider']}" stroke-width="1"/>

  <!-- 左侧五维能力雷达面板 -->
  <rect x="28" y="64" width="388" height="222" rx="10" fill="{t['panel_bg']}" fill-opacity="{t['panel_bg_opacity']}" stroke="{t['panel_border']}" stroke-width="1"/>
  <text x="44" y="84" fill="{t['text_muted']}" font-family="{mono}" font-size="10.5" letter-spacing="1.1">CAPABILITY RADAR</text>
  {"".join(rings_svg)}
  <polygon points="{data_pts}" fill="url(#radar-fill-{theme_name})" stroke="url(#radar-stroke-{theme_name})" stroke-width="2" stroke-linejoin="round"/>
  {"".join(dots_svg)}
  {"".join(labels_svg)}

  <!-- 右侧分段条形评分与门禁面板 -->
  <rect x="432" y="64" width="500" height="222" rx="10" fill="{t['panel_bg']}" fill-opacity="{t['panel_bg_opacity']}" stroke="{t['panel_border']}" stroke-width="1"/>
  <text x="448" y="84" fill="{t['text_muted']}" font-family="{mono}" font-size="10.5" letter-spacing="1.1">AUDIT METRICS</text>
  <text x="916" y="84" text-anchor="end" fill="{t['text_muted']}" font-family="{mono}" font-size="10.5" letter-spacing="0.8">SCALE D — A</text>
  {"".join(bars_svg)}

  <line x1="448" y1="234" x2="916" y2="234" stroke="{t['divider']}" stroke-width="1"/>
  <text x="448" y="266" fill="{t['text_muted']}" font-family="{mono}" font-size="10.5" letter-spacing="1.0">GATES</text>
  {"".join(gates_svg)}
</svg>
"""


def main() -> None:
    """生成深浅双色工程评估图表 SVG 文件。"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        out_path = ASSETS_DIR / f"audit-{theme}.svg"
        out_path.write_text(render_audit_svg(theme), encoding="utf-8")


if __name__ == "__main__":
    main()

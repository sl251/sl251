#!/usr/bin/env python3
"""生成深浅双色自托管 System Spec Bento 卡片网格 SVG（assets/spec-dark.svg 与 spec-light.svg）。"""

from __future__ import annotations

import html
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

# 与遥测头图及审计图保持一致的深浅配色体系
THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "card_bg_start": "#0f151e",
        "card_bg_end": "#0b1017",
        "border": "#242e3e",
        "text_primary": "#f0f6fc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "cyan": "#38bdf8",
        "emerald": "#34d399",
        "amber": "#f59e0b",
    },
    "light": {
        "card_bg_start": "#ffffff",
        "card_bg_end": "#f6f8fa",
        "border": "#d0d7de",
        "text_primary": "#1f2328",
        "text_secondary": "#57606a",
        "text_muted": "#6e7781",
        "cyan": "#0284c7",
        "emerald": "#059669",
        "amber": "#d97706",
    },
}

# 6 张 Bento 规格卡片：(标签, 主值, 中文说明, 强调色键名, 右上角 16x16 线条图标路径)
CARDS = [
    (
        "RELEASE & ACCESS",
        "Public Preview · Read-Only",
        "持续滚动更新，核心实例不接受外部 PR",
        "emerald",
        '<circle cx="8" cy="8" r="5" fill="none" stroke="{c}" stroke-width="1.5"/>'
        '<circle cx="8" cy="8" r="2" fill="{c}"/>',
    ),
    (
        "HARDWARE TARGET",
        "Carbon-Based · Single Node",
        "单节点部署，不支持集群化或横向扩容",
        "cyan",
        '<rect x="3" y="3" width="10" height="10" rx="2" fill="none" stroke="{c}" stroke-width="1.5"/>'
        '<path d="M6 1v2M10 1v2M6 13v2M10 13v2M1 6h2M1 10h2M13 6h2M13 10h2" stroke="{c}" stroke-width="1.3" stroke-linecap="round"/>',
    ),
    (
        "POWER INPUT",
        "Carbohydrates · Sleep",
        "断供期间触发性能降级与状态告警",
        "emerald",
        '<path d="M9 1.5L3.5 9H8l-1 5.5L12.5 7H8l1-5.5Z" fill="none" stroke="{c}" stroke-width="1.4" stroke-linejoin="round"/>',
    ),
    (
        "MAINTENANCE WINDOW",
        "6–8h / 24h · Offline",
        "每日离线执行记忆整理与上下文清理",
        "cyan",
        '<path d="M12.5 9.8A5.2 5.2 0 0 1 6.2 3.5a5.3 5.3 0 1 0 6.3 6.3Z" fill="none" stroke="{c}" stroke-width="1.4" stroke-linejoin="round"/>',
    ),
    (
        "CONCURRENCY",
        "1 Thread · Preemptive",
        "严格单线程调度，新想法到达时直接抢占",
        "cyan",
        '<path d="M4 3v10M4 8h5a3 3 0 0 0 3-3V3M10 5l2-2 2 2" fill="none" stroke="{c}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
    ),
    (
        "ROLLBACK & BACKLOG",
        "No Revert · Growing",
        "历史版本不可回滚，待办持续高于清理速率",
        "amber",
        '<path d="M8 2.2L14 13H2L8 2.2Z" fill="none" stroke="{c}" stroke-width="1.4" stroke-linejoin="round"/>'
        '<path d="M8 6.4v3.2M8 11.4v.4" stroke="{c}" stroke-width="1.4" stroke-linecap="round"/>',
    ),
]


def render_spec_svg(theme_name: str) -> str:
    """渲染透明底 2x3 Bento 规格卡片网格 SVG。"""
    t = THEMES[theme_name]
    mono = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
    sans = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'PingFang SC', sans-serif"

    card_w = 468
    card_h = 84
    col_gap = 22
    row_gap = 12

    cards_svg: list[str] = []
    for idx, (label, value, desc, color_key, icon_tpl) in enumerate(CARDS):
        col = idx % 2
        row = idx // 2
        cx = 1 + col * (card_w + col_gap)
        cy = 1 + row * (card_h + row_gap)
        accent = t[color_key]
        icon_svg = icon_tpl.format(c=accent)
        icon_cls = ' class="spec-warn"' if idx == 5 else ' class="spec-icon"'
        live_ring = (
            f'\n    <circle class="motion-only" cx="{cx + 21}" cy="{cy + 20}" r="3" fill="none" stroke="{accent}" stroke-width="1.3" stroke-opacity="0.7">\n'
            f'      <animate attributeName="r" values="3;9.5" dur="2.8s" repeatCount="indefinite"/>\n'
            f'      <animate attributeName="stroke-opacity" values="0.7;0" dur="2.8s" repeatCount="indefinite"/>\n'
            f"    </circle>"
            if idx == 0
            else ""
        )

        cards_svg.append(
            f"""  <g>
    <rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" rx="12" fill="url(#spec-card-{theme_name})" stroke="{t['border']}" stroke-width="1"/>
    <rect class="spec-edge spec-d{idx}" x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" rx="12" fill="none" stroke="{accent}" stroke-width="1" stroke-opacity="0"/>{live_ring}
    <circle class="spec-dot spec-d{idx}" cx="{cx + 21}" cy="{cy + 20}" r="3" fill="{accent}"/>
    <text x="{cx + 31}" y="{cy + 24}" fill="{t['text_muted']}" font-family="{mono}" font-size="10.5" letter-spacing="1.1">{html.escape(label)}</text>
    <g{icon_cls} transform="translate({cx + card_w - 34}, {cy + 12})">{icon_svg}</g>
    <text x="{cx + 18}" y="{cy + 49}" fill="{t['text_primary']}" font-family="{sans}" font-size="17" font-weight="600">{html.escape(value)}</text>
    <text x="{cx + 18}" y="{cy + 70}" fill="{t['text_secondary']}" font-family="{sans}" font-size="12">{html.escape(desc)}</text>
  </g>"""
        )

    joined_cards = "\n".join(cards_svg)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 278" width="960" height="278" role="img" aria-label="sl251 system specification bento grid ({theme_name})">
  <style>
    @keyframes specDotBreathe {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.42; }}
    }}
    @keyframes specEdgeGlow {{
      0%, 100% {{ stroke-opacity: 0; }}
      50% {{ stroke-opacity: 0.36; }}
    }}
    @keyframes specWarnPulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.48; }}
    }}
    .spec-dot {{ animation: specDotBreathe 3.6s ease-in-out infinite; }}
    .spec-edge {{ animation: specEdgeGlow 4.8s ease-in-out infinite; }}
    .spec-warn {{ animation: specWarnPulse 2.4s ease-in-out infinite; }}
    .spec-d0 {{ animation-delay: 0s; }}
    .spec-d1 {{ animation-delay: -0.8s; }}
    .spec-d2 {{ animation-delay: -1.6s; }}
    .spec-d3 {{ animation-delay: -2.4s; }}
    .spec-d4 {{ animation-delay: -3.2s; }}
    .spec-d5 {{ animation-delay: -4.0s; }}
    @media (prefers-reduced-motion: reduce) {{
      .spec-dot, .spec-edge, .spec-warn {{ animation: none; }}
      .motion-only {{ display: none; }}
    }}
  </style>
  <defs>
    <linearGradient id="spec-card-{theme_name}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t['card_bg_start']}"/>
      <stop offset="100%" stop-color="{t['card_bg_end']}"/>
    </linearGradient>
  </defs>
{joined_cards}
</svg>
"""


def main() -> None:
    """生成深浅双色 System Spec Bento SVG 文件。"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        out_path = ASSETS_DIR / f"spec-{theme}.svg"
        out_path.write_text(render_spec_svg(theme), encoding="utf-8")


if __name__ == "__main__":
    main()

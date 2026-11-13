#!/usr/bin/env python3
"""生成 Q 版冬雪莲（结合 Q 版萌脸发饰与青花瓷服饰特征）骑自行车动态 SVG 片段。

用于嵌入主页顶部遥测卡片右侧 458x130 视口，严格使用纯声明式 SVG
（CSS @keyframes + SMIL 动画，无脚本），并通过解析式二连杆逆运动学（IK）
确保双腿、袜套、短靴与旋转曲柄及踏板精确咬合联动。
"""

from __future__ import annotations

import math

# 单车核心几何与运动学参数（基于 458x130 局部画布坐标）
GROUND_Y = 116.0
WHEEL_R = 16.0
WHEEL_Y = GROUND_Y - WHEEL_R  # 100.0
REAR_X = 194.0
FRONT_X = 274.0
BB_X = 230.0
BB_Y = 100.0
CRANK_R = 6.5

HIP_X = 218.0
HIP_Y = 69.0
THIGH_LEN = 20.0
SHIN_LEN = 20.0

CRANK_DUR = "1.2s"
WHEEL_DUR = "0.8s"
# 0.8s 内轮子转一圈行进 2 * pi * 16 ≈ 100.53px，路面虚线严格按此步长卷动实现零打滑
WHEEL_CIRC = 2.0 * math.pi * WHEEL_R  # 100.531

# 骑行场景配色（兼容深浅主题背景并保持银白发丝与服饰高辨识度）
SCENE_PALETTES: dict[str, dict[str, str]] = {
    "dark": {
        "sky_top": "#070c14",
        "sky_bot": "#0f1c2e",
        "hill_far": "#142238",
        "hill_mid": "#1a2d47",
        "road_bg": "#0a1019",
        "road_line": "#2a3c55",
        "road_dash": "#475f7d",
        "shadow": "#020617",
        "outline": "#1e293b",
        "hair_outline": "#64748b",
        "skin": "#fde6da",
        "skin_far": "#f3cfc0",
        "blush": "#fb7185",
        "hair_main": "#f8fafc",
        "hair_shadow": "#dbeafe",
        "hair_tint": "#818cf8",
        "dress_white": "#f8fafc",
        "dress_mid": "#93c5fd",
        "dress_deep": "#1d4ed8",
        "ribbon_navy": "#1e3a8a",
        "sock_gray": "#a8a29e",
        "boot_dark": "#1e293b",
        "bike_frame": "#38bdf8",
        "bike_frame_dark": "#0284c7",
        "tire": "#0f172a",
        "tire_edge": "#64748b",
        "rim": "#94a3b8",
        "spoke": "#cbd5e1",
        "basket": "#d6b88d",
        "basket_stroke": "#92764f",
        "snow": "#bae6fd",
        "drop_fill": "#7dd3fc",
        "drop_stroke": "#38bdf8",
        "hud_text": "#64748b",
    },
    "light": {
        "sky_top": "#e6f1fc",
        "sky_bot": "#f7fbff",
        "hill_far": "#d2e3f5",
        "hill_mid": "#bdd4ec",
        "road_bg": "#dce6f2",
        "road_line": "#9fb3c8",
        "road_dash": "#ffffff",
        "shadow": "#94a3b8",
        "outline": "#334155",
        "hair_outline": "#64748b",
        "skin": "#fde4d6",
        "skin_far": "#f3cbb9",
        "blush": "#fb7185",
        "hair_main": "#ffffff",
        "hair_shadow": "#dbeafe",
        "hair_tint": "#6366f1",
        "dress_white": "#ffffff",
        "dress_mid": "#60a5fa",
        "dress_deep": "#1e40af",
        "ribbon_navy": "#1e3a8a",
        "sock_gray": "#9ca3af",
        "boot_dark": "#1e293b",
        "bike_frame": "#0284c7",
        "bike_frame_dark": "#0369a1",
        "tire": "#334155",
        "tire_edge": "#94a3b8",
        "rim": "#64748b",
        "spoke": "#94a3b8",
        "basket": "#e5cca3",
        "basket_stroke": "#8c6d46",
        "snow": "#38bdf8",
        "drop_fill": "#7dd3fc",
        "drop_stroke": "#0284c7",
        "hud_text": "#6e7781",
    },
}


def _solve_leg_ik(
    hx: float, hy: float, ax: float, ay: float, l1: float, l2: float
) -> tuple[float, float]:
    """二连杆平面逆运动学求解（膝盖朝画面右侧前屈）。"""
    dx = ax - hx
    dy = ay - hy
    dist = math.hypot(dx, dy)
    max_reach = l1 + l2 - 0.15
    if dist > max_reach:
        dist = max_reach
    elif dist < 1.0:
        dist = 1.0

    ux = dx / dist
    uy = dy / dist
    cos_a = max(-1.0, min(1.0, (l1 * l1 + dist * dist - l2 * l2) / (2.0 * l1 * dist)))
    a = dist * cos_a
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))

    # SVG y 轴向下，前屈法线方向为 (+uy, -ux)
    kx = hx + a * ux + h * uy
    ky = hy + a * uy - h * ux
    return kx, ky


def _build_leg_keyframes(phase_offset: float, samples: int = 16) -> dict[str, str]:
    """采样完整踩踏周期的腿部、过膝袜、短袜、吊袜带与短靴位移序列。"""
    leg_paths: list[str] = []
    sock_paths: list[str] = []
    ankle_sock_paths: list[str] = []
    garter_paths: list[str] = []
    boot_translates: list[str] = []

    for i in range(samples + 1):
        theta = phase_offset + (2.0 * math.pi * i / samples)
        pin_x = BB_X + CRANK_R * math.cos(theta)
        pin_y = BB_Y + CRANK_R * math.sin(theta)
        ax = pin_x - 1.0
        ay = pin_y - 2.6

        kx, ky = _solve_leg_ik(HIP_X, HIP_Y, ax, ay, THIGH_LEN, SHIN_LEN)

        # 大腿 72% 处作为右腿过膝袜分界点
        st = 0.72
        sx = HIP_X + st * (kx - HIP_X)
        sy = HIP_Y + st * (ky - HIP_Y)

        # 小腿 80% 处作为左腿短袜口（复刻图一不对称袜长）
        at = 0.80
        asx = kx + at * (ax - kx)
        asy = ky + at * (ay - ky)

        # 过膝袜上方小吊袜环
        gt = 0.62
        gx = HIP_X + gt * (kx - HIP_X)
        gy = HIP_Y + gt * (ky - HIP_Y)
        tdx = kx - HIP_X
        tdy = ky - HIP_Y
        tlen = max(math.hypot(tdx, tdy), 1.0)
        nx = -tdy / tlen * 3.3
        ny = tdx / tlen * 3.3

        leg_paths.append(f"M {HIP_X:.1f} {HIP_Y:.1f} L {kx:.1f} {ky:.1f} L {ax:.1f} {ay:.1f}")
        sock_paths.append(f"M {sx:.1f} {sy:.1f} L {kx:.1f} {ky:.1f} L {ax:.1f} {ay:.1f}")
        ankle_sock_paths.append(f"M {asx:.1f} {asy:.1f} L {ax:.1f} {ay:.1f}")
        garter_paths.append(f"M {gx - nx:.1f} {gy - ny:.1f} L {gx + nx:.1f} {gy + ny:.1f}")
        boot_translates.append(f"{ax:.1f} {ay:.1f}")

    return {
        "leg_d": ";".join(leg_paths),
        "leg_d0": leg_paths[0],
        "sock_d": ";".join(sock_paths),
        "sock_d0": sock_paths[0],
        "ankle_sock_d": ";".join(ankle_sock_paths),
        "ankle_sock_d0": ankle_sock_paths[0],
        "garter_d": ";".join(garter_paths),
        "garter_d0": garter_paths[0],
        "boot_t": ";".join(boot_translates),
        "boot_t0": boot_translates[0],
    }


def _wheel_svg(cx: float, cy: float, r: float, p: dict[str, str]) -> str:
    """绘制带旋转辐条、外胎高光与花鼓的车轮。"""
    spokes: list[str] = []
    inner_r = r - 2.3
    for k in range(8):
        ang = math.radians(k * 45)
        x2 = cx + inner_r * math.cos(ang)
        y2 = cy + inner_r * math.sin(ang)
        spokes.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{p["spoke"]}" stroke-width="0.85" stroke-opacity="0.72"/>'
        )
    return f"""    <g>
      <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r - 1.0:.1f}" fill="none" stroke="{p['tire']}" stroke-width="2.4"/>
      <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r - 2.2:.1f}" fill="none" stroke="{p['rim']}" stroke-width="0.9"/>
      <g>
        {"".join(spokes)}
        <animateTransform class="smil-anim" attributeName="transform" type="rotate" from="0 {cx:.1f} {cy:.1f}" to="360 {cx:.1f} {cy:.1f}" dur="{WHEEL_DUR}" repeatCount="indefinite"/>
      </g>
      <circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.2" fill="{p['bike_frame_dark']}" stroke="{p['outline']}" stroke-width="0.7"/>
      <circle cx="{cx:.1f}" cy="{cy:.1f}" r="0.9" fill="#ffffff"/>
    </g>"""


def build_cycling_panel(theme_name: str, peak_per_day: int) -> str:
    """构建替换原图三右侧面板（458x130）的 Q 版冬雪莲骑行场景 SVG。"""
    p = SCENE_PALETTES[theme_name]
    mono = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"

    near_kf = _build_leg_keyframes(0.0)
    far_kf = _build_leg_keyframes(math.pi)

    # 路面虚线按 100.531px 精确周期铺满 [0 .. 580]，滚动周期与车轮转一圈严格一致
    step = WHEEL_CIRC / 2.0
    road_dashes = "".join(
        f'<rect x="{i * step:.1f}" y="121.5" width="22" height="2.2" rx="1.1" fill="{p["road_dash"]}" fill-opacity="0.48"/>'
        for i in range(12)
    )

    # 远景雪山轮廓（双倍平铺宽度 460px）
    far_hills_tile = (
        "M 0 116 L 0 96 Q 48 80 96 95 Q 145 106 196 86 Q 248 72 300 94 "
        "Q 360 105 412 88 Q 438 82 460 96 L 460 116 Z"
    )
    # 中景冬日松树剪影与路灯（双倍平铺 460px）
    mid_trees = "".join(
        f'<g transform="translate({tx}, 0)">'
        f'<polygon points="0,116 7,96 14,116" fill="{p["hill_mid"]}"/>'
        f'<polygon points="2,106 7,91 12,106" fill="{p["hill_mid"]}"/>'
        f"</g>"
        for tx in (28, 46, 152, 294, 314, 418)
    )
    mid_trees_pair = (
        f'<g opacity="0.58">{mid_trees}'
        f'<g transform="translate(460, 0)">{mid_trees}</g></g>'
    )

    # 飘落的小雪花与速度光点
    snow_particles = "".join(
        f'<circle class="motion-only" cx="{sx}" cy="{sy}" r="{sr}" fill="{p["snow"]}" fill-opacity="{op}">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;-180 28" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;{op};{op};0" keyTimes="0;0.15;0.82;1" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
        f"</circle>"
        for sx, sy, sr, op, dur, beg in (
            (440, 22, 1.4, "0.75", "2.6", "0"),
            (390, 38, 1.1, "0.60", "3.1", "-1.1"),
            (325, 18, 1.3, "0.68", "2.8", "-2.0"),
            (450, 56, 1.0, "0.55", "2.4", "-0.6"),
            (280, 24, 1.2, "0.62", "3.3", "-1.7"),
        )
    )

    # 双马尾随风波浪关键帧（左后侧飘逸双缕马尾 & 右侧马尾）
    tail_l_1 = "M 212 24 C 202 27 195 36 192 50 Q 197 53 200 47 Q 200 54 205 56 Q 207 49 209 42 Q 213 33 215 26 Z"
    tail_l_2 = "M 212 24 C 199 26 191 34 187 48 Q 193 51 197 45 Q 197 52 202 54 Q 205 47 208 41 Q 212 33 215 26 Z"
    tail_r_1 = "M 241 23 C 248 28 249 38 247 48 Q 243 49 242 44 Q 240 34 239 26 Z"
    tail_r_2 = "M 241 23 C 250 27 251 37 249 47 Q 245 48 243 43 Q 240 34 239 26 Z"

    # 后摆蝴蝶结燕尾丝带波浪关键帧
    cape_1 = "M 212 65 Q 199 69 190 66 Q 196 72 207 71 Z"
    cape_2 = "M 212 65 Q 200 65 188 69 Q 197 74 208 71 Z"

    # 短靴（局部原点在脚踝，鞋尖朝右）
    boot_shape = (
        f'<path d="M -3.6 -3.8 L 1.2 -3.8 L 2.2 0.3 L 6.0 0.8 Q 7.2 1.8 6.4 2.8 L -3.8 2.8 Z" '
        f'fill="{p["boot_dark"]}" stroke="{p["outline"]}" stroke-width="0.9" stroke-linejoin="round"/>'
        f'<line x1="-1.2" y1="-2.2" x2="1.4" y2="-2.2" stroke="#94a3b8" stroke-width="0.6"/>'
        f'<line x1="-1.0" y1="-0.8" x2="1.6" y2="-0.8" stroke="#94a3b8" stroke-width="0.6"/>'
    )

    return f"""  <defs>
    <linearGradient id="cycle-sky-{theme_name}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{p['sky_top']}"/>
      <stop offset="100%" stop-color="{p['sky_bot']}"/>
    </linearGradient>
    <linearGradient id="dress-grad-{theme_name}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{p['dress_white']}"/>
      <stop offset="58%" stop-color="{p['dress_white']}"/>
      <stop offset="82%" stop-color="{p['dress_mid']}"/>
      <stop offset="100%" stop-color="{p['dress_deep']}"/>
    </linearGradient>
    <linearGradient id="sleeve-grad-{theme_name}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{p['dress_white']}"/>
      <stop offset="65%" stop-color="{p['dress_mid']}"/>
      <stop offset="100%" stop-color="{p['dress_deep']}"/>
    </linearGradient>
    <linearGradient id="iris-grad-{theme_name}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="55%" stop-color="#93c5fd"/>
      <stop offset="100%" stop-color="#e0e7ff"/>
    </linearGradient>
  </defs>

  <g clip-path="url(#panel-clip-{theme_name})">
    <g transform="translate(473, 65)">
      <!-- 天空与视差远中景 -->
      <rect x="0" y="0" width="458" height="116" fill="url(#cycle-sky-{theme_name})"/>
      <g class="bg-far" opacity="0.65">
        <path d="{far_hills_tile}" fill="{p['hill_far']}"/>
        <path d="{far_hills_tile}" fill="{p['hill_far']}" transform="translate(460, 0)"/>
      </g>
      <g class="bg-mid">{mid_trees_pair}</g>

      <!-- 路面与零打滑滚动虚线 -->
      <rect x="0" y="116" width="458" height="14" fill="{p['road_bg']}"/>
      <line x1="0" y1="116" x2="458" y2="116" stroke="{p['road_line']}" stroke-width="1"/>
      <g class="road-track">{road_dashes}</g>

      <!-- 左/右上角极简角标 -->
      <text x="15" y="17" fill="{p['hud_text']}" font-family="{mono}" font-size="9.5" letter-spacing="1.0" opacity="0.82">SL251 // WINTER CYCLING</text>
      <text x="443" y="17" text-anchor="end" fill="{p['hud_text']}" font-family="{mono}" font-size="9.5" letter-spacing="0.8" opacity="0.82">PEAK {peak_per_day}/D</text>

      <!-- 速度风线与飘雪粒子 -->
      <g class="motion-only" opacity="0.48">
        <line class="wind-line w1" x1="120" y1="54" x2="156" y2="54" stroke="{p['snow']}" stroke-width="1" stroke-linecap="round"/>
        <line class="wind-line w2" x1="102" y1="88" x2="144" y2="88" stroke="{p['snow']}" stroke-width="0.9" stroke-linecap="round"/>
      </g>
      {snow_particles}

      <!-- 地面投影 -->
      <ellipse cx="234" cy="116.5" rx="52" ry="2.2" fill="{p['shadow']}" fill-opacity="0.34"/>

      <!-- 远侧左腿（露腿 + 短袜 + 远侧短靴，位于车架后方） -->
      <g>
        <path d="{far_kf['leg_d0']}" fill="none" stroke="{p['outline']}" stroke-width="7.8" stroke-linecap="round" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{far_kf['leg_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>
        <path d="{far_kf['leg_d0']}" fill="none" stroke="{p['skin_far']}" stroke-width="5.8" stroke-linecap="round" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{far_kf['leg_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>
        <path d="{far_kf['ankle_sock_d0']}" fill="none" stroke="{p['outline']}" stroke-width="7.8" stroke-linecap="round">
          <animate class="smil-anim" attributeName="d" values="{far_kf['ankle_sock_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>
        <path d="{far_kf['ankle_sock_d0']}" fill="none" stroke="{p['sock_gray']}" stroke-width="5.8" stroke-linecap="round">
          <animate class="smil-anim" attributeName="d" values="{far_kf['ankle_sock_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>
        <g transform="translate({far_kf['boot_t0']})">
          {boot_shape}
          <animateTransform class="smil-anim" attributeName="transform" type="translate" values="{far_kf['boot_t']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </g>
      </g>

      <!-- 远侧曲柄与平踏板 -->
      <g>
        <g transform="translate({BB_X:.1f}, {BB_Y:.1f})">
          <g>
            <line x1="0" y1="0" x2="{-CRANK_R:.1f}" y2="0" stroke="{p['outline']}" stroke-width="2.0" stroke-linecap="round"/>
            <g transform="translate({-CRANK_R:.1f}, 0)">
              <g>
                <rect x="-3.4" y="-1.1" width="6.8" height="2.2" rx="1" fill="{p['outline']}"/>
                <animateTransform class="smil-anim" attributeName="transform" type="rotate" from="0 0 0" to="-360 0 0" dur="{CRANK_DUR}" repeatCount="indefinite"/>
              </g>
            </g>
            <animateTransform class="smil-anim" attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="{CRANK_DUR}" repeatCount="indefinite"/>
          </g>
        </g>
      </g>

      <!-- 自行车主体：前后轮、车架三角、链条、泥瓦与前筐 -->
      {_wheel_svg(REAR_X, WHEEL_Y, WHEEL_R, p)}
      {_wheel_svg(FRONT_X, WHEEL_Y, WHEEL_R, p)}

      <!-- 挡泥板、尾灯与后货架 -->
      <path d="M 176.5 91.5 A 19.2 19.2 0 0 1 210.5 87.5" fill="none" stroke="{p['bike_frame_dark']}" stroke-width="2.1" stroke-linecap="round"/>
      <path d="M 257.5 89.5 A 19.2 19.2 0 0 1 291.5 92.5" fill="none" stroke="{p['bike_frame_dark']}" stroke-width="2.1" stroke-linecap="round"/>
      <path d="M 214 75 L 184 75 L 194 100" fill="none" stroke="{p['rim']}" stroke-width="1.5" stroke-linejoin="round"/>
      <circle cx="183.2" cy="76.2" r="1.8" fill="#fb7185"/>

      <!-- 链条与飞轮/大盘 -->
      <circle cx="{REAR_X:.1f}" cy="{WHEEL_Y:.1f}" r="3.4" fill="{p['rim']}" stroke="{p['outline']}" stroke-width="0.9"/>
      <line class="chain-line" x1="{REAR_X:.1f}" y1="{WHEEL_Y - 3.2:.1f}" x2="{BB_X:.1f}" y2="{BB_Y - 5.8:.1f}" stroke="{p['tire_edge']}" stroke-width="1.3" stroke-dasharray="2.4 1.6"/>
      <line class="chain-line-rev" x1="{REAR_X:.1f}" y1="{WHEEL_Y + 3.2:.1f}" x2="{BB_X:.1f}" y2="{BB_Y + 5.8:.1f}" stroke="{p['tire_edge']}" stroke-width="1.3" stroke-dasharray="2.4 1.6"/>

      <!-- 主车架（暗底描边 + 亮蓝漆面） -->
      <g fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M 194 100 L 230 100 L 218 72 L 194 100 M 230 100 Q 248 90 260 78 M 218 75 Q 240 83 257.5 72 M 256.5 67 L 260 78 Q 266 89 274 100" stroke="{p['outline']}" stroke-width="4.0"/>
        <path d="M 194 100 L 230 100 L 218 72 L 194 100 M 230 100 Q 248 90 260 78 M 218 75 Q 240 83 257.5 72 M 256.5 67 L 260 78 Q 266 89 274 100" stroke="{p['bike_frame']}" stroke-width="2.4"/>
      </g>

      <!-- 座管、复古车座、车把与铃铛 -->
      <line x1="218" y1="72" x2="216" y2="67" stroke="{p['rim']}" stroke-width="2.1" stroke-linecap="round"/>
      <path d="M 207.5 67.5 Q 216 64 224.5 66.8 Q 223 70 209 69.5 Z" fill="{p['ribbon_navy']}" stroke="{p['outline']}" stroke-width="0.9"/>
      <path d="M 256.5 67 L 254 58 Q 250 56 246 58.5" fill="none" stroke="{p['rim']}" stroke-width="2.1" stroke-linecap="round"/>
      <circle cx="253" cy="56.2" r="1.6" fill="#fbbf24" stroke="{p['outline']}" stroke-width="0.6"/>
      <rect x="242.5" y="57.2" width="5.5" height="2.6" rx="1.2" fill="{p['ribbon_navy']}"/>

      <!-- 前车筐与小蓝熊彩蛋（呼应图二发夹小熊） -->
      <g>
        <line x1="264" y1="74" x2="274" y2="100" stroke="{p['rim']}" stroke-width="1.1"/>
        <circle cx="270" cy="60.5" r="4.0" fill="#6366f1" stroke="{p['outline']}" stroke-width="0.85"/>
        <circle cx="267" cy="57.4" r="1.5" fill="#6366f1" stroke="{p['outline']}" stroke-width="0.8"/>
        <circle cx="273" cy="57.4" r="1.5" fill="#6366f1" stroke="{p['outline']}" stroke-width="0.8"/>
        <circle cx="268.8" cy="60.3" r="0.6" fill="#ffffff"/>
        <circle cx="271.5" cy="60.3" r="0.6" fill="#ffffff"/>
        <polygon points="260,61.5 278.5,61.5 275.5,73.5 262.5,73.5" fill="{p['basket']}" stroke="{p['basket_stroke']}" stroke-width="1.0" stroke-linejoin="round"/>
        <line x1="261.2" y1="65.5" x2="277.3" y2="65.5" stroke="{p['basket_stroke']}" stroke-width="0.7" stroke-opacity="0.65"/>
        <line x1="261.9" y1="69.5" x2="276.5" y2="69.5" stroke="{p['basket_stroke']}" stroke-width="0.7" stroke-opacity="0.65"/>
      </g>

      <!-- 大盘护罩与近侧右腿（灰色过膝袜 + 吊袜带 + 黑色短靴） -->
      <circle cx="{BB_X:.1f}" cy="{BB_Y:.1f}" r="5.6" fill="{p['rim']}" stroke="{p['outline']}" stroke-width="1.0"/>
      <circle cx="{BB_X:.1f}" cy="{BB_Y:.1f}" r="2.1" fill="{p['bike_frame_dark']}"/>

      <g>
        <!-- 右腿轮廓（大腿皮肤 + 过膝灰袜） -->
        <path d="{near_kf['leg_d0']}" fill="none" stroke="{p['outline']}" stroke-width="8.2" stroke-linecap="round" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{near_kf['leg_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>
        <path d="{near_kf['leg_d0']}" fill="none" stroke="{p['skin']}" stroke-width="6.2" stroke-linecap="round" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{near_kf['leg_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>
        <path d="{near_kf['sock_d0']}" fill="none" stroke="{p['outline']}" stroke-width="8.2" stroke-linecap="round" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{near_kf['sock_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>
        <path d="{near_kf['sock_d0']}" fill="none" stroke="{p['sock_gray']}" stroke-width="6.2" stroke-linecap="round" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{near_kf['sock_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>
        <path d="{near_kf['garter_d0']}" fill="none" stroke="{p['outline']}" stroke-width="1.4" stroke-linecap="round">
          <animate class="smil-anim" attributeName="d" values="{near_kf['garter_d']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </path>

        <!-- 近侧曲柄、踏板与绑带短靴 -->
        <g transform="translate({BB_X:.1f}, {BB_Y:.1f})">
          <g>
            <line x1="0" y1="0" x2="{CRANK_R:.1f}" y2="0" stroke="{p['outline']}" stroke-width="2.2" stroke-linecap="round"/>
            <line x1="0" y1="0" x2="{CRANK_R:.1f}" y2="0" stroke="{p['rim']}" stroke-width="1.2" stroke-linecap="round"/>
            <g transform="translate({CRANK_R:.1f}, 0)">
              <g>
                <rect x="-3.5" y="-1.1" width="7.0" height="2.2" rx="1" fill="{p['outline']}"/>
                <animateTransform class="smil-anim" attributeName="transform" type="rotate" from="0 0 0" to="-360 0 0" dur="{CRANK_DUR}" repeatCount="indefinite"/>
              </g>
            </g>
            <animateTransform class="smil-anim" attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="{CRANK_DUR}" repeatCount="indefinite"/>
          </g>
        </g>
        <g transform="translate({near_kf['boot_t0']})">
          {boot_shape}
          <animateTransform class="smil-anim" attributeName="transform" type="translate" values="{near_kf['boot_t']}" dur="{CRANK_DUR}" repeatCount="indefinite"/>
        </g>
      </g>

      <!-- 冬雪莲上半身、青花瓷裙摆与大头 Q 版头像（随骑行节奏轻微弹性起伏） -->
      <g class="rider-bob">
        <!-- 背后飘动小翼状蝴蝶结丝带 -->
        <path d="{cape_1}" fill="{p['ribbon_navy']}" stroke="{p['outline']}" stroke-width="0.9" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{cape_1};{cape_2};{cape_1}" dur="0.72s" repeatCount="indefinite"/>
        </path>

        <!-- 左后侧双马尾 -->
        <path d="{tail_l_1}" fill="{p['hair_main']}" stroke="{p['hair_outline']}" stroke-width="1.15" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{tail_l_1};{tail_l_2};{tail_l_1}" dur="0.72s" repeatCount="indefinite"/>
        </path>

        <!-- 青花瓷白蓝渐变伞裙与波浪蕾丝裙摆 -->
        <path d="M 215 55 C 209 62 204 68 202 72.5 Q 218 76.5 235 72.5 C 232 66 229 60 227 55 Z" fill="url(#dress-grad-{theme_name})" stroke="{p['outline']}" stroke-width="1.1" stroke-linejoin="round"/>
        <path d="M 205 69.5 Q 218 72.5 233 69.5" fill="none" stroke="#dbeafe" stroke-width="0.85" stroke-dasharray="2.5 2"/>
        <!-- 挂在裙角的小蓝流苏 -->
        <circle cx="204.5" cy="74.5" r="1.6" fill="{p['dress_deep']}" stroke="{p['outline']}" stroke-width="0.6"/>

        <!-- 身体上装：白蓝水手领与海军蓝小领结 + 十字坠 -->
        <path d="M 216 55 L 219 44.5 L 229 44.5 L 231 55 Z" fill="{p['dress_white']}" stroke="{p['outline']}" stroke-width="1.05" stroke-linejoin="round"/>
        <path d="M 218.5 45 L 225 51 L 231 45.5 L 228 43.5 L 220 43.5 Z" fill="{p['ribbon_navy']}" stroke="{p['outline']}" stroke-width="0.8"/>
        <polygon points="227,48.5 224.2,47.2 224.2,49.8" fill="{p['ribbon_navy']}"/>
        <polygon points="227,48.5 229.8,47.2 229.8,49.8" fill="{p['ribbon_navy']}"/>
        <circle cx="227" cy="48.5" r="1.1" fill="#93c5fd"/>
        <line x1="227" y1="50" x2="227" y2="54.2" stroke="{p['outline']}" stroke-width="0.7"/>
        <line x1="225.7" y1="52.4" x2="228.3" y2="52.4" stroke="{p['outline']}" stroke-width="0.7"/>

        <!-- 伸向车把的手臂与标志性白蓝渐变宽袖 -->
        <path d="M 225 48 L 236 55.5 L 245.5 58.2" fill="none" stroke="{p['outline']}" stroke-width="5.2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 225 48 L 236 55.5 L 245.5 58.2" fill="none" stroke="{p['skin']}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 222 46.5 L 237 54 L 238.5 62.5 Q 229.5 64 221 58 Z" fill="url(#sleeve-grad-{theme_name})" stroke="{p['outline']}" stroke-width="1.0" stroke-linejoin="round"/>
        <circle cx="245.8" cy="58.4" r="2.5" fill="{p['skin']}" stroke="{p['outline']}" stroke-width="0.9"/>

        <!-- 远侧（右后方）双马尾 -->
        <path d="{tail_r_1}" fill="{p['hair_shadow']}" stroke="{p['hair_outline']}" stroke-width="1.05" stroke-linejoin="round">
          <animate class="smil-anim" attributeName="d" values="{tail_r_1};{tail_r_2};{tail_r_1}" dur="0.72s" repeatCount="indefinite"/>
        </path>

        <!-- Q 版大头轮廓与五官（3/4 朝右萌脸，参考图二比例与蓬松银发质感） -->
        <!-- 后层蓬松发底 -->
        <ellipse cx="228.5" cy="31.0" rx="18.2" ry="15.2" fill="{p['hair_main']}" stroke="{p['hair_outline']}" stroke-width="0.95"/>
        <!-- 脸蛋轮廓 + 左侧小耳朵及蓝耳钉 -->
        <path d="M 213.8 29 C 213.8 41.2 220 46.8 231.5 46.6 C 240.2 46.4 244.2 39.8 243.8 29 C 243.5 21 236.5 18 228.5 18 C 219 18 213.8 22 213.8 29 Z" fill="{p['skin']}" stroke="{p['outline']}" stroke-width="0.9"/>
        <circle cx="212.8" cy="36.2" r="2.6" fill="{p['skin']}" stroke="{p['outline']}" stroke-width="0.85"/>
        <circle cx="212.5" cy="37.5" r="1.0" fill="#2563eb"/>

        <!-- 腮红、柔和弯眉与图二同款 w 猫咪微笑 -->
        <ellipse cx="220.2" cy="39.8" rx="3.4" ry="1.8" fill="{p['blush']}" fill-opacity="0.48"/>
        <ellipse cx="239.2" cy="39.2" rx="2.6" ry="1.5" fill="{p['blush']}" fill-opacity="0.48"/>
        <path d="M 229.8 41.5 Q 231.3 43.1 232.6 41.6 Q 233.9 43.1 235.4 41.3" fill="none" stroke="{p['hair_outline']}" stroke-width="0.85" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M 222.2 28.8 Q 225.2 27.6 228.0 28.8" fill="none" stroke="{p['hair_outline']}" stroke-width="0.65" stroke-opacity="0.7" stroke-linecap="round"/>
        <path d="M 235.2 28.8 Q 237.8 27.6 240.4 28.8" fill="none" stroke="{p['hair_outline']}" stroke-width="0.65" stroke-opacity="0.7" stroke-linecap="round"/>

        <!-- 紫蓝渐变动感大眼（绕局部中心缩放实现稳固眨眼） -->
        <g transform="translate(225.2, 34.8)">
          <g>
            <ellipse cx="0" cy="0" rx="4.2" ry="4.8" fill="#ffffff" stroke="{p['hair_outline']}" stroke-width="0.65"/>
            <ellipse cx="0.2" cy="0.2" rx="3.5" ry="4.3" fill="url(#iris-grad-{theme_name})"/>
            <ellipse cx="0.2" cy="0.4" rx="1.4" ry="2.0" fill="#3730a3"/>
            <circle cx="-1.1" cy="-1.6" r="1.4" fill="#ffffff"/>
            <circle cx="1.2" cy="1.7" r="0.7" fill="#ffffff"/>
            <path d="M -4.4 -1.4 Q 0 -5.5 4.4 -1.6" fill="none" stroke="{p['outline']}" stroke-width="1.35" stroke-linecap="round"/>
            <animateTransform class="smil-anim" attributeName="transform" type="scale" values="1 1;1 1;1 0.1;1 1;1 1" keyTimes="0;0.90;0.935;0.97;1" dur="4.2s" repeatCount="indefinite"/>
          </g>
        </g>
        <g transform="translate(238.2, 34.5)">
          <g>
            <ellipse cx="0" cy="0" rx="3.4" ry="4.5" fill="#ffffff" stroke="{p['hair_outline']}" stroke-width="0.65"/>
            <ellipse cx="-0.1" cy="0.2" rx="2.8" ry="4.0" fill="url(#iris-grad-{theme_name})"/>
            <ellipse cx="-0.1" cy="0.4" rx="1.15" ry="1.8" fill="#3730a3"/>
            <circle cx="-0.9" cy="-1.4" r="1.2" fill="#ffffff"/>
            <circle cx="0.9" cy="1.5" r="0.6" fill="#ffffff"/>
            <path d="M -3.5 -1.3 Q 0 -5.1 3.6 -1.5" fill="none" stroke="{p['outline']}" stroke-width="1.3" stroke-linecap="round"/>
            <animateTransform class="smil-anim" attributeName="transform" type="scale" values="1 1;1 1;1 0.1;1 1;1 1" keyTimes="0;0.90;0.935;0.97;1" dur="4.2s" repeatCount="indefinite"/>
          </g>
        </g>

        <!-- 蓬松碎刘海、垂落颊侧修颜鬓发、冷紫挑染发丝与顶部呆毛 -->
        <path d="M 210 28 C 210.5 17.5 220 14.5 229 14.5 C 238 14.5 244.5 18 245.5 27.5 C 246 34 245.2 42 243 47.5 Q 241.2 43.5 242 35 Q 241.5 28.5 239 29.8 Q 237 24 234.5 30 Q 232 24 229.5 31 Q 227 24.5 224 30.2 Q 221 24.5 218.5 30.5 Q 216 27 215.5 36 Q 216.5 44 214 50.5 Q 210.5 44 210 34 Z" fill="{p['hair_main']}" stroke="{p['hair_outline']}" stroke-width="0.9" stroke-linejoin="round"/>
        <path d="M 227.5 21 Q 226.8 27 228.0 30" fill="none" stroke="{p['hair_tint']}" stroke-width="1.05" stroke-linecap="round"/>
        <path d="M 222.5 22 Q 222 25.5 222.8 27.8" fill="none" stroke="{p['hair_outline']}" stroke-width="0.55" stroke-opacity="0.45" stroke-linecap="round"/>
        <path d="M 235.5 22 Q 235.5 25.5 234.8 27.8" fill="none" stroke="{p['hair_outline']}" stroke-width="0.55" stroke-opacity="0.45" stroke-linecap="round"/>
        <!-- 顶部精致呆毛 -->
        <path d="M 226 14.8 Q 223 7.5 216.5 9.8 Q 221.5 11.5 224.8 14.8 Z" fill="{p['hair_main']}" stroke="{p['hair_outline']}" stroke-width="0.8" stroke-linejoin="round"/>

        <!-- 图二左右不对称萌系发饰（精准置于双马尾发根两侧） -->
        <g>
          <ellipse cx="209.5" cy="22.0" rx="3.9" ry="5.0" transform="rotate(-20 209.5 22.0)" fill="#6366f1" stroke="{p['hair_outline']}" stroke-width="0.8"/>
          <circle cx="206.8" cy="18.8" r="1.9" fill="#4f46e5" stroke="{p['hair_outline']}" stroke-width="0.7"/>
          <circle cx="211.2" cy="17.2" r="2.0" fill="#7dd3fc" stroke="{p['hair_outline']}" stroke-width="0.7"/>
          <circle cx="209.0" cy="24.5" r="2.2" fill="#818cf8" stroke="{p['hair_outline']}" stroke-width="0.7"/>
          <circle cx="209.5" cy="21.8" r="0.6" fill="#ffffff"/>
        </g>
        <g>
          <path d="M 243.5 21.5 L 247.8 27.2 L 244.8 28.2 L 242.5 22.5 Z" fill="{p['ribbon_navy']}" stroke="{p['outline']}" stroke-width="0.7"/>
          <path d="M 244 22 L 241.2 27.5 L 243.8 28.5 L 245 22.5 Z" fill="{p['ribbon_navy']}" stroke="{p['outline']}" stroke-width="0.7"/>
          <line x1="244.6" y1="23.3" x2="246.2" y2="27.2" stroke="#bfdbfe" stroke-width="0.55"/>
          <line x1="243.4" y1="23.6" x2="242.4" y2="27.3" stroke="#bfdbfe" stroke-width="0.55"/>
          <circle cx="241.5" cy="19.5" r="2.5" fill="#f5d0fe" stroke="{p['hair_outline']}" stroke-width="0.7"/>
          <circle cx="239.8" cy="17.4" r="0.95" fill="#f5d0fe" stroke="{p['hair_outline']}" stroke-width="0.65"/>
          <circle cx="243.4" cy="17.6" r="0.95" fill="#f5d0fe" stroke="{p['hair_outline']}" stroke-width="0.65"/>
          <circle cx="245.0" cy="18.6" r="1.8" fill="#bae6fd" stroke="{p['hair_outline']}" stroke-width="0.65"/>
        </g>

        <!-- 图二同款元气浅蓝小水滴气泡 -->
        <g class="drop-float">
          <path d="M 199 15.5 C 199 15.5 196.8 19.6 198.3 20.8 C 199.5 21.6 201.0 20.5 200.4 18.8 Z" fill="{p['drop_fill']}" stroke="{p['drop_stroke']}" stroke-width="0.55"/>
          <path d="M 193.5 23.0 C 193.5 23.0 190.4 25.4 191.5 27.0 C 192.4 28.2 194.2 27.3 194.1 25.6 Z" fill="{p['drop_fill']}" stroke="{p['drop_stroke']}" stroke-width="0.55"/>
          <path d="M 251.5 14.5 C 251.5 14.5 254.3 17.2 253.2 18.8 C 252.3 20.0 250.6 19.1 250.7 17.4 Z" fill="{p['drop_fill']}" stroke="{p['drop_stroke']}" stroke-width="0.55"/>
        </g>
      </g>
    </g>
  </g>"""

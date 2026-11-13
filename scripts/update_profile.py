#!/usr/bin/env python3
"""同步 sl251 公开仓库动态、30 天提交脉冲 SVG 头图与 profile.json。

仅采集公开且非 Fork 的本人仓库（并排除当前 profile 仓库自身），
所有输出均以最新真实公开活动日期为锚点，保证无新活动时输出完全幂等。
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

OWNER = "sl251"
SELF_REPO = "sl251"
API_BASE = "https://api.github.com"

ROOT_DIR = Path(__file__).resolve().parent.parent
README_PATH = ROOT_DIR / "README.md"
PROFILE_JSON_PATH = ROOT_DIR / "profile.json"
ASSETS_DIR = ROOT_DIR / "assets"

ACTIVITY_START = "<!-- ACTIVITY:START -->"
ACTIVITY_END = "<!-- ACTIVITY:END -->"
MAX_ACTIVITY_ITEMS = 4
PULSE_DAYS = 30

# 两套自绘遥测头图配色（深色 / 浅色）
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
        "dot": "#34d399",
        "accent_start": "#38bdf8",
        "accent_end": "#34d399",
        "area_color": "#38bdf8",
        "area_opacity": "0.16",
        "baseline": "#334155",
        "guide": "#1e293b",
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
        "dot": "#059669",
        "accent_start": "#0284c7",
        "accent_end": "#059669",
        "area_color": "#0284c7",
        "area_opacity": "0.13",
        "baseline": "#cbd5e1",
        "guide": "#dde4ed",
    },
}


def github_get(path: str, token: str | None) -> Any:
    """请求 GitHub REST API；遇到空仓库（409）或无 Release（404）时返回 None。"""
    url = path if path.startswith("http") else f"{API_BASE}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sl251-profile-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 409):
            return None
        raise


def parse_iso_datetime(value: str) -> dt.datetime:
    """将 GitHub ISO 8601 时间字符串解析为带 UTC 时区的 datetime。"""
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def sanitize_text(text: str, max_len: int = 68) -> str:
    """清理提交摘要中的换行、反引号与 Markdown 干扰字符，并按长度截断。"""
    line = re.sub(r"\s+", " ", text.splitlines()[0]).strip()
    line = line.replace("`", "'").replace("[", "(").replace("]", ")")
    if len(line) > max_len:
        line = line[: max_len - 1].rstrip() + "…"
    return line


def fetch_public_original_repos(token: str | None) -> list[dict[str, Any]]:
    """拉取归属于 sl251 的公开非 Fork 原创仓库列表（排除 sl251 自身）。"""
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        data = github_get(
            f"/users/{OWNER}/repos?type=owner&sort=pushed&per_page=100&page={page}",
            token,
        )
        if not data:
            break
        for repo in data:
            # 严格过滤私有仓库、Fork 仓库及当前主页仓库自身
            if repo.get("private") or repo.get("fork"):
                continue
            if repo.get("name") == SELF_REPO:
                continue
            repos.append(repo)
        if len(data) < 100:
            break
        page += 1
    repos.sort(key=lambda r: (r.get("pushed_at") or "", r["name"]), reverse=True)
    return repos


def fetch_recent_activity(
    repos: list[dict[str, Any]], token: str | None
) -> list[dict[str, str]]:
    """从最近活跃的公开仓库采集最新 Release 或最近一次提交。"""
    events: list[dict[str, Any]] = []

    for repo in repos[:8]:
        name = repo["name"]
        html_url = repo["html_url"]

        commits = github_get(f"/repos/{OWNER}/{name}/commits?per_page=1", token)
        latest_commit = commits[0] if isinstance(commits, list) and commits else None

        releases = github_get(f"/repos/{OWNER}/{name}/releases?per_page=1", token)
        latest_release = (
            releases[0]
            if isinstance(releases, list) and releases and not releases[0].get("draft")
            else None
        )

        commit_dt: dt.datetime | None = None
        commit_msg = ""
        if latest_commit:
            commit_info = latest_commit.get("commit", {})
            raw_date = (
                commit_info.get("author", {}).get("date")
                or commit_info.get("committer", {}).get("date")
            )
            if raw_date:
                commit_dt = parse_iso_datetime(raw_date)
            commit_msg = sanitize_text(commit_info.get("message", ""))

        release_dt: dt.datetime | None = None
        if latest_release and latest_release.get("published_at"):
            release_dt = parse_iso_datetime(latest_release["published_at"])

        # 若最新 Release 与最新提交间隔在 24 小时内（或更新），优先展示发版信息
        use_release = (
            release_dt is not None
            and (commit_dt is None or release_dt >= commit_dt - dt.timedelta(hours=24))
        )

        if use_release and release_dt is not None:
            tag = latest_release["tag_name"]
            rel_url = latest_release["html_url"]
            events.append(
                {
                    "repo": name,
                    "repo_url": html_url,
                    "date": release_dt.strftime("%Y-%m-%d"),
                    "timestamp": release_dt.isoformat(),
                    "kind": "release",
                    "tag": tag,
                    "detail_url": rel_url,
                    "summary": f"发布 {tag}",
                    "markdown": (
                        f"- `{release_dt.strftime('%Y-%m-%d')}` · "
                        f"**[{name}]({html_url})** — 发布 [`{tag}`]({rel_url})"
                    ),
                }
            )
        elif commit_dt is not None and commit_msg:
            events.append(
                {
                    "repo": name,
                    "repo_url": html_url,
                    "date": commit_dt.strftime("%Y-%m-%d"),
                    "timestamp": commit_dt.isoformat(),
                    "kind": "commit",
                    "detail_url": latest_commit.get("html_url", html_url),
                    "summary": commit_msg,
                    "markdown": (
                        f"- `{commit_dt.strftime('%Y-%m-%d')}` · "
                        f"**[{name}]({html_url})** — {commit_msg}"
                    ),
                }
            )

    events.sort(key=lambda e: (e["timestamp"], e["repo"]), reverse=True)
    return events[:MAX_ACTIVITY_ITEMS]


def fetch_30d_pulse(
    repos: list[dict[str, Any]],
    anchor_date: dt.date,
    token: str | None,
) -> dict[str, Any]:
    """统计以最新公开活动日期为终点的 30 天每日公开提交数。"""
    start_date = anchor_date - dt.timedelta(days=PULSE_DAYS - 1)
    # 稍微放宽拉取窗口 2 天再按 UTC 日期精确过滤，避免边界遗漏
    since_iso = dt.datetime.combine(
        start_date - dt.timedelta(days=1), dt.time.min, tzinfo=dt.timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    daily_map: dict[str, int] = {
        (start_date + dt.timedelta(days=i)).isoformat(): 0 for i in range(PULSE_DAYS)
    }

    for repo in repos:
        pushed_at = repo.get("pushed_at")
        if pushed_at and parse_iso_datetime(pushed_at).date() < start_date - dt.timedelta(days=2):
            continue

        name = repo["name"]
        page = 1
        while page <= 3:
            query = urllib.parse.urlencode(
                {"since": since_iso, "per_page": 100, "page": page}
            )
            commits = github_get(f"/repos/{OWNER}/{name}/commits?{query}", token)
            if not isinstance(commits, list) or not commits:
                break
            for item in commits:
                raw_date = (
                    item.get("commit", {}).get("author", {}).get("date")
                    or item.get("commit", {}).get("committer", {}).get("date")
                )
                if not raw_date:
                    continue
                day_key = parse_iso_datetime(raw_date).date().isoformat()
                if day_key in daily_map:
                    daily_map[day_key] += 1
            if len(commits) < 100:
                break
            page += 1

    ordered_days = sorted(daily_map.keys())
    counts = [daily_map[d] for d in ordered_days]
    total_commits = sum(counts)
    peak = max(counts) if counts else 0

    return {
        "window_start": ordered_days[0],
        "window_end": ordered_days[-1],
        "total_commits": total_commits,
        "peak_per_day": peak,
        "daily_counts": [
            {"date": d, "commits": daily_map[d]} for d in ordered_days
        ],
    }


def build_ecg_paths(counts: list[int]) -> tuple[str, str, list[tuple[float, float, int]]]:
    """将 30 天每日提交数转换为平滑的示波器/心电脉冲 SVG 路径与峰点坐标。"""
    x_start = 496.0
    x_end = 916.0
    y_base = 158.0
    y_bottom = 176.0
    max_height = 54.0
    step = (x_end - x_start) / max(len(counts) - 1, 1)

    peak_ref = max(max(counts, default=0), 4)
    line_parts: list[str] = [f"M {x_start - 8.0:.1f} {y_base:.1f}"]
    peaks: list[tuple[float, float, int]] = []

    for idx, count in enumerate(counts):
        cx = x_start + idx * step
        if count <= 0:
            line_parts.append(f"L {cx:.1f} {y_base:.1f}")
            continue

        # 使用幂次平滑缩放，拉开高低提交日的起伏层次同时保证单次提交清晰可见
        ratio = (count / peak_ref) ** 0.65
        height = 12.0 + (max_height - 12.0) * min(ratio, 1.0)
        y_peak = y_base - height

        q_x = cx - 4.8
        dip_x = cx - 2.2
        s_x = cx + 2.3
        end_x = cx + 5.0

        line_parts.append(f"L {q_x:.1f} {y_base:.1f}")
        line_parts.append(f"L {dip_x:.1f} {y_base + 4.5:.1f}")
        line_parts.append(f"L {cx:.1f} {y_peak:.1f}")
        line_parts.append(f"L {s_x:.1f} {y_base + 6.5:.1f}")
        line_parts.append(f"L {end_x:.1f} {y_base:.1f}")
        peaks.append((cx, y_peak, count))

    line_parts.append(f"L {x_end + 8.0:.1f} {y_base:.1f}")
    line_d = " ".join(line_parts)
    area_d = f"{line_d} L {x_end + 8.0:.1f} {y_bottom:.1f} L {x_start - 8.0:.1f} {y_bottom:.1f} Z"
    return line_d, area_d, peaks


def render_header_svg(theme_name: str, pulse: dict[str, Any]) -> str:
    """生成指定配色的自托管遥测 SVG 头图。"""
    t = THEMES[theme_name]
    counts = [item["commits"] for item in pulse["daily_counts"]]
    line_d, area_d, peaks = build_ecg_paths(counts)

    total_commits = pulse["total_commits"]
    peak = pulse["peak_per_day"]
    w_start = html.escape(pulse["window_start"])
    w_end = html.escape(pulse["window_end"])

    # 仅在有提交的日子画圆点，最后一个活跃点加淡淡外圈
    dots_svg_parts: list[str] = []
    for idx, (px, py, _cnt) in enumerate(peaks):
        is_last = idx == len(peaks) - 1
        if is_last:
            dots_svg_parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="{t["dot"]}" fill-opacity="0.22"/>'
            )
            dots_svg_parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.8" fill="{t["dot"]}"/>'
            )
        else:
            dots_svg_parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.0" fill="{t["accent_start"]}"/>'
            )
    dots_svg = "\n    ".join(dots_svg_parts)

    mono = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
    sans = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 220" width="960" height="220" role="img" aria-label="sl251 telemetry header ({theme_name})">
  <defs>
    <linearGradient id="bg-{theme_name}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t['bg_start']}"/>
      <stop offset="100%" stop-color="{t['bg_end']}"/>
    </linearGradient>
    <linearGradient id="pulse-stroke-{theme_name}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{t['accent_start']}"/>
      <stop offset="100%" stop-color="{t['accent_end']}"/>
    </linearGradient>
    <linearGradient id="pulse-area-{theme_name}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{t['area_color']}" stop-opacity="{t['area_opacity']}"/>
      <stop offset="100%" stop-color="{t['area_color']}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid-{theme_name}" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M 32 0 L 0 0 0 32" fill="none" stroke="{t['grid']}" stroke-opacity="{t['grid_opacity']}" stroke-width="1"/>
    </pattern>
    <clipPath id="card-clip-{theme_name}">
      <rect x="1" y="1" width="958" height="218" rx="14"/>
    </clipPath>
  </defs>

  <g clip-path="url(#card-clip-{theme_name})">
    <rect x="1" y="1" width="958" height="218" rx="14" fill="url(#bg-{theme_name})"/>
    <rect x="1" y="1" width="958" height="218" fill="url(#grid-{theme_name})"/>
  </g>
  <rect x="1" y="1" width="958" height="218" rx="14" fill="none" stroke="{t['border']}" stroke-width="1"/>

  <!-- 顶部状态栏 -->
  <circle cx="34" cy="30" r="7.5" fill="{t['dot']}" fill-opacity="0.18"/>
  <circle cx="34" cy="30" r="3.6" fill="{t['dot']}"/>
  <text x="50" y="34" fill="{t['text_secondary']}" font-family="{mono}" font-size="11.5" letter-spacing="1.4">SL251 // TELEMETRY</text>
  <text x="928" y="34" text-anchor="end" fill="{t['text_muted']}" font-family="{mono}" font-size="11" letter-spacing="0.9">30D PULSE · {total_commits} COMMITS · LATEST {w_end}</text>
  <line x1="28" y1="50" x2="932" y2="50" stroke="{t['divider']}" stroke-width="1"/>

  <!-- 左侧项目主标识区 -->
  <text x="36" y="126" fill="{t['text_primary']}" font-family="{sans}" font-size="48" font-weight="700" letter-spacing="-1">sl251</text>
  <text x="38" y="156" fill="{t['text_secondary']}" font-family="{sans}" font-size="15">A human project. No stable release yet.</text>

  <!-- 右侧 30 天公开提交示波面板 -->
  <rect x="472" y="64" width="460" height="132" rx="10" fill="{t['panel_bg']}" fill-opacity="{t['panel_bg_opacity']}" stroke="{t['panel_border']}" stroke-width="1"/>
  <text x="488" y="83" fill="{t['text_muted']}" font-family="{mono}" font-size="10.5" letter-spacing="1.1">PUBLIC COMMIT PULSE (30D)</text>
  <text x="918" y="83" text-anchor="end" fill="{t['text_secondary']}" font-family="{mono}" font-size="10.5" letter-spacing="0.8">PEAK {peak}/D</text>

  <line x1="488" y1="106" x2="922" y2="106" stroke="{t['guide']}" stroke-width="1" stroke-dasharray="2 4"/>
  <line x1="488" y1="132" x2="922" y2="132" stroke="{t['guide']}" stroke-width="1" stroke-dasharray="2 4"/>
  <line x1="488" y1="158" x2="922" y2="158" stroke="{t['baseline']}" stroke-width="1" stroke-dasharray="3 3"/>

  <path d="{area_d}" fill="url(#pulse-area-{theme_name})"/>
  <path d="{line_d}" fill="none" stroke="url(#pulse-stroke-{theme_name})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  {dots_svg}

  <text x="488" y="185" fill="{t['text_muted']}" font-family="{mono}" font-size="10" letter-spacing="0.5">{w_start}</text>
  <text x="918" y="185" text-anchor="end" fill="{t['text_muted']}" font-family="{mono}" font-size="10" letter-spacing="0.5">{w_end}</text>
</svg>
"""


def update_readme_activity(events: list[dict[str, str]]) -> None:
    """只替换 README.md 中 ACTIVITY 标记包裹的区块，保持人工内容原封不动。"""
    content = README_PATH.read_text(encoding="utf-8")
    if ACTIVITY_START not in content or ACTIVITY_END not in content:
        raise RuntimeError("README.md 中缺少 ACTIVITY 起止注释标记")

    if events:
        body = "\n".join(event["markdown"] for event in events)
    else:
        body = "- 暂无公开项目动态记录。"

    replacement = f"{ACTIVITY_START}\n{body}\n{ACTIVITY_END}"
    pattern = re.compile(
        re.escape(ACTIVITY_START) + r".*?" + re.escape(ACTIVITY_END),
        flags=re.DOTALL,
    )
    updated = pattern.sub(replacement, content, count=1)
    if updated != content:
        README_PATH.write_text(updated, encoding="utf-8")


def write_profile_json(
    events: list[dict[str, str]],
    pulse: dict[str, Any],
) -> None:
    """输出供外部 Agent 读取的公开结构化元数据 profile.json。"""
    payload = {
        "handle": OWNER,
        "tagline": "A human project. No stable release yet.",
        "summary": "Clinical Medicine undergrad. Building AI agents, Android apps, and overly serious detours.",
        "runtime_status": {
            "release_channel": "Rolling Release",
            "task_scheduler": "Preemptive",
            "scope_control": "Experimental",
            "interrupt_source": "New model releases",
            "rollback_support": "Not Implemented",
            "issue_backlog": "Growing",
        },
        "featured_projects": [
            {
                "name": "HDSI-Android",
                "repo": "sl251/HDSI-Android",
                "url": "https://github.com/sl251/HDSI-Android",
                "summary": "把 HDS-Interlude 的长期记忆、心境和日程叙事引擎搬进 Android 本地，无需电脑或 Termux。",
            },
            {
                "name": "Antigravity ACP",
                "repo": "sl251/astrbot_plugin_antigravity_acp",
                "url": "https://github.com/sl251/astrbot_plugin_antigravity_acp",
                "summary": "让 AstrBot 通过 ACP 协议直接连接并驱动 Antigravity 客户端。",
            },
            {
                "name": "E2B Sandbox",
                "repo": "sl251/astrbot_plugin_e2b_sandbox",
                "url": "https://github.com/sl251/astrbot_plugin_e2b_sandbox",
                "summary": "给机器人配一台云端 Python 沙箱电脑，算数据、画图、处理文件不占本地资源。",
            },
        ],
        "experiments": [
            {
                "name": "WHO IS NAILONG",
                "url": "https://whoisnailong.me/",
                "repo": "sl251/nailong",
                "summary": "全国高校“奶龙大学”域名 3D 地球，点一下还会笑。一个毫无现实必要性、却依然按正经网站标准配齐了独立域名和交互地球仪的产物。",
            },
            {
                "name": "defensive-writing-expression",
                "url": "https://github.com/sl251/defensive-writing-expression",
                "repo": "sl251/defensive-writing-expression",
                "summary": "GPT 式防御性表达 Skill：专门把简单观点改写成层层审慎修饰的“过审腔”。",
            },
        ],
        "telemetry_30d": pulse,
        "recent_activity": [
            {
                "date": item["date"],
                "repo": item["repo"],
                "kind": item["kind"],
                "summary": item["summary"],
                "url": item["detail_url"],
            }
            for item in events
        ],
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if not PROFILE_JSON_PATH.exists() or PROFILE_JSON_PATH.read_text(encoding="utf-8") != text:
        PROFILE_JSON_PATH.write_text(text, encoding="utf-8")


def write_if_changed(path: Path, content: str) -> None:
    """仅当内容真正变化时写盘，避免不必要的磁盘修改。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")


def main() -> None:
    """入口函数：采集公开数据并幂等更新 README、SVG 头图与 profile.json。"""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repos = fetch_public_original_repos(token)
    events = fetch_recent_activity(repos, token)

    # 以最新真实活动日期作为 30 天脉冲窗口终点，保证无新提交时不触发无效更新
    if events:
        anchor_date = dt.date.fromisoformat(events[0]["date"])
    elif repos and repos[0].get("pushed_at"):
        anchor_date = parse_iso_datetime(repos[0]["pushed_at"]).date()
    else:
        anchor_date = dt.datetime.now(dt.timezone.utc).date()

    pulse = fetch_30d_pulse(repos, anchor_date, token)

    update_readme_activity(events)
    write_profile_json(events, pulse)
    for theme_name in THEMES:
        svg_text = render_header_svg(theme_name, pulse)
        write_if_changed(ASSETS_DIR / f"header-{theme_name}.svg", svg_text)


if __name__ == "__main__":
    main()

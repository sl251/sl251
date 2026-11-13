<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/header-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/header-light.svg">
  <img alt="sl251 telemetry header" src="./assets/header-light.svg" width="100%">
</picture>

# sl251

> A human project. No stable release yet.

`Clinical Medicine undergrad. Building AI agents, Android apps, and overly serious detours.`

业余时间主要做三件事：给 AI Agent 接工具链、把复杂项目塞进手机，以及为一个突然冒出来的念头认真写完一整套仓库。

## Runtime Status

| Property | Value |
| --- | --- |
| Release Channel | `Rolling Release` |
| Task Scheduler | `Preemptive` |
| Scope Control | `Experimental` |
| Interrupt Source | `New model releases` |
| Rollback Support | `Not Implemented` |
| Issue Backlog | `Growing` |

## Deployed Projects

- **[HDSI-Android](https://github.com/sl251/HDSI-Android)** — 把 HDS-Interlude 的长期记忆、心境和日程叙事引擎搬进 Android 本地，无需电脑或 Termux。
- **[Antigravity ACP](https://github.com/sl251/astrbot_plugin_antigravity_acp)** — 让 AstrBot 通过 ACP 协议直接连接并驱动 Antigravity 客户端。
- **[E2B Sandbox](https://github.com/sl251/astrbot_plugin_e2b_sandbox)** — 给机器人配一台云端 Python 沙箱电脑，算数据、画图、处理文件不占本地资源。

<details>
<summary>其他认真做出来的轮子（3）</summary>

- **[defensive-writing-expression](https://github.com/sl251/defensive-writing-expression)** — 专门生成“GPT 式三层套娃防御性表达”的 Agent Skill，配了 22 项回归测试。
- **[zlibrary-tor](https://github.com/sl251/zlibrary-tor)** — 走本地 Tor 代理连 Z-Library 洋葱 E-API 的检索与下载 CLI，全命令输出纯 JSON 供 Agent 调用。
- **[Xiaomi MiMo Voice Dispatcher](https://github.com/sl251/astrbot_plugin_xiaomi_mimo_voice_dispatcher)** — 本来只是为了试免费语音额度，最后做成了让模型自己决定“什么时候开口发语音”的工具插件。

</details>

## Undocumented Features

- 部分仓库的诞生原因，仅仅是不想手动重复同一个步骤两次。
- 比起让 AI 只会聊天，更关心怎么给它接上沙箱、CLI 和工具权限把事情真正做完。
- 遇到“这功能怎么没有”，默认反应是查文档、开仓库、写测试。
- 偏爱可自行部署、本地可控、不依赖黑盒服务的工具形态。

## Recent Activity

<!-- ACTIVITY:START -->
- `2026-11-13` · **[astrbot_plugin_antigravity_acp](https://github.com/sl251/astrbot_plugin_antigravity_acp)** — 发布 [`v0.4.3`](https://github.com/sl251/astrbot_plugin_antigravity_acp/releases/tag/v0.4.3)
- `2026-11-13` · **[defensive-writing-expression](https://github.com/sl251/defensive-writing-expression)** — docs: add defensive writing meme illustration to README
- `2026-11-04` · **[HDSI-Android](https://github.com/sl251/HDSI-Android)** — 发布 [`v0.1.0-preview.9.7.2`](https://github.com/sl251/HDSI-Android/releases/tag/v0.1.0-preview.9.7.2)
- `2026-10-21` · **[zlibrary-tor](https://github.com/sl251/zlibrary-tor)** — fix(deps): raise certifi/setuptools floors (2026-10 advisories)
<!-- ACTIVITY:END -->

## Experiments

- **[WHO IS NAILONG](https://whoisnailong.me/)**（[sl251/nailong](https://github.com/sl251/nailong)）— 全国高校“奶龙大学”域名 3D 地球，点一下还会笑。严肃项目列表里的已知异常。

<details>
<summary>⚠️ 免责声明（以及对该免责声明的澄清）</summary>

本主页展示的内容仅代表该人类对象在最近一次构建时的局部观察快照，并不构成对系统稳定性、作息规律或下一个坑何时会填完的任何承诺；需要说明的是，上述“不作承诺”本身并不意味着项目处于停摆状态，更不能直接等同于对任何既定主线或实验分支的否定。同样地，这句补充澄清也并非为了暗示本仓库存在某种严格意义上的版本发布时间表——它只是一段为了避免过度解读而顺手多写了一层的声明，而“顺手多写了一层”这件事本身，亦不代表任何未明示的承诺。

<sub>— Written in the spirit of <a href="https://github.com/sl251/defensive-writing-expression">defensive-writing-expression</a></sub>

</details>

---

*This project is maintained by itself.*  
<sub>For agents: [`profile.json`](https://github.com/sl251/sl251/blob/main/profile.json)</sub>

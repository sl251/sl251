<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/header-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/header-light.svg">
  <img alt="sl251 telemetry header" src="./assets/header-light.svg" width="100%">
</picture>

# sl251

> A human project. No stable release yet.

`Clinical Medicine undergrad. Building AI agents, Android apps, and overly serious detours.`

## Runtime Status

| Property | Value |
| --- | --- |
| Release Channel | `Rolling Release` |
| Task Scheduler | `Preemptive` |
| Scope Control | `Experimental` |
| Interrupt Source | `New model releases` |
| Rollback Support | `Not Implemented` |
| Issue Backlog | `Growing` |

## Project Assessment

### Project Spec

| 字段 | 当前配置 | 说明 |
| --- | --- | --- |
| **Project ID** | `sl251` | 长期运行于公开预览阶段（Public Preview），尚未进入 GA 正式发行 |
| **Maintainer** | `Single-Maintainer` | 核心架构、日常运维与线上实例均由同一维护方托管，暂不开放外部协作 |
| **Access Policy** | `Read-Only` | 仅对外公开部分构建产物；核心运行环境及内部配置不接受外部 PR |
| **Core Modules** | `Agents · Android · Detours` | 主要功能模块涵盖 Agent 工具链、移动端移植及若干非必要实验特性 |
| **Runtime Env** | `Desktop / Mobile / Cloud` | 强依赖网络连接、命令行环境与持续供电；离线模式下仅保留基础交互能力 |
| **Issue Tracker** | `Internal Only` | 暂未公开外部工单通道，多数已知问题与异常由内部闭环消化 |

### Engineering Audit

| 评估项 | 评级 | 审计说明 |
| --- | --- | --- |
| **服务可用性** | `Beta` | 主干流程可维持常规在线，但主版本尚未冻结，随时可能引入破坏性变更 |
| **文档覆盖率** | `C-` | 对外交付组件具备基础说明；内部状态变更与接口文档长期滞后于实际版本 |
| **热更新机制** | `A` | 暂不支持停机重装与冷迁移，所有策略调整及局部修复均通过在线热补丁生效 |
| **低功耗调度** | `D` | 自动休眠策略尚未稳定，连续高负载周期后常需人工介入执行强制休眠 |
| **范围收敛度** | `D+` | 需求边界控制较弱；轻量级验证脚本在迭代过程中常演变为完整独立模块 |
| **流程自动化倾向** | `High` | 对手工重复操作容忍度较低；面对高频冗余环节倾向于直接开发工具予以接管 |

### Readiness Checklist

- [x] **支持单节点独立冷启动** — 不依赖外部人工编排即可维持基础服务持续运转
- [x] **具备基础异常自愈能力** — 经历资源过载或短暂异常后，通常可在完整休眠周期后恢复
- [x] **处于活跃持续集成状态** — 高频合并新能力与实验性改动，当前仍无特性冻结计划
- [ ] **完成核心路径全量文档化** — 部分底层决策路径仍属于未公开说明的黑盒行为
- [ ] **达到 GA / LTS 长期支持标准** — 仍处公开预览通道，暂不提供稳定性或 SLA 承诺

> **综合评审结论**：一个处于长期预览阶段、特性持续扩张且偶发非预期行为的实验性项目。适合用于前沿工具链探索与快速原型验证；若业务场景对确定性排期或生产级 SLA 有强约束，建议审慎评估接入风险。

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

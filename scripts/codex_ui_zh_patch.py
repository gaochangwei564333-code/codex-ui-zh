#!/usr/bin/env python3
"""
Patch Codex plugin/skill UI metadata into Chinese, with backup and restore.

Targets only active local sources:
- ~/.codex/plugins/cache
- ~/.codex/skills
- ~/.agents/skills

It avoids ~/.codex/.tmp and vendor_imports marketplace caches.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import shutil
from pathlib import Path


HOME = Path.home()
CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex")).expanduser()
BACKUP_ROOT = CODEX_HOME / "backups" / "codex-ui-zh"

TARGET_ROOTS = [
    CODEX_HOME / "plugins" / "cache",
    CODEX_HOME / "skills",
    HOME / ".agents" / "skills",
]

PLUGIN_MANIFEST_ROOTS = [
    CODEX_HOME / "plugins" / "cache",
    CODEX_HOME / ".tmp" / "plugins" / "plugins",
    CODEX_HOME / ".tmp" / "bundled-marketplaces" / "openai-bundled" / "plugins",
    HOME / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "plugins" / "openai-primary-runtime" / "plugins",
]

TRANSLATIONS = {
    "agents": ("语音智能体", "用 ElevenLabs 构建实时语音助手、客服机器人和互动语音角色。"),
    "aihot": ("AI HOT 中文资讯", "查询今天或最近的 AI 热点、模型发布、产品动态、论文和行业消息。"),
    "analyze-data-quality": ("数据质量分析", "在分析或发布前检查表格与数据集的完整性、一致性和质量风险。"),
    "anysearch": ("实时搜索", "进行实时网页搜索、垂直领域搜索、批量搜索和网页内容提取。"),
    "brainstorming": ("需求头脑风暴", "在创作、开发功能或改行为前，先澄清目标、约束和设计方向。"),
    "build-dashboard": ("仪表盘构建", "创建有数据来源、指标定义、筛选器和验证结果的分析仪表盘。"),
    "build-report": ("分析报告构建", "把审核后的证据整理成包含图表、结论、限制和来源的分析报告。"),
    "browser": ("内置浏览器", "让 Codex 打开并操作内置浏览器，用于测试本地网页、点击、输入和截图。"),
    "chrome": ("Chrome 浏览器", "操作用户自己的 Chrome，适合需要登录态、Cookie、扩展或已有标签页的网站。"),
    "claude-to-deerflow": ("DeerFlow 研究代理", "把复杂研究、分析、文件上传和会话任务交给 DeerFlow 平台处理。"),
    "computer-use": ("电脑操作", "控制本地 Mac 应用，执行点击、输入、滚动、拖拽和读屏类任务。"),
    "control-chrome": ("Chrome 浏览器", "操作用户自己的 Chrome，适合需要登录态、Cookie、扩展或已有标签页的网站。"),
    "control-in-app-browser": ("内置浏览器", "让 Codex 打开并操作内置浏览器，用于测试本地网页、点击、输入和截图。"),
    "codex-ui-zh": ("Codex 界面汉化", "先扫描变更，再备份并汉化 Codex 插件页和技能页中文描述"),
    "design-kpis": ("KPI 指标设计", "定义核心指标、驱动指标、护栏指标、目标值和计分卡。"),
    "documents": ("文档处理", "创建、编辑、修订和检查 Word 或 Google Docs 目标文档。"),
    "find-skill": ("技能查找", "查找适合当前任务的可安装 Codex 技能，并提供安装建议。"),
    "gather-business-context": ("业务背景收集", "在分析前收集产品、业务目标、口径和决策背景。"),
    "gh-address-comments": ("PR 评论处理", "检查 GitHub PR 里的未解决评审意见，并实现选定修改。"),
    "gh-fix-ci": ("CI 失败调试", "检查 GitHub Actions 失败日志，定位原因并修复 PR 检查。"),
    "github": ("GitHub 检查", "查看 PR、Issue、CI 和发布流程，理解仓库状态并选择合适工作流。"),
    "github-project-management": ("GitHub 项目管理", "管理 GitHub Issue、项目看板、冲刺计划和多代理协作。"),
    "gmail": ("Gmail 邮箱", "搜索和总结邮件线程、提取待办事项，并起草回复或转发内容。"),
    "gmail-inbox-triage": ("Gmail 收件箱整理", "把收件箱整理为紧急、需回复、等待中和仅供参考等行动分类。"),
    "google-docs": ("Google 文档", "读取、创建和编辑 Google Docs 文档，并验证写入结果。"),
    "google-drive": ("Google 云端硬盘", "统一查找和处理 Drive、Docs、Sheets 与 Slides 文件。"),
    "google-drive-comments": ("Google Drive 评论", "在 Docs、Sheets、Slides 和 Drive 文件中写入、回复或解决评论。"),
    "google-sheets": ("Google 表格", "查找表格、检查精确范围、搜索数据并执行批量更新。"),
    "google-slides": ("Google 幻灯片", "创建、检查、改编和编辑 Google Slides 演示文稿。"),
    "gsap": ("GSAP 动画参考", "为 HyperFrames 动画提供 GSAP 时间线、缓动、交错和性能写法参考。"),
    "hatch-pet": ("Codex 宠物生成", "从角色、品牌或参考图生成 Codex 可用的动态宠物素材。"),
    "heygen": ("HeyGen 数字人视频", "创建 HeyGen 数字人视频和个性化视频消息。"),
    "heygen-avatar": ("HeyGen 数字人身份", "创建可复用的 HeyGen 数字人头像身份，并选择匹配声音。"),
    "heygen-video": ("HeyGen 视频生成", "生成由数字人出镜讲解的 HeyGen 视频。"),
    "hyperframes": ("HyperFrames 视频合成", "用 HTML 创建视频构图、动画、标题卡、字幕、旁白、音频反应视觉和转场。"),
    "hyperframes-cli": ("HyperFrames 命令行", "初始化、检查、预览、渲染、转录和排查 HyperFrames 项目。"),
    "hyperframes-registry": ("HyperFrames 组件库", "安装并接入 HyperFrames registry 里的区块和组件。"),
    "imagegen": ("图片生成与编辑", "生成或编辑网页、游戏、产品图和素材需要的位图图片。"),
    "index": ("数据分析工作流", "为宽泛的数据分析请求选择合适的分析、报告或仪表盘流程。"),
    "jupyter-notebooks": ("Jupyter 分析笔记本", "创建和验证包含代码、输出、假设与检查步骤的可复现分析笔记本。"),
    "kpi-reporting": ("KPI 汇报", "生成面向管理层的 KPI 状态、对比、驱动因素和行动建议。"),
    "letta-api-client": ("Letta API 客户端", "用 Letta API 构建带长期记忆的状态化智能体应用。"),
    "market-sizing": ("市场规模测算", "用透明的范围、假设、计算和敏感性分析估算市场或机会规模。"),
    "metric-diagnostics": ("指标异常诊断", "复算指标并验证驱动因素，解释变化、异常、差距和口径不一致。"),
    "openai-docs": ("OpenAI 官方文档", "查询 OpenAI 官方文档、选择模型并迁移 OpenAI API 集成。"),
    "pdf": ("PDF 处理", "读取、创建和检查 PDF，并通过页面渲染验证内容与版式。"),
    "playwright": ("Playwright 浏览器自动化", "通过真实浏览器完成网页导航、表单填写、截图、抓取和界面流程调试。"),
    "plugin-creator": ("插件创建器", "创建 Codex 插件目录、manifest 和 marketplace 条目。"),
    "presentations": ("演示文稿", "创建和编辑 PowerPoint 或 Google Slides 目标演示文稿。"),
    "Presentations": ("演示文稿", "创建和编辑 PowerPoint 或 Google Slides 目标演示文稿。"),
    "product-business-analysis": ("产品与业务分析", "分析产品或业务数据，形成有证据支持的判断和行动建议。"),
    "prompt-optimizer": ("提示词优化器", "分析原始 prompt，补齐意图、约束和上下文，输出可直接使用的优化版。"),
    "report-to-google-doc": ("报告转 Google 文档", "把现有 HTML 分析报告转换成 Google Docs 或 DOCX 交付物。"),
    "report-to-google-slides": ("报告转 Google 幻灯片", "把现有 HTML 分析报告转换成简洁的 Google Slides 演示文稿。"),
    "report-to-pdf": ("报告转 PDF", "把数据分析 HTML 报告或导出结果转换成经过验证的 PDF。"),
    "seedance-ugc-cn-director": ("Seedance UGC 中文导演", "为 Seedance、即梦等 AI 工具生成本地化 UGC 短视频广告方案。"),
    "skill-creator": ("技能创建器", "创建或更新 Codex skill，把常用工作流程封装成可复用技能。"),
    "skill-installer": ("技能安装器", "从精选列表或 GitHub 仓库安装 Codex skills 到本机。"),
    "spreadsheets": ("表格处理", "创建、编辑、分析和可视化 Excel、CSV 或 Google Sheets 目标表格。"),
    "Spreadsheets": ("表格处理", "创建、编辑、分析和可视化 Excel、CSV 或 Google Sheets 目标表格。"),
    "user-context": ("数据分析用户配置", "管理数据源路由、初始设置和语义层配置。"),
    "using-superpowers": ("技能调用规则", "帮助 Codex 判断什么时候应该启用哪个 skill。"),
    "validate-data": ("数据验证", "检查分析逻辑、指标口径、图表和结论是否正确且证据充分。"),
    "visualize-data": ("数据可视化", "设计和检查分析图表的编码、标签、比较方式与读者结论。"),
    "watch-video": ("视频分析管线", "通过 /watch-video 运行视频下载、抽帧、转录和分析流程。"),
    "website-to-hyperframes": ("网页转视频", "抓取网站并创建 HyperFrames 产品介绍、教程或广告视频。"),
    "yeet": ("发布本地改动", "确认改动范围，提交、推送分支并打开 draft PR。"),
}

PLUGIN_TRANSLATIONS = {
    "browser": {
        "displayName": "内置浏览器",
        "shortDescription": "让 Codex 操作内置浏览器",
        "longDescription": "用于打开、检查、点击、输入和截图本地开发页面、localhost 页面和文件页面，适合前端测试与页面验证。",
    },
    "chrome": {
        "displayName": "Chrome 浏览器",
        "shortDescription": "操作用户自己的 Chrome 浏览器",
        "longDescription": "用于需要登录态、Cookie、浏览器扩展或已有标签页的网页任务，可在你的 Chrome 环境中点击、输入、检查和截图。",
    },
    "computer-use": {
        "displayName": "电脑操作",
        "shortDescription": "控制本地 Mac 应用",
        "longDescription": "让 Codex 通过屏幕操作本地 Mac 应用，执行点击、输入、滚动、拖拽、读取界面和设置参数等任务。",
    },
    "documents": {
        "displayName": "文档",
        "shortDescription": "创建和编辑 Word 或 Google Docs 文档",
        "longDescription": "用于创建、编辑、检查、渲染、验证和导出 DOCX 文档。适合报告、备忘录、方案、Word 文件和 Google Docs 目标文档。",
    },
    "github": {
        "displayName": "GitHub",
        "shortDescription": "处理 PR、Issue、CI 和发布流程",
        "longDescription": "用于查看仓库、审查 Pull Request、处理评审反馈、调试 GitHub Actions 失败检查，并准备代码改动用于提交和评审。",
    },
    "heygen": {
        "displayName": "HeyGen 数字人",
        "shortDescription": "创建数字人视频和个性化视频消息",
        "longDescription": "用于创建 HeyGen 数字人、头像视频、个性化视频消息、视频翻译和口型同步等视频工作流。",
    },
    "hyperframes": {
        "displayName": "HyperFrames 视频",
        "shortDescription": "用 HTML 和动画制作视频",
        "longDescription": "用于编写 HTML 视频合成、动画、标题卡、字幕、旁白、音频反应视觉、场景转场，以及把网站转成视频。",
    },
    "data-analytics": {
        "displayName": "数据分析",
        "shortDescription": "分析数据并创建报告、图表和仪表盘",
        "longDescription": "用于分析产品和业务数据、诊断指标变化、设计 KPI、测算市场规模，并创建经过验证的图表、报告、笔记本和仪表盘。",
    },
    "gmail": {
        "displayName": "Gmail 邮箱",
        "shortDescription": "整理邮件、总结线程并起草回复",
        "longDescription": "用于搜索和总结 Gmail 邮件线程、提取决策与待办事项、整理收件箱，并在发送前起草回复或转发内容。",
    },
    "google-drive": {
        "displayName": "Google 云端硬盘",
        "shortDescription": "统一处理 Drive、Docs、Sheets 和 Slides",
        "longDescription": "用于查找、读取、创建、编辑和整理 Google Drive 文件，并通过统一工作流处理 Google Docs、Sheets 和 Slides。",
    },
    "presentations": {
        "displayName": "演示文稿",
        "shortDescription": "创建和编辑 PPT 演示文稿",
        "longDescription": "用于创建、编辑、渲染、检查和导出 PowerPoint、PPTX 或 Google Slides 目标演示文稿。",
    },
    "spreadsheets": {
        "displayName": "表格",
        "shortDescription": "创建和分析 Excel 或表格文件",
        "longDescription": "用于创建、编辑、分析、可视化、渲染和导出 Excel、CSV、TSV 或 Google Sheets 目标表格。",
    },
}

DISPLAY_ALIASES = {
    "Browser": "browser",
    "CI Debug": "gh-fix-ci",
    "Documents": "documents",
    "GitHub": "github",
    "GSAP": "gsap",
    "Hatch Pet": "hatch-pet",
    "HeyGen": "heygen",
    "HeyGen Avatar": "heygen-avatar",
    "HeyGen Video": "heygen-video",
    "HyperFrames": "hyperframes",
    "HyperFrames CLI": "hyperframes-cli",
    "HyperFrames Registry": "hyperframes-registry",
    "Image Gen": "imagegen",
    "OpenAI Docs": "openai-docs",
    "Plugin Creator": "plugin-creator",
    "Presentations": "presentations",
    "Publish Changes": "yeet",
    "Review Follow-up": "gh-address-comments",
    "Seedance UGC 中文导演": "seedance-ugc-cn-director",
    "Skill Creator": "skill-creator",
    "Skill Installer": "skill-installer",
    "Spreadsheets": "spreadsheets",
    "Website to HyperFrames": "website-to-hyperframes",
}


def generic_plugin_translation(data: dict) -> dict:
    interface = data.get("interface") if isinstance(data.get("interface"), dict) else {}
    name = str(data.get("name") or "").strip()
    display = str(interface.get("displayName") or name.replace("-", " ").title()).strip()
    description = " ".join(
        str(value or "")
        for value in [
            data.get("description"),
            interface.get("shortDescription"),
            interface.get("longDescription"),
            " ".join(data.get("keywords") or []),
            interface.get("category"),
            name,
        ]
    ).lower()

    def has_phrase(phrases: list[str]) -> bool:
        return any(phrase in description for phrase in phrases)

    def has_word(words: list[str]) -> bool:
        return any(re.search(rf"\b{re.escape(word)}\b", description) for word in words)

    if has_phrase(["database", "data warehouse", "analytics", "dashboard", "spreadsheet"]) or has_word(["sql", "query", "postgres", "dataset", "datasets"]):
        purpose = "连接数据源，进行查询、分析、报表和数据处理"
    elif has_phrase(["design", "figma", "canva", "image", "video", "creative", "asset", "biorender", "cloudinary"]):
        purpose = "处理设计、视觉素材、图片、视频和创意生产"
    elif has_phrase(["deploy", "deployment", "cloudflare", "vercel", "netlify", "render", "supabase", "neon", "github", "circleci", "coderabbit", "sentry", "datadog"]) or has_word(["code", "repo", "android", "ios", "macos"]):
        purpose = "辅助软件开发、部署、代码协作、监控和工程排查"
    elif has_phrase(["earnings", "financial market", "market data", "public market", "capital market", "stock", "crypto", "trading", "investment", "investor", "equity", "finance"]):
        purpose = "查询和分析金融市场、公司信息、交易数据或投资研究资料"
    elif has_phrase(["crm", "sales", "prospect", "lead", "account", "contact", "customer", "outreach", "revenue", "marketing", "social media"]):
        purpose = "管理客户、销售线索、账号研究、联系人和外联信息"
    elif has_phrase(["email", "calendar", "meeting", "slack", "teams", "gmail", "outlook", "notion", "asana", "jira", "confluence", "sharepoint", "planner", "task"]):
        purpose = "处理办公协作、消息、会议、任务、日程和团队知识"
    elif has_phrase(["research", "paper", "citation", "science", "life science", "zotero", "scite", "literature"]):
        purpose = "进行资料检索、学术研究、文献整理和研究分析"
    elif has_phrase(["support", "ticket", "help", "service", "feedback"]):
        purpose = "处理客服、工单、用户反馈和服务流程"
    else:
        category = str(interface.get("category") or data.get("category") or "").lower()
        if category == "coding":
            purpose = "辅助开发、自动化、工程管理和技术工作流"
        elif category == "design":
            purpose = "辅助设计、创作和视觉内容生产"
        elif category == "research":
            purpose = "辅助研究、资料整理和信息分析"
        else:
            purpose = "把外部工具或服务连接到 Codex，让 Codex 能读取、整理或操作相关工作流"

    return {
        "displayName": display,
        "shortDescription": f"连接 {display}，用于{purpose}",
        "longDescription": f"这个插件把 {display} 接入 Codex，主要用于{purpose}。具体能力取决于插件权限、账号连接状态和该服务提供的接口。",
    }


def plugin_translation(data: dict) -> dict:
    key = data.get("name")
    if key in PLUGIN_TRANSLATIONS:
        return PLUGIN_TRANSLATIONS[key]
    interface = data.get("interface") if isinstance(data.get("interface"), dict) else {}
    short = interface.get("shortDescription")
    long = interface.get("longDescription")
    if isinstance(short, str) and isinstance(long, str) and short.startswith("连接 ") and long.startswith("这个插件把 "):
        return {
            "displayName": str(interface.get("displayName") or data.get("name") or ""),
            "shortDescription": short,
            "longDescription": long,
        }
    return generic_plugin_translation(data)


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_yaml_field(text: str, field: str) -> str | None:
    match = re.search(rf"(?m)^(\s*{re.escape(field)}:\s*)(.+?)\s*$", text)
    if not match:
        return None
    raw = match.group(2).strip()
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    return raw


def replace_yaml_field(text: str, field: str, value: str) -> str:
    pattern = rf"(?m)^(\s*{re.escape(field)}:\s*)(.+?)\s*$"
    replacement = rf"\1{yaml_quote(value)}"
    if re.search(pattern, text):
        return re.sub(pattern, replacement, text, count=1)
    display_line = re.search(r"(?m)^(\s*display_name:\s*.+?)\s*$", text)
    if display_line:
        insert_at = display_line.end()
        indent = re.match(r"^(\s*)", display_line.group(0)).group(1)
        return text[:insert_at] + f"\n{indent}{field}: {yaml_quote(value)}" + text[insert_at:]
    return text.rstrip() + f"\n  {field}: {yaml_quote(value)}\n"


def skill_id_from_skill_md(skill_dir: Path) -> str:
    text = read_text(skill_dir / "SKILL.md")
    match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)['\"]?\s*$", text)
    if match:
        return match.group(1).strip()
    return skill_dir.name


def translation_key_for_yaml(path: Path, text: str) -> str | None:
    display = parse_yaml_field(text, "display_name")
    if display in DISPLAY_ALIASES:
        return DISPLAY_ALIASES[display]
    # For ".../<skill-id>/agents/openai.yaml", only the skill directory is a
    # reliable key. The parent folder is literally named "agents", which is also
    # a real skill id on this machine, so scanning every path part is unsafe.
    if len(path.parents) >= 2:
        skill_dir_name = path.parents[1].name
        if skill_dir_name in TRANSLATIONS:
            return skill_dir_name
    return None


def discover_targets() -> list[dict]:
    targets: dict[Path, dict] = {}

    for root in TARGET_ROOTS:
        if not root.exists():
            continue
        for yaml_path in root.rglob("agents/openai.yaml"):
            text = read_text(yaml_path)
            key = translation_key_for_yaml(yaml_path, text)
            if key and key in TRANSLATIONS:
                targets[yaml_path] = {"path": yaml_path, "key": key, "exists": True}

        for skill_md in root.rglob("SKILL.md"):
            skill_dir = skill_md.parent
            key = skill_id_from_skill_md(skill_dir)
            if key not in TRANSLATIONS:
                continue
            yaml_path = skill_dir / "agents" / "openai.yaml"
            targets.setdefault(yaml_path, {"path": yaml_path, "key": key, "exists": yaml_path.exists()})

    return sorted(targets.values(), key=lambda item: str(item["path"]))


def discover_skills() -> dict[str, list[str]]:
    skills: dict[str, list[str]] = {}
    for root in TARGET_ROOTS:
        if not root.exists():
            continue
        for skill_md in root.rglob("SKILL.md"):
            try:
                key = skill_id_from_skill_md(skill_md.parent)
            except (OSError, UnicodeError):
                continue
            skills.setdefault(key, []).append(str(skill_md))
    return dict(sorted(skills.items()))


def discover_plugin_targets() -> list[dict]:
    targets = []
    seen = set()
    for root in PLUGIN_MANIFEST_ROOTS:
        if not root.exists():
            continue
        for plugin_json in root.rglob(".codex-plugin/plugin.json"):
            if plugin_json in seen:
                continue
            seen.add(plugin_json)
            try:
                data = json.loads(read_text(plugin_json))
            except json.JSONDecodeError:
                continue
            key = data.get("name")
            if isinstance(key, str) and key.strip():
                targets.append({"path": plugin_json, "key": key, "kind": "plugin"})
    return sorted(targets, key=lambda item: str(item["path"]))


def pending_changes() -> tuple[int, list[dict], list[dict]]:
    skill_targets = discover_targets()
    plugin_targets = discover_plugin_targets()
    changed = 0
    for item in skill_targets:
        path = item["path"]
        exists = path.exists()
        old_text = read_text(path) if exists else None
        if old_text != patched_text(path, item["key"], exists):
            changed += 1
    for item in plugin_targets:
        path = item["path"]
        if read_text(path) != patched_plugin_text(path, item["key"]):
            changed += 1
    return changed, skill_targets, plugin_targets


def patched_text(path: Path, key: str, exists: bool) -> str:
    display_name, short_description = TRANSLATIONS[key]
    if exists:
        text = read_text(path)
    else:
        text = "interface:\n"
    text = replace_yaml_field(text, "display_name", display_name)
    text = replace_yaml_field(text, "short_description", short_description)
    return text


def patched_plugin_text(path: Path, key: str) -> str:
    data = json.loads(read_text(path))
    translation = plugin_translation(data)
    interface = data.setdefault("interface", {})
    interface["displayName"] = translation["displayName"]
    interface["shortDescription"] = translation["shortDescription"]
    interface["longDescription"] = translation["longDescription"]
    data["description"] = translation["longDescription"]
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def latest_backup_dir() -> Path:
    if not BACKUP_ROOT.exists():
        raise SystemExit("No backup directory found.")
    candidates = [p for p in BACKUP_ROOT.iterdir() if p.is_dir() and (p / "manifest.json").exists()]
    if not candidates:
        raise SystemExit("No usable backup found.")
    return sorted(candidates)[-1]


def backup_file(src: Path, backup_dir: Path, manifest_entries: list[dict]) -> None:
    try:
        rel = src.relative_to(HOME)
    except ValueError:
        rel = Path("external") / Path(*src.parts[1:])
    dst = backup_dir / "files" / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dst)
        existed = True
    else:
        existed = False
    manifest_entries.append({
        "path": str(src),
        "backup_path": str(dst),
        "existed": existed,
    })


def cmd_status(_: argparse.Namespace) -> None:
    targets = discover_targets()
    plugin_targets = discover_plugin_targets()
    print(f"Skill targets: {len(targets)}")
    for item in targets:
        path = item["path"]
        key = item["key"]
        display_name, short_description = TRANSLATIONS[key]
        state = "update" if path.exists() else "create"
        print(f"[{state}] {path}")
        print(f"  -> {display_name} | {short_description}")
    print(f"Plugin targets: {len(plugin_targets)}")
    for item in plugin_targets:
        path = item["path"]
        translation = plugin_translation(json.loads(read_text(path)))
        print(f"[update] {path}")
        print(f"  -> {translation['displayName']} | {translation['shortDescription']}")


def cmd_scan(_: argparse.Namespace) -> None:
    skills = discover_skills()
    changed, skill_targets, plugin_targets = pending_changes()
    unmapped = sorted(set(skills) - set(TRANSLATIONS))
    existing_roots = [str(path) for path in TARGET_ROOTS + PLUGIN_MANIFEST_ROOTS if path.exists()]
    print(f"platform: {platform.system()}")
    print(f"codex_home: {CODEX_HOME}")
    print(f"existing_roots: {len(set(existing_roots))}")
    print(f"skills_discovered: {len(skills)}")
    print(f"skill_targets: {len(skill_targets)}")
    print(f"plugin_manifests: {len(plugin_targets)}")
    print(f"unmapped_skills: {len(unmapped)}")
    if unmapped:
        print("unmapped_names: " + ", ".join(unmapped))
    print(f"would_change: {changed}")


def cmd_apply(args: argparse.Namespace) -> None:
    if not args.dry_run and not args.confirm:
        raise SystemExit("Refusing to apply without --confirm after the user reviews a scan.")
    targets = [] if args.plugins_only else discover_targets()
    plugin_targets = [] if args.skills_only else discover_plugin_targets()
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_ROOT / timestamp
    manifest_entries: list[dict] = []
    changed = 0

    for item in targets:
        path = item["path"]
        key = item["key"]
        exists = path.exists()
        new_text = patched_text(path, key, exists)
        old_text = read_text(path) if exists else None
        if old_text == new_text:
            continue
        if not args.dry_run:
            backup_file(path, backup_dir, manifest_entries)
        if not args.dry_run:
            write_text(path, new_text)
        changed += 1

    for item in plugin_targets:
        path = item["path"]
        key = item["key"]
        new_text = patched_plugin_text(path, key)
        old_text = read_text(path)
        if old_text == new_text:
            continue
        if not args.dry_run:
            backup_file(path, backup_dir, manifest_entries)
        if not args.dry_run:
            write_text(path, new_text)
        changed += 1

    if changed and not args.dry_run:
        manifest = {
            "created_at": timestamp,
            "target_roots": [str(p) for p in TARGET_ROOTS],
            "entries": manifest_entries,
        }
        write_text(backup_dir / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    mode = "would change" if args.dry_run else "changed"
    print(f"{mode}: {changed}")
    if changed and not args.dry_run:
        print(f"backup: {backup_dir}")
    print("Restart Codex desktop app if the UI does not refresh immediately.")


def cmd_restore(args: argparse.Namespace) -> None:
    if not args.dry_run and not args.confirm:
        raise SystemExit("Refusing to restore without --confirm after the user reviews the backup.")
    backup_dir = Path(args.backup_dir).expanduser() if args.backup_dir else latest_backup_dir()
    manifest_path = backup_dir / "manifest.json"
    manifest = json.loads(read_text(manifest_path))
    restored = 0
    removed = 0

    for entry in manifest["entries"]:
        path = Path(entry["path"])
        backup_path = Path(entry["backup_path"])
        if entry["existed"]:
            if not args.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_path, path)
            restored += 1
        else:
            if path.exists():
                if not args.dry_run:
                    path.unlink()
                removed += 1

    mode = "would restore" if args.dry_run else "restored"
    print(f"{mode}: {restored}, removed created files: {removed}")
    print(f"from backup: {backup_dir}")
    print("Restart Codex desktop app if the UI does not refresh immediately.")


def cmd_backups(_: argparse.Namespace) -> None:
    if not BACKUP_ROOT.exists():
        print(f"backup_root: {BACKUP_ROOT}")
        print("backups: 0")
        return
    candidates = sorted(
        path for path in BACKUP_ROOT.iterdir()
        if path.is_dir() and (path / "manifest.json").exists()
    )
    print(f"backup_root: {BACKUP_ROOT}")
    print(f"backups: {len(candidates)}")
    for path in candidates:
        manifest = json.loads(read_text(path / "manifest.json"))
        print(f"{path}\tentries={len(manifest.get('entries', []))}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chinese UI metadata patcher for Codex plugins and skills.")
    subparsers = parser.add_subparsers(required=True)

    scan = subparsers.add_parser("scan", help="Show concise read-only counts and pending changes.")
    scan.set_defaults(func=cmd_scan)

    status = subparsers.add_parser("status", help="Show files that can be patched.")
    status.set_defaults(func=cmd_status)

    apply = subparsers.add_parser("apply", help="Backup and patch UI metadata into Chinese.")
    apply.add_argument("--dry-run", action="store_true", help="Show how many files would change without writing.")
    apply.add_argument("--confirm", action="store_true", help="Confirm applying the previously reviewed scan.")
    apply.add_argument("--plugins-only", action="store_true", help="Patch plugin page metadata only.")
    apply.add_argument("--skills-only", action="store_true", help="Patch skill page metadata only.")
    apply.set_defaults(func=cmd_apply)

    restore = subparsers.add_parser("restore", help="Restore from the latest backup, or a specific backup directory.")
    restore.add_argument("--backup-dir", help="Backup directory to restore from.")
    restore.add_argument("--dry-run", action="store_true", help="Show what would restore without writing.")
    restore.add_argument("--confirm", action="store_true", help="Confirm restoring the previously reviewed backup.")
    restore.set_defaults(func=cmd_restore)

    backups = subparsers.add_parser("backups", help="List available translation backups.")
    backups.set_defaults(func=cmd_backups)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

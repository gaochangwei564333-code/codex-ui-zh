# Codex UI 中文汉化

`codex-ui-zh` 是一个 Codex Skill，用于扫描、备份并汉化 Codex 插件页和技能页的名称与描述。

## 特点

- 先扫描并展示预计修改数量，用户确认后才写入
- 自动备份所有修改文件
- 支持恢复指定备份
- 自动识别当前用户的 Codex 目录
- 支持插件更新后重新补充汉化
- 不修改 `Codex.app`、`app.asar` 或应用签名

## 安装

克隆仓库到 Codex skills 目录：

```bash
git clone https://github.com/gaochangwei564333-code/codex-ui-zh.git ~/.codex/skills/codex-ui-zh
```

重启 Codex，然后输入：

```text
使用 $codex-ui-zh 更新汉化
```

也可以手动运行只读扫描：

```bash
python3 ~/.codex/skills/codex-ui-zh/scripts/codex_ui_zh_patch.py scan
```

## 工作流程

1. 扫描已安装技能、插件缓存、Marketplace 源和 Primary Runtime。
2. 显示技能数量、插件数量、未映射技能和预计修改文件数。
3. 等待用户明确确认。
4. 创建时间戳备份并应用中文显示元数据。
5. 再次扫描，验证 `would_change: 0`。

## 恢复

列出备份：

```bash
python3 ~/.codex/skills/codex-ui-zh/scripts/codex_ui_zh_patch.py backups
```

恢复指定备份：

```bash
python3 ~/.codex/skills/codex-ui-zh/scripts/codex_ui_zh_patch.py restore \
  --backup-dir ~/.codex/backups/codex-ui-zh/<时间戳> \
  --confirm
```

## 安全边界

该技能只修改插件和技能的本地显示元数据，不修改 Codex 应用包。部分内置推荐卡片可能写在 `app.asar` 中，因此不会被本技能汉化。

Codex 或插件更新可能覆盖本地中文元数据，重新调用技能即可再次扫描和应用。

## 兼容性

- 主要支持 macOS Codex Desktop
- 需要 Python 3
- 其他系统在未发现目标目录时只会报告结果，不会创建猜测路径

## License

MIT

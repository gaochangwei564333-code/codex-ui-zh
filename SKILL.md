---
name: codex-ui-zh
description: "Scan, preview, apply, verify, and restore Chinese display metadata for Codex plugin and skill pages. Use when the user asks to 汉化 Codex 插件页或技能页, update Chinese descriptions after Codex plugins or skills change, scan new Codex plugins/skills for untranslated UI metadata, or restore a previous Codex UI translation backup. Always scan and report counts first, then wait for explicit confirmation before applying or restoring."
---

# Codex UI Chinese Translation

Use the bundled script to update plugin and skill display metadata without modifying the Codex application bundle.

## Locate the script

Resolve the script relative to this skill directory:

```text
scripts/codex_ui_zh_patch.py
```

Use `python3`. Do not assume the caller's working directory.

## Scan first

Run:

```bash
python3 <skill-dir>/scripts/codex_ui_zh_patch.py scan
```

Report:

- discovered skill count
- mapped skill target count
- plugin manifest count
- unmapped skill names
- number of files that would change

Do not apply changes in the same turn unless the user had already explicitly confirmed applying the exact scan result. Ask for confirmation after showing the counts.

## Apply after confirmation

Only after explicit confirmation, run:

```bash
python3 <skill-dir>/scripts/codex_ui_zh_patch.py apply --confirm
```

If filesystem permissions block writes, request permission for this exact command. Never use `--no-backup` or modify `Codex.app`.

Then run:

```bash
python3 <skill-dir>/scripts/codex_ui_zh_patch.py scan
```

Success requires `would_change: 0`. Report the backup directory and restart guidance.

## Restore

First list backups:

```bash
python3 <skill-dir>/scripts/codex_ui_zh_patch.py backups
```

Show the selected backup and wait for explicit confirmation. Then run:

```bash
python3 <skill-dir>/scripts/codex_ui_zh_patch.py restore --backup-dir <backup-dir> --confirm
```

## Safety rules

- Treat `scan`, `status`, and `backups` as read-only.
- Require current-turn confirmation for `apply` and `restore`.
- Always create a backup before applying.
- Do not patch `/Applications/Codex.app`, `app.asar`, signatures, menus, or integrity metadata.
- Preserve unknown skill metadata and report it as unmapped.
- Permit generic Chinese descriptions for unknown plugins while preserving their brand names.
- Use `Path.home()` and `CODEX_HOME`; never hardcode a username.
- On unsupported systems or missing directories, report what was not found instead of creating guessed Codex directories.

## Sharing

The entire `codex-ui-zh` folder is self-contained. Another user can install the folder into `${CODEX_HOME:-~/.codex}/skills/`, restart Codex, and invoke `$codex-ui-zh`.

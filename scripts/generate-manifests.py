#!/usr/bin/env python3
"""Generate the marketplace manifest and one plugin.json per skill.

Layout (source of truth = the SKILL.md files):
    plugins/<skill>/skills/<skill>/SKILL.md         # the skill (hand-edited)
    plugins/<skill>/.claude-plugin/plugin.json      # GENERATED
    .claude-plugin/marketplace.json                 # GENERATED

Re-run after adding, removing, or editing a skill's frontmatter:
    python3 scripts/generate-manifests.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO / "plugins"
MARKETPLACE_NAME = "panteparak-skills"
OWNER = "panteparak"
VERSION = "0.1.0"


def read_description(skill_md: Path) -> str:
    """Pull the `description:` field from a SKILL.md YAML frontmatter block."""
    text = skill_md.read_text(encoding="utf-8")
    m = re.search(r"^---\s*$(.*?)^---\s*$", text, re.DOTALL | re.MULTILINE)
    block = m.group(1) if m else text
    dm = re.search(r"^description:\s*(.+)$", block, re.MULTILINE)
    if not dm:
        return ""
    return dm.group(1).strip().strip("'\"")


def main() -> None:
    plugin_dirs = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir())
    entries = []

    for pdir in plugin_dirs:
        name = pdir.name
        skill_md = pdir / "skills" / name / "SKILL.md"
        if not skill_md.exists():
            print(f"  ! skip {name}: no skills/{name}/SKILL.md")
            continue
        description = read_description(skill_md)

        # per-plugin manifest
        manifest_dir = pdir / ".claude-plugin"
        manifest_dir.mkdir(exist_ok=True)
        plugin_json = {
            "name": name,
            "version": VERSION,
            "description": description,
            "author": {"name": OWNER},
        }
        (manifest_dir / "plugin.json").write_text(
            json.dumps(plugin_json, indent=2) + "\n", encoding="utf-8"
        )

        # marketplace entry
        entries.append(
            {
                "name": name,
                "source": f"./plugins/{name}",
                "description": description,
                "version": VERSION,
                "author": {"name": OWNER},
            }
        )

    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": {"name": OWNER},
        "metadata": {
            "description": "Pan Teparak's self-authored development skills, "
            "one plugin per skill for fine-grained per-repo enablement.",
            "version": VERSION,
        },
        "plugins": entries,
    }
    out_dir = REPO / ".claude-plugin"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "marketplace.json").write_text(
        json.dumps(marketplace, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Generated {len(entries)} plugins + marketplace.json")


if __name__ == "__main__":
    main()

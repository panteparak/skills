#!/usr/bin/env python3
"""Detect a project's stack and recommend (and optionally install) skills from catalog.json.

Usage:
    python3 recommend-skills.py [PROJECT_DIR] [--json] [--write] [--catalog PATH]

    PROJECT_DIR   project to inspect (default: current directory)
    --json        emit machine-readable JSON (consumed by the skills-setup skill)
    --write       merge marketplace skills into PROJECT_DIR/.claude/settings.json
                  (skills-cli / manual skills are printed as commands, never auto-run)
    --catalog     path to catalog.json (default: alongside this script)

Pure standard library — no third-party dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "vendor", ".venv", "venv", "env", "__pycache__",
    "dist", "build", ".next", ".nuxt", ".terraform", "target", ".dart_tool",
    ".gradle", ".idea", ".mypy_cache", ".pytest_cache", "coverage", ".turbo",
}
WALK_FILE_CAP = 20000        # stop walking after this many files (perf guard)
READ_BYTE_CAP = 2_000_000    # max bytes read for fileContains


# --------------------------------------------------------------------------- #
# Project scanning (cached relative-path list + helpers)
# --------------------------------------------------------------------------- #
class Project:
    def __init__(self, root: Path):
        self.root = root
        self._files: list[str] | None = None

    def files(self) -> list[str]:
        if self._files is None:
            out: list[str] = []
            for dirpath, dirnames, filenames in os.walk(self.root):
                dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
                for f in filenames:
                    rel = os.path.relpath(os.path.join(dirpath, f), self.root)
                    out.append(rel.replace(os.sep, "/"))
                    if len(out) >= WALK_FILE_CAP:
                        self._files = out
                        return out
            self._files = out
        return self._files

    def file_exists(self, rel: str) -> bool:
        return (self.root / rel).is_file()

    def read_text(self, rel: str) -> str:
        p = self.root / rel
        if not p.is_file():
            return ""
        try:
            with p.open("r", encoding="utf-8", errors="ignore") as fh:
                return fh.read(READ_BYTE_CAP)
        except OSError:
            return ""


def glob_to_re(pattern: str) -> re.Pattern:
    """Translate a glob (supporting ** ) to a full-path regex."""
    i, n, out = 0, len(pattern), "^"
    while i < n:
        if pattern[i:i + 3] == "**/":
            out += "(?:.*/)?"
            i += 3
        elif pattern[i:i + 2] == "**":
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        elif pattern[i] in ".[](){}+^$|\\":
            out += "\\" + pattern[i]
            i += 1
        else:
            out += pattern[i]
            i += 1
    return re.compile(out + "$")


def glob_match(project: Project, pattern: str) -> bool:
    rx = glob_to_re(pattern)
    return any(rx.match(rel) for rel in project.files())


def json_dep(project: Project, file: str, dep: str) -> bool:
    raw = project.read_text(file)
    if not raw:
        return False
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return False
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        block = data.get(key)
        if isinstance(block, dict) and dep in block:
            return True
    return False


def file_contains(project: Project, file: str, pattern: str) -> bool:
    text = project.read_text(file)
    return bool(text) and re.search(pattern, text) is not None


# --------------------------------------------------------------------------- #
# Predicate evaluation
# --------------------------------------------------------------------------- #
def evaluate(pred: dict, project: Project) -> bool:
    if "always" in pred:
        return bool(pred["always"])
    if "anyOf" in pred:
        return any(evaluate(p, project) for p in pred["anyOf"])
    if "allOf" in pred:
        return all(evaluate(p, project) for p in pred["allOf"])
    if "noneOf" in pred:
        return not any(evaluate(p, project) for p in pred["noneOf"])
    if "fileExists" in pred:
        return project.file_exists(pred["fileExists"])
    if "glob" in pred:
        return glob_match(project, pred["glob"])
    if "jsonDep" in pred:
        d = pred["jsonDep"]
        return json_dep(project, d["file"], d["dep"])
    if "fileContains" in pred:
        d = pred["fileContains"]
        return file_contains(project, d["file"], d["pattern"])
    return False


# --------------------------------------------------------------------------- #
# Installed-state detection (best effort)
# --------------------------------------------------------------------------- #
def installed_state() -> dict:
    home = Path.home()
    marketplaces: set[str] = set()
    plugins: set[str] = set()
    skills: set[str] = set()
    km = home / ".claude" / "plugins" / "known_marketplaces.json"
    if km.is_file():
        try:
            marketplaces = set(json.loads(km.read_text()).keys())
        except (OSError, json.JSONDecodeError):
            pass
    ip = home / ".claude" / "plugins" / "installed_plugins.json"
    if ip.is_file():
        try:
            data = json.loads(ip.read_text())
            plugins = set((data.get("plugins") or {}).keys())
        except (OSError, json.JSONDecodeError):
            pass
    for base in (home / ".agents" / "skills", home / ".claude" / "skills"):
        if base.is_dir():
            skills |= {p.name for p in base.iterdir()}
    return {"marketplaces": marketplaces, "plugins": plugins, "skills": skills}


def availability(sid: str, entry: dict, state: dict) -> str:
    """Return '', 'registered', or 'installed' describing what's already present."""
    if entry["type"] == "marketplace":
        mid = entry.get("marketplaceId", "")
        any_plugin = any(f"{p}@{mid}" in state["plugins"] for p in entry.get("plugins", []))
        if any_plugin:
            return "installed"
        if mid in state["marketplaces"]:
            return "registered"
    else:  # skills-cli / manual
        names = entry.get("skills", [sid])
        if any(n in state["skills"] for n in names):
            return "installed"
    return ""


# --------------------------------------------------------------------------- #
# Recommendation
# --------------------------------------------------------------------------- #
def recommend(catalog: dict, project: Project) -> dict:
    skills = catalog["skills"]
    reasons: dict[str, list[str]] = {}

    def add(ids, why):
        for sid in ids:
            if sid in skills:
                reasons.setdefault(sid, [])
                if why not in reasons[sid]:
                    reasons[sid].append(why)

    add(catalog.get("universal", []), "universal")
    detected = []
    for name, stack in catalog.get("stacks", {}).items():
        if evaluate(stack["detect"], project):
            label = stack.get("label", name)
            detected.append({"key": name, "label": label})
            add(stack.get("skills", []), label)

    state = installed_state()
    items = []
    for sid, why in reasons.items():
        entry = skills[sid]
        items.append({
            "id": sid,
            "repo": entry["repo"],
            "url": entry["url"],
            "type": entry["type"],
            "purpose": entry["purpose"],
            "stars": entry.get("stars"),
            "license": entry.get("license"),
            "note": entry.get("note", ""),
            "reasons": why,
            "available": availability(sid, entry, state),
            "command": entry.get("install") or entry.get("skillsCli", ""),
        })
    items.sort(key=lambda x: (x["type"], x["id"]))
    return {
        "project": str(project.root),
        "detectedStacks": detected,
        "recommendations": items,
        "gaps": catalog.get("gaps", []),
    }


# --------------------------------------------------------------------------- #
# --write: merge marketplace skills into <project>/.claude/settings.json
# --------------------------------------------------------------------------- #
def write_settings(catalog: dict, result: dict, project: Project) -> dict:
    skills = catalog["skills"]
    settings_path = project.root / ".claude" / "settings.json"
    settings: dict = {}
    if settings_path.is_file():
        try:
            settings = json.loads(settings_path.read_text())
        except json.JSONDecodeError:
            raise SystemExit(f"ERROR: {settings_path} is not valid JSON; not overwriting.")

    mkts = settings.setdefault("extraKnownMarketplaces", {})
    enabled = settings.setdefault("enabledPlugins", {})

    written, deferred = [], []
    for item in result["recommendations"]:
        entry = skills[item["id"]]
        if entry["type"] == "marketplace":
            mid = entry["marketplaceId"]
            mkts.setdefault(mid, {"source": {"source": "github", "repo": entry["repo"]}})
            for plugin in entry.get("plugins", []):
                enabled[f"{plugin}@{mid}"] = True
                written.append(f"{plugin}@{mid}")
        else:  # skills-cli / manual — surface the command, never auto-run
            deferred.append({"id": item["id"], "type": entry["type"], "command": item["command"]})

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return {"settingsPath": str(settings_path), "enabled": written, "deferred": deferred}


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
TYPE_LABEL = {"marketplace": "plugin marketplace", "skills-cli": "npx skills add", "manual": "manual"}


def render_report(result: dict) -> str:
    lines = [f"# Skill recommendations for {result['project']}", ""]
    stacks = result["detectedStacks"]
    lines.append("Detected stacks: " + (", ".join(s["label"] for s in stacks) or "none (universal only)"))
    lines.append("")
    by_status = {"to-install": [], "available": []}
    for it in result["recommendations"]:
        by_status["available" if it["available"] else "to-install"].append(it)

    def fmt(it):
        star = f"{it['stars']:,}★" if it.get("stars") else ""
        why = ", ".join(it["reasons"])
        head = f"  - {it['id']} ({TYPE_LABEL[it['type']]}{', ' + star if star else ''}) — {why}"
        body = f"      {it['purpose']}"
        cmd = f"      install: {it['command']}" if it["command"] else ""
        note = f"      note: {it['note']}" if it["note"] else ""
        return "\n".join(x for x in (head, body, cmd, note) if x)

    if by_status["to-install"]:
        lines.append("## Recommended (not yet installed)")
        lines += [fmt(it) for it in by_status["to-install"]]
        lines.append("")
    if by_status["available"]:
        lines.append("## Already available (registered/installed)")
        lines += [f"  - {it['id']} ({it['available']}) — {', '.join(it['reasons'])}" for it in by_status["available"]]
        lines.append("")
    if result["gaps"]:
        lines.append("## Coverage gaps (no strong popular skill)")
        lines += [f"  - {g}" for g in result["gaps"]]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description="Detect stack and recommend skills from catalog.json")
    ap.add_argument("project", nargs="?", default=".", help="project directory (default: cwd)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--write", action="store_true", help="merge marketplace skills into <project>/.claude/settings.json")
    ap.add_argument("--only", default="", help="comma-separated skill ids to keep (subset of recommendations)")
    ap.add_argument("--exclude", default="", help="comma-separated skill ids to drop")
    ap.add_argument("--catalog", default=str(Path(__file__).resolve().parent / "catalog.json"))
    args = ap.parse_args()

    root = Path(args.project).resolve()
    if not root.is_dir():
        raise SystemExit(f"ERROR: not a directory: {root}")
    catalog = json.loads(Path(args.catalog).read_text())
    project = Project(root)
    result = recommend(catalog, project)

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    exclude = {s.strip() for s in args.exclude.split(",") if s.strip()}
    if only:
        result["recommendations"] = [r for r in result["recommendations"] if r["id"] in only]
    if exclude:
        result["recommendations"] = [r for r in result["recommendations"] if r["id"] not in exclude]

    if args.write:
        result["written"] = write_settings(catalog, result, project)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_report(result))
        if args.write:
            w = result["written"]
            print(f"\nWrote {len(w['enabled'])} plugin(s) to {w['settingsPath']}")
            if w["deferred"]:
                print("Run these to finish (skills-cli / manual):")
                for d in w["deferred"]:
                    print(f"  - {d['command']}")


if __name__ == "__main__":
    main()

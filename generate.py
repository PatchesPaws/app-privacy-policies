#!/usr/bin/env python3
"""
Generate privacy policy HTML pages from per-app YAML configs.
Usage:
  python generate.py              # regenerate all apps
  python generate.py potion-sort  # regenerate one app only
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
APPS_DIR = ROOT / "apps"
TEMPLATES_DIR = ROOT / "templates"
DOCS_DIR = ROOT / "docs"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)


def load_app(yaml_path: Path) -> dict:
    with yaml_path.open() as f:
        data = yaml.safe_load(f)
    data["slug"] = yaml_path.stem
    return data


def render_policy(app: dict) -> None:
    out_dir = DOCS_DIR / app["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    html = env.get_template("policy.html.j2").render(**app)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"  generated: docs/{app['slug']}/index.html")


def render_index(apps: list[dict]) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = env.get_template("index.html.j2").render(apps=apps, generated_at=generated_at)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"  generated: docs/index.html")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate privacy policy pages")
    parser.add_argument("app", nargs="?", help="Slug of a single app to regenerate (omit for all)")
    args = parser.parse_args()

    DOCS_DIR.mkdir(exist_ok=True)

    if args.app:
        yaml_path = APPS_DIR / f"{args.app}.yaml"
        if not yaml_path.exists():
            print(f"Error: {yaml_path} not found", file=sys.stderr)
            sys.exit(1)
        app = load_app(yaml_path)
        render_policy(app)
        all_apps = [load_app(p) for p in sorted(APPS_DIR.glob("*.yaml"))]
        render_index(all_apps)
    else:
        yaml_paths = sorted(APPS_DIR.glob("*.yaml"))
        if not yaml_paths:
            print("No app YAML files found in apps/")
            sys.exit(0)
        apps = [load_app(p) for p in yaml_paths]
        for app in apps:
            render_policy(app)
        render_index(apps)

    print("Done.")


if __name__ == "__main__":
    main()

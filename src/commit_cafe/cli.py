"""CLI: render the cafe from a fetched or saved CafeState."""

import argparse
import os
import sys
from pathlib import Path

from defusedxml import ElementTree
from loguru import logger

from commit_cafe.render import render
from commit_cafe.state import CafeState


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="commit-cafe")
    sub = parser.add_subparsers(dest="command", required=True)
    rend = sub.add_parser("render", help="render SVG variants")
    rend.add_argument("--state", type=Path, help="CafeState JSON file (skips API fetch)")
    rend.add_argument("--username", help="GitHub username to fetch (requires GITHUB_TOKEN)")
    rend.add_argument("--out", type=Path, default=Path("dist"))
    args = parser.parse_args(argv)

    if args.state:
        state = CafeState.model_validate_json(args.state.read_text())
    elif args.username:
        from commit_cafe.collect import fetch_state

        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            logger.error("GITHUB_TOKEN is required with --username")
            return 1
        state = fetch_state(args.username, token)
    else:
        logger.error("provide --state or --username")
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    for mode in ("day", "night"):
        svg = render(state, mode)
        ElementTree.fromstring(svg)  # invalid XML must fail the run, not ship
        path = args.out / f"cafe-{mode}.svg"
        path.write_text(svg)
        logger.info("wrote {} ({} bytes)", path, path.stat().st_size)
    return 0


if __name__ == "__main__":
    sys.exit(main())

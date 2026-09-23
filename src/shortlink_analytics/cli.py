from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict

from . import __version__
from .app import create_app
from .core import Store


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="shortlink-analytics", description="Local short links with privacy-conscious analytics")
    p.add_argument("--db", default=os.getenv("SHORTLINK_DB", "shortlinks.db"), help="SQLite database path")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create", help="Create a short link"); c.add_argument("url"); c.add_argument("--slug")
    sub.add_parser("list", help="List links")
    s = sub.add_parser("stats", help="Show analytics"); s.add_argument("slug")
    for name in ("disable", "enable"):
        q = sub.add_parser(name, help=f"{name.title()} a link"); q.add_argument("slug")
    serve = sub.add_parser("serve", help="Run the HTTP service")
    serve.add_argument("--host", default="127.0.0.1"); serve.add_argument("--port", type=int, default=8080)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    store = Store(args.db)
    try:
        if args.command == "create":
            print(json.dumps(asdict(store.create(args.url, args.slug)), ensure_ascii=False, indent=2))
        elif args.command == "list":
            print(json.dumps([asdict(x) for x in store.list()], ensure_ascii=False, indent=2))
        elif args.command == "stats":
            print(json.dumps(store.stats(args.slug), ensure_ascii=False, indent=2))
        elif args.command in {"disable", "enable"}:
            if not store.set_active(args.slug, args.command == "enable"):
                raise KeyError(args.slug)
            print(f"{args.command}d {args.slug}")
        elif args.command == "serve":
            create_app({"DATABASE": args.db}).run(host=args.host, port=args.port, debug=False)
        return 0
    except (ValueError, KeyError) as exc:
        parser().error(str(exc))
    return 2

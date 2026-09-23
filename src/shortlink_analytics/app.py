from __future__ import annotations

import os
from flask import Flask, abort, jsonify, redirect, request

from .core import Store


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(DATABASE=os.getenv("SHORTLINK_DB", "shortlinks.db"))
    if config:
        app.config.update(config)
    store = Store(app.config["DATABASE"])
    store.init()

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/links")
    def links():
        return jsonify([x.__dict__ for x in store.list()])

    @app.get("/api/links/<slug>/stats")
    def stats(slug: str):
        try:
            return jsonify(store.stats(slug))
        except (KeyError, ValueError):
            abort(404)

    @app.get("/<slug>")
    def follow(slug: str):
        try:
            link = store.get(slug)
        except ValueError:
            abort(404)
        if link is None or not link.active:
            abort(404)
        store.record_click(slug, request.referrer, request.user_agent.string)
        return redirect(link.url, code=302)

    return app

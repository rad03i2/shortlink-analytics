from shortlink_analytics.app import create_app
from shortlink_analytics.core import Store


def test_redirect_records_click_and_api_reports_it(tmp_path):
    db = tmp_path / "web.db"
    Store(db).create("https://example.com/target", "target")
    app = create_app({"TESTING": True, "DATABASE": str(db)})
    client = app.test_client()
    response = client.get("/target", headers={"Referer": "https://source.example/path?private=yes"})
    assert response.status_code == 302
    assert response.location == "https://example.com/target"
    stats = client.get("/api/links/target/stats").get_json()
    assert stats["clicks"] == 1
    assert stats["referrers"][0]["source"] == "source.example"
    assert client.get("/health").get_json() == {"status": "ok"}


def test_missing_and_disabled_are_404(tmp_path):
    db = tmp_path / "web.db"; store = Store(db)
    store.create("https://example.com", "gone"); store.set_active("gone", False)
    client = create_app({"TESTING": True, "DATABASE": str(db)}).test_client()
    assert client.get("/gone").status_code == 404
    assert client.get("/missing").status_code == 404

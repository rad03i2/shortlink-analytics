import pytest

from shortlink_analytics.core import Store, validate_url


def test_create_get_list_and_stats(tmp_path):
    s = Store(tmp_path / "links.db")
    link = s.create("https://example.com/docs?a=1", "docs_1")
    assert link.slug == "docs_1"
    assert s.get("docs_1").url == "https://example.com/docs?a=1"
    s.record_click("docs_1", "https://search.example/path?q=secret", "Browser/1.0 details")
    stats = s.stats("docs_1")
    assert stats["clicks"] == 1
    assert stats["referrers"] == [{"source": "search.example", "count": 1}]
    assert len(s.list()) == 1


def test_disable_enable(tmp_path):
    s = Store(tmp_path / "x.db"); s.create("https://example.com", "hello")
    assert s.set_active("hello", False)
    assert not s.get("hello").active
    assert s.set_active("hello", True)


def test_validation_and_duplicate(tmp_path):
    with pytest.raises(ValueError): validate_url("javascript:alert(1)")
    with pytest.raises(ValueError): validate_url("https://user:pass@example.com")
    s = Store(tmp_path / "x.db"); s.create("https://example.com", "valid")
    with pytest.raises(ValueError): s.create("https://example.org", "valid")
    with pytest.raises(ValueError): s.create("https://example.org", "x")

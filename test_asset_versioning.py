"""Cache-busting contract: served HTML must fingerprint its CSS/JS URLs.

Without this, browsers keep serving the previously cached stylesheet after an
update, so users see stale styles until they manually hard-refresh.
"""

from pathlib import Path
import re

from fastapi.testclient import TestClient

from app.main import app


ROOT = Path(__file__).parent
client = TestClient(app)


def test_app_html_fingerprints_stylesheet_and_scripts():
    response = client.get("/app")
    assert response.status_code == 200
    body = response.text

    assert re.search(r'href="/css/app\.css\?v=\d+"', body), "stylesheet is not fingerprinted"
    assert re.search(r'src="/js/app\.js\?v=\d+"', body), "app.js is not fingerprinted"
    assert re.search(r'src="/js/i18n\.js\?v=\d+"', body), "i18n.js is not fingerprinted"

    # An unversioned reference would still be cacheable and defeat the purpose.
    assert 'href="/css/app.css"' not in body
    assert 'src="/js/app.js"' not in body


def test_served_document_is_always_revalidated():
    """New fingerprints are invisible if the HTML itself is served from cache."""
    response = client.get("/app")
    assert "no-cache" in response.headers.get("cache-control", "")


def test_fingerprint_tracks_file_changes():
    css = ROOT / "static" / "css" / "app.css"
    original = css.stat().st_mtime

    first = re.search(r'/css/app\.css\?v=(\d+)', client.get("/app").text).group(1)

    try:
        css.touch()
        bumped = re.search(r'/css/app\.css\?v=(\d+)', client.get("/app").text).group(1)
    finally:
        os_utime = __import__("os").utime
        os_utime(css, (original, original))

    assert bumped != first, "fingerprint must change when the asset changes"


def test_versioned_asset_is_still_served():
    version = re.search(r'/css/app\.css\?v=(\d+)', client.get("/app").text).group(1)
    response = client.get(f"/css/app.css?v={version}")

    assert response.status_code == 200
    assert ".bug-report-fab" in response.text

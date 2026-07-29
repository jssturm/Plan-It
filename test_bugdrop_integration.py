"""Static contract tests for the account-free, private BugDrop integration."""

from pathlib import Path
import re


ROOT = Path(__file__).parent
APP_HTML = (ROOT / "static" / "app.html").read_text(encoding="utf-8")
APP_JS = (ROOT / "static" / "js" / "app.js").read_text(encoding="utf-8")
I18N_JS = (ROOT / "static" / "js" / "i18n.js").read_text(encoding="utf-8")


def test_bugdrop_is_pinned_and_targets_private_intake():
    tag = re.search(
        r'<script\s+id="planit-bugdrop".*?</script>',
        APP_HTML,
        re.DOTALL,
    )
    assert tag, "BugDrop script tag is missing"
    markup = tag.group(0)

    assert "widget.v1.js" in markup
    assert 'data-repo="jssturm/elevated-applicant-feedback"' in markup
    assert 'data-button="false"' in markup
    assert 'data-screenshot="optional"' in markup
    assert 'data-send-console-logs="false"' in markup
    assert 'data-show-name="false"' in markup
    assert 'data-show-email="false"' in markup
    assert 'data-show-issue-link="never"' in markup
    assert "async" not in markup
    assert "defer" not in markup


def test_existing_button_opens_bugdrop_with_github_fallback():
    handler = re.search(
        r'\$bugBtn\.addEventListener\("click".*?\n\s*}\);',
        APP_JS,
        re.DOTALL,
    )
    assert handler, "Bug-report click handler is missing"
    source = handler.group(0)

    assert 'typeof window.BugDrop.open === "function"' in source
    assert "window.BugDrop.open()" in source
    assert "openBugReport()" in source


def test_sensitive_travel_surfaces_are_masked():
    sensitive_ids = (
        "sidebar-saved-plans",
        "trip-input",
        "trip-departure-ampm",
        "trip-start",
        "trip-restaurants",
        "result-new-trip",
        "plans-list",
        "plan-detail-title",
        "plan-detail-subtitle",
        "plan-detail-content",
        "modal-container",
    )

    for element_id in sensitive_ids:
        element = re.search(
            rf'<[^>]+(?=[^>]*id="{re.escape(element_id)}")'
            rf'(?=[^>]*data-bugdrop-mask)[^>]*>',
            APP_HTML,
        )
        assert element, f"#{element_id} must be marked for screenshot masking"

    assert 'class="modal" data-bugdrop-mask' in APP_JS


def test_bug_report_control_is_docked_in_the_sidebar_footer():
    """The sidebar paints over the bottom-left corner, so the control lives inside it."""
    footer = re.search(
        r'<div class="sidebar-footer">.*?</aside>',
        APP_HTML,
        re.DOTALL,
    )
    assert footer, "sidebar footer is missing"
    assert 'id="bug-report-fab"' in footer.group(0)
    assert 'id="btn-bug-report"' in footer.group(0)

    # A floating overlay would be hidden behind the sidebar again.
    assert "position: fixed" not in _bug_report_css()
    assert 'data-i18n="bug.sectionLabel"' in APP_HTML
    assert '"bug.sectionLabel"' in I18N_JS


def _bug_report_css() -> str:
    css = (ROOT / "static" / "css" / "app.css").read_text(encoding="utf-8")
    block = re.search(r"\.bug-report-fab \{.*?\}", css, re.DOTALL)
    assert block, ".bug-report-fab rule is missing"
    return block.group(0)


def test_fallback_privacy_copy_names_plan_it_data():
    assert "your CV, profile, application answers" not in I18N_JS
    assert "trip description, starting address" in I18N_JS
    assert "descripción del viaje, dirección inicial" in I18N_JS


def test_theme_sandbox_documents_ready_and_fallback_states():
    sandbox = (ROOT / "theme-sandbox" / "index.html").read_text(encoding="utf-8")
    assert "BugDrop ready" in sandbox
    assert "existing GitHub fallback" in sandbox
    assert "Toggle light/dark" in sandbox

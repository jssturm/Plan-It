"""WCAG 2.1 AA guard for the muted text token.

Muted text renders at 12px throughout the sidebar and form hints, so it must
meet the 4.5:1 normal-text minimum against every surface it can land on.
"""

from pathlib import Path
import re


CSS = (Path(__file__).parent / "static" / "css" / "app.css").read_text(encoding="utf-8")

SURFACE_TOKENS = (
    "--color-bg-primary",
    "--color-bg-secondary",
    "--color-bg-card",
    "--color-bg-card-hover",
    "--color-bg-input",
    "--color-bg-chip",
)

THEMES = (":root", "html.dark")


def _theme_block(selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{(.*?)\n\}}", CSS, re.DOTALL)
    assert match, f"{selector} token block not found"
    return match.group(1)


def _hex_token(block: str, name: str) -> str:
    match = re.search(rf"{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})", block)
    assert match, f"{name} not found or not a 6-digit hex"
    return match.group(1)


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(foreground: str, background: str) -> float:
    high, low = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)), reverse=True
    )
    return (high + 0.05) / (low + 0.05)


def test_muted_text_meets_aa_on_every_surface():
    failures = []
    for selector in THEMES:
        block = _theme_block(selector)
        muted = _hex_token(block, "--color-text-muted")
        for surface in SURFACE_TOKENS:
            ratio = _contrast(muted, _hex_token(block, surface))
            if ratio < 4.5:
                failures.append(f"{selector} {muted} on {surface}: {ratio:.2f}:1")

    assert not failures, "muted text below 4.5:1 -> " + "; ".join(failures)


def test_muted_stays_dimmer_than_secondary_text():
    """The visual hierarchy must survive the contrast fix."""
    for selector in THEMES:
        block = _theme_block(selector)
        surface = _relative_luminance(_hex_token(block, "--color-bg-card"))
        muted = _relative_luminance(_hex_token(block, "--color-text-muted"))
        secondary = _relative_luminance(_hex_token(block, "--color-text-secondary"))

        muted_distance = abs(muted - surface)
        secondary_distance = abs(secondary - surface)
        assert muted_distance < secondary_distance, (
            f"{selector}: muted text is no longer dimmer than secondary text"
        )

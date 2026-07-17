"""Cross-platform environment detection for macOS, Windows, Linux, iOS, and Android.

Provides a single ``check_environment()`` entry point that returns an
``Environment`` dataclass with all the details needed for a successful
install — OS info, Python version, available tools, write paths, and
network configuration.
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
import sysconfig
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Environment:
    """Detected runtime environment across all supported platforms."""

    system: str  # "linux", "darwin", "windows", "android", "ios"
    system_release: str
    machine: str  # "x86_64", "arm64", "aarch64", etc.
    python_version: str
    python_executable: str
    python_prefix: str
    is_virtualenv: bool
    is_wsl: bool = False
    is_termux: bool = False  # Android Termux
    is_ish: bool = False     # iOS iSH

    # Tool discoveries
    has_git: bool = False
    has_node: bool = False
    has_npm: bool = False
    has_docker: bool = False
    has_pip: bool = False

    # Write paths
    config_dir: str = ""
    data_dir: str = ""
    home_dir: str = ""

    # Network
    has_internet: bool = False

    # Warnings / notes
    warnings: List[str] = field(default_factory=list)


def _detect_system() -> tuple[str, str]:
    """Return (normalized_system, raw_release)."""
    raw_system = platform.system()
    release = platform.release() or "unknown"

    # Android detection (Termux, UserLAnd, etc.)
    if raw_system == "Linux":
        # Check for Android markers
        if hasattr(sys, "getandroidapilevel"):
            return ("android", release)
        cpuinfo = Path("/proc/cpuinfo")
        if cpuinfo.is_file():
            content = cpuinfo.read_text().lower()
            if "qualcomm" in content or "mediatek" in content or "qcom" in content:
                # Strong signal it's ARM Android
                if Path("/data/data/com.termux").is_dir() or "com.termux" in str(Path.home()):
                    return ("android", release)
        build_prop = Path("/system/build.prop")
        if build_prop.is_file():
            return ("android", release)
        if os.environ.get("ANDROID_ROOT") or os.environ.get("ANDROID_DATA"):
            return ("android", release)

        # Check for iOS via iSH
        if Path("/proc/ish").is_dir() or "ish.app" in (os.environ.get("PATH", "")):
            return ("ios", release)

    if raw_system == "Darwin":
        # iOS on Mac Catalyst / x86 simulator
        if os.environ.get("IPHONE_SIMULATOR_ROOT"):
            return ("ios", release)
        return ("darwin", release)

    if raw_system == "Windows":
        return ("windows", release)

    return ("linux", release)


def check_environment() -> Environment:
    """Run a full environment probe and return the result."""
    system, release = _detect_system()
    machine = platform.machine()

    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_exec = sys.executable
    py_prefix = sysconfig.get_config_var("prefix") or sys.prefix
    is_venv = (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        or os.environ.get("VIRTUAL_ENV") is not None
    )

    # WSL detection (windows subsystem for linux)
    is_wsl = False
    if system == "linux":
        version_file = Path("/proc/version")
        if version_file.is_file():
            content = version_file.read_text().lower()
            is_wsl = "microsoft" in content or "wsl" in content

    is_termux = system == "android" and "com.termux" in str(Path.home())
    is_ish = system == "ios" and Path("/proc/ish").is_dir()

    # Available tools
    has_git = shutil.which("git") is not None
    has_node = shutil.which("node") is not None
    has_npm = shutil.which("npm") is not None
    has_docker = shutil.which("docker") is not None
    has_pip = shutil.which("pip") is not None or shutil.which("pip3") is not None

    # Platform-aware config/data directories
    home = str(Path.home())
    if system == "darwin":
        config_dir = os.path.join(home, ".config", "plan-it")
        data_dir = os.path.join(home, "Library", "Application Support", "plan-it")
    elif system == "windows":
        appdata = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        config_dir = os.path.join(appdata, "plan-it")
        data_dir = config_dir
    elif system == "android":
        config_dir = os.path.join(home, ".config", "plan-it")
        data_dir = os.path.join(home, ".local", "share", "plan-it")
    elif system == "ios":
        config_dir = os.path.join(home, ".config", "plan-it")
        data_dir = os.path.join(home, ".local", "share", "plan-it")
    else:  # linux
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))
        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.join(home, ".local", "share"))
        config_dir = os.path.join(xdg_config, "plan-it")
        data_dir = os.path.join(xdg_data, "plan-it")

    # Warnings
    warnings: list[str] = []
    if sys.version_info < (3, 12):
        warnings.append(f"Python 3.12+ recommended (found {py_version})")
    if system == "android" and not is_termux:
        warnings.append("Android detected but Termux not confirmed — some features may be limited")
    if system == "ios" and not is_ish:
        warnings.append("iOS environment detected but iSH not confirmed")
    if is_wsl:
        warnings.append("WSL detected — network binding to 0.0.0.0 requires Windows Firewall rules")
    if not has_pip:
        warnings.append("pip not found on PATH — package installation will fail")

    return Environment(
        system=system,
        system_release=release,
        machine=machine,
        python_version=py_version,
        python_executable=py_exec,
        python_prefix=py_prefix,
        is_virtualenv=is_venv,
        is_wsl=is_wsl,
        is_termux=is_termux,
        is_ish=is_ish,
        has_git=has_git,
        has_node=has_node,
        has_npm=has_npm,
        has_docker=has_docker,
        has_pip=has_pip,
        config_dir=config_dir,
        data_dir=data_dir,
        home_dir=home,
        warnings=warnings,
    )


def format_env_report(env: Environment) -> str:
    """Produce a human-readable environment report."""
    platform_emoji = {
        "darwin": "🍎",
        "windows": "🪟",
        "linux": "🐧",
        "android": "🤖",
        "ios": "📱",
    }

    lines = [
        f"  System:       {platform_emoji.get(env.system, '?')} {env.system} {env.system_release} ({env.machine})",
        f"  Python:       {env.python_version}  ({env.python_executable})",
        f"  Venv:         {'yes' if env.is_virtualenv else 'no'}",
    ]

    if env.is_wsl:
        lines.append("  WSL:          yes")
    if env.is_termux:
        lines.append("  Termux:       yes (Android)")
    if env.is_ish:
        lines.append("  iSH:          yes (iOS)")

    lines += [
        f"  Config dir:   {env.config_dir}",
        f"  Data dir:     {env.data_dir}",
        f"  Home:         {env.home_dir}",
    ]

    return "\n".join(lines) + "\n"
from importlib import resources
import json
import logging
import os
from typing import Any

# These are still needed for render_platforms
galaxy_alls = {"alpine", "archlinux", "kali"}

galaxy_os_name = {
    "alpine": "Alpine",
    "archlinux": "ArchLinux",
    "debian": "Debian",
    "fedora": "Fedora",
    "kali": "Debian",
    "rockylinux": "EL",
    "ubi": "EL",
    "ubuntu": "Ubuntu",
}

# These will be populated from the default platform matrix if available
latest_pairs: dict[str, set[str]] = {}
upgrades: dict[str, dict[str, set[str]]] = {}
default_platforms: dict[tuple[str, str], str] = {}
default_upstream: dict[tuple[str, str], dict[str, str]] = {}


def load_default_platform_matrix() -> list[dict[str, Any]] | None:
    """Load the default platform matrix from the external JSON file."""
    log = logging.getLogger("ansible-galaxy-local-deps.platform_matrix")

    # First try to load from the package resources
    try:
        files = resources.files("ansible_galaxy_local_deps")
        default_matrix_file = files / "default-platform-matrix-v1.json"
        if default_matrix_file.is_file():
            log.info("Loading default platform matrix from package resources")
            return json.loads(default_matrix_file.read_text())
    except Exception as e:
        log.warning(f"Failed to load defaults from package resources: {e}")

    # Fall back to checking external locations for user overrides
    external_paths = [
        # In the current working directory
        "default-platform-matrix-v1.json",
        # In the user's home directory
        os.path.expanduser("~/default-platform-matrix-v1.json"),
    ]

    for path in external_paths:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    log.info(f"Loading default platform matrix from {path}")
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                log.error(f"Failed to load default platform matrix from {path}: {e}")

    log.warning("No default platform matrix file found, using built-in defaults")
    return None


def populate_defaults_from_matrix(matrix: list[dict[str, Any]]) -> None:
    """Populate the module-level defaults from the platform matrix."""
    global latest_pairs, upgrades, default_platforms, default_upstream

    # Reset to empty
    latest_pairs = {}
    upgrades = {}
    default_platforms = {}
    default_upstream = {}

    # Group by OS to find latest versions
    by_os: dict[str, list[dict[str, Any]]] = {}
    for entry in matrix:
        os = entry["OS"]
        by_os.setdefault(os, []).append(entry)

    # Populate latest_pairs and default_platforms
    for os, entries in by_os.items():
        versions = {e["OS_VER"] for e in entries}

        # For latest_pairs, use the last 2 versions (or all if less than 2)
        # Special handling for versions like "edge", "latest", etc
        special_versions = {"edge", "latest", "rolling", "rawhide"}
        regular_versions = [v for v in versions if v not in special_versions]

        if regular_versions:
            sorted_regular = sorted(regular_versions)
            if len(sorted_regular) >= 2:
                latest_pairs[os] = set(sorted_regular[-2:])
            else:
                latest_pairs[os] = set(sorted_regular)
        else:
            # If only special versions, use them
            latest_pairs[os] = versions

        # Populate upgrades
        # Special versions always stay as-is
        # For regular versions not in latest_pairs, they upgrade to latest_pairs
        # For versions in latest_pairs, they stay as-is
        upgrades[os] = {}
        for ver in versions:
            if ver in special_versions:
                # Special versions always stay as-is
                upgrades[os][ver] = {ver}
            elif ver in latest_pairs[os]:
                # Latest versions stay as-is
                upgrades[os][ver] = {ver}
            else:
                # Older versions upgrade to the latest pairs
                upgrades[os][ver] = latest_pairs[os]

        # Populate default_platforms and upstream info
        for entry in entries:
            key = (entry["OS"], entry["OS_VER"])
            if "PLATFORMS" in entry:
                default_platforms[key] = entry["PLATFORMS"]

            # Collect UPSTREAM_* fields
            upstream_fields = {
                k: v for k, v in entry.items() if k.startswith("UPSTREAM_")
            }
            if upstream_fields:
                default_upstream[key] = upstream_fields


# Initialize with built-in defaults
def _init_builtin_defaults() -> None:
    """Initialize with hardcoded defaults as fallback."""
    global latest_pairs, upgrades, default_platforms

    latest_pairs = {
        "alpine": {"3.21", "3.22"},
        "archlinux": {"latest"},
        "debian": {"bookworm", "bullseye"},
        "fedora": {"41", "42"},
        "kali": {"latest"},
        "rockylinux": {"9"},
        "ubi": {"9", "10"},
        "ubuntu": {"jammy", "noble"},
    }

    upgrades = {
        "alpine": {"3.21": {"3.21"}, "edge": {"edge"}},
        "debian": {"bookworm": {"bookworm"}},
        "fedora": {"41": {"41"}},
        "kali": {"latest": {"latest"}},
        "rockylinux": {"9": {"9"}},
        "ubi": {"9": {"9"}, "10": {"10"}},
        "ubuntu": {"noble": {"noble"}},
    }

    default_platforms = {
        # Alpine only supports linux/amd64
        ("alpine", "3.20"): "linux/amd64",
        ("alpine", "3.21"): "linux/amd64",
        ("alpine", "3.22"): "linux/amd64",
        ("alpine", "edge"): "linux/amd64",
        # ArchLinux only supports linux/amd64
        ("archlinux", "latest"): "linux/amd64",
        # Debian supports both linux/amd64 and linux/arm64
        ("debian", "bookworm"): "linux/amd64,linux/arm64",
        ("debian", "bullseye"): "linux/amd64,linux/arm64",
        # Fedora supports both linux/amd64 and linux/arm64
        ("fedora", "41"): "linux/amd64,linux/arm64",
        ("fedora", "42"): "linux/amd64,linux/arm64",
        # Kali only supports linux/amd64
        ("kali", "latest"): "linux/amd64",
        # Rocky Linux supports both linux/amd64 and linux/arm64
        ("rockylinux", "9"): "linux/amd64,linux/arm64",
        # UBI supports both linux/amd64 and linux/arm64
        ("ubi", "9"): "linux/amd64,linux/arm64",
        ("ubi", "10"): "linux/amd64,linux/arm64",
        # Ubuntu supports both linux/amd64 and linux/arm64
        ("ubuntu", "jammy"): "linux/amd64,linux/arm64",
        ("ubuntu", "noble"): "linux/amd64,linux/arm64",
    }


# Try to load from external file, fall back to built-in
_default_matrix = load_default_platform_matrix()
if _default_matrix:
    populate_defaults_from_matrix(_default_matrix)
else:
    _init_builtin_defaults()


def apply_default_platforms(pm: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply default platforms and upstream info to platform matrix entries."""
    for p in pm:
        key = (p["OS"], p["OS_VER"])

        # Apply default platforms if not already set
        if "PLATFORMS" not in p:
            p["PLATFORMS"] = default_platforms.get(key, "linux/amd64")

        # Apply upstream info if available and not already set
        if key in default_upstream:
            for k, v in default_upstream[key].items():
                if k not in p:
                    p[k] = v

    return pm


def upgrade(pm_in: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_os: dict[str, set[str]] = {}
    # Store all extra fields for each OS/OS_VER combo
    extras_map: dict[tuple[str, str], dict[str, Any]] = {}

    # apply upgrades and flatten to set
    for p in pm_in:
        os = p["OS"]
        bo = by_os.setdefault(os, set())

        os_ver = p["OS_VER"]

        # Store all extra fields (PLATFORMS, UPSTREAM_*, etc)
        extra_fields = {k: v for k, v in p.items() if k not in {"OS", "OS_VER"}}
        if extra_fields:
            extras_map[(os, os_ver)] = extra_fields

        if os in upgrades:
            ups = upgrades[os]
            if os_ver in ups:
                bo |= ups[os_ver]
            else:
                bo |= latest_pairs.get(os, {os_ver})
        else:
            bo |= {os_ver}

    pm_out = []
    # reinflate sets
    for os in sorted(by_os.keys()):
        for os_ver in sorted(by_os[os]):
            entry = {"OS": os, "OS_VER": os_ver}

            # Preserve extra fields if they were in the original
            if (os, os_ver) in extras_map:
                entry.update(extras_map[(os, os_ver)])

            pm_out.append(entry)

    # Apply default platforms and upstream info
    return apply_default_platforms(pm_out)


def from_dcb_osl(osl: list[str]) -> list[dict[str, Any]]:
    pm = []
    for o in osl:
        s = o.split("_")
        pm.append({"OS": s[0], "OS_VER": s[1]})
    # upgrade will also apply default platforms
    return upgrade(pm)


def render_platforms(pm: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_os: dict[str, set[str]] = {}
    for p in pm:
        os = p["OS"]
        os_name = galaxy_os_name[os]
        bo = by_os.setdefault(os_name, set())
        if os in galaxy_alls:
            bo |= {"all"}
        else:
            bo |= {p["OS_VER"]}

    # reinflate sets
    platforms = []
    for os_name in sorted(by_os.keys()):
        platforms.append({"name": os_name, "versions": sorted(by_os[os_name])})
    return platforms

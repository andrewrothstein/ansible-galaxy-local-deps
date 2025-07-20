from typing import Any

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

# Default platforms for OS/OS_VER combinations
# Based on the platform support from tests/platform-matrix-v1.json
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


def apply_default_platforms(pm: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply default platforms to platform matrix entries that don't have PLATFORMS defined."""
    for p in pm:
        if "PLATFORMS" not in p:
            key = (p["OS"], p["OS_VER"])
            p["PLATFORMS"] = default_platforms.get(key, "linux/amd64")
    return pm


def upgrade(pm_in: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_os = {}
    platforms_map = {}  # Store PLATFORMS for each OS/OS_VER combo

    # apply upgrades and flatten to set
    for p in pm_in:
        os = p["OS"]
        bo = by_os.setdefault(os, set())

        os_ver = p["OS_VER"]

        # Store PLATFORMS if provided
        if "PLATFORMS" in p:
            platforms_map[(os, os_ver)] = p["PLATFORMS"]

        if os in upgrades:
            ups = upgrades[os]
            if os_ver in ups:
                bo |= ups[os_ver]
            else:
                bo |= latest_pairs[os]
        else:
            bo |= {os_ver}

    pm_out = []
    # reinflate sets
    for os in sorted(by_os.keys()):
        for os_ver in sorted(by_os[os]):
            entry = {"OS": os, "OS_VER": os_ver}
            # Preserve PLATFORMS if it was in the original
            if (os, os_ver) in platforms_map:
                entry["PLATFORMS"] = platforms_map[(os, os_ver)]
            pm_out.append(entry)

    # Apply default platforms
    return apply_default_platforms(pm_out)


def from_dcb_osl(osl: list[str]) -> list[dict[str, Any]]:
    pm = []
    for o in osl:
        s = o.split("_")
        pm.append({"OS": s[0], "OS_VER": s[1]})
    # upgrade will also apply default platforms
    return upgrade(pm)


def render_platforms(pm: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_os = {}
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

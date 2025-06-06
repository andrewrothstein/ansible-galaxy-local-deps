import logging
import json

galaxy_alls = {'alpine', 'archlinux'}

galaxy_os_name = {
    "alpine": "Alpine",
    "archlinux": "ArchLinux",
    "debian": "Debian",
    "fedora": "Fedora",
    "rockylinux": "EL",
    "ubuntu": "Ubuntu"
}

latest_pairs = {
    "alpine": {"3.21", "3.22"},
    "archlinux": {"latest"},
    "debian": {"bookworm", "bullseye"},
    "fedora": {"41", "42"},
    "rockylinux": {"8", "9"},
    "ubuntu": {"jammy", "noble"}
}

upgrades = {
    "alpine": {
        "3.21": {"3.21"},
        "edge": {"edge"}
    },
    "debian": {
        "bookworm": {"bookworm"}
    },
    "fedora": {
        "41": {"41"}
    },
    "rockylinux": {
        "9": {"9"}
    },
    "ubuntu": {
        "noble": {"noble"}
    }
}

def upgrade(pm_in):
    by_os = {}
    # apply upgrades and flatten to set
    for p in pm_in:
        os = p["OS"]
        bo = by_os.setdefault(os, set())

        os_ver = p["OS_VER"]

        if os in upgrades.keys():
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
            pm_out.append({"OS": os, "OS_VER": os_ver})
    return pm_out

def from_dcb_osl(osl):
    pm = []
    for o in osl:
        s = o.split('_')
        pm.append({"OS": s[0], "OS_VER" : s[1]})
    return upgrade(pm)

def render_platforms(pm):
    by_os = {}
    for p in pm:
        os = p['OS']
        os_name = galaxy_os_name[os]
        bo = by_os.setdefault(os_name, set())
        if os in galaxy_alls:
            bo |= {"all"}
        else:
            bo |= {p["OS_VER"]}

    # reinflate sets
    platforms = []
    for os_name in sorted(by_os.keys()):
        platforms.append({
            "name": os_name,
            "versions": sorted(by_os[os_name])
        })
    return platforms

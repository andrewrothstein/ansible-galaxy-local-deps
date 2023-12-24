import logging
import json

upgrades = {
    "alpine": {
        "3.15": ["3.18", "3.19"],
        "3.16": ["3.18", "3.19"],
        "3.17": ["3.18", "3.19"],
        "3.18": ["3.18","3.19"],
        "3.19": ["3.19"],
        "edge": ["edge"]
    },
    "debian": {
        "jessie": ["bookworm", "bullseye"],
        "buster": ["bookworm", "bullseye"],
        "bullseye": ["bookworm", "bullseye"],
        "bookworm": ["bookworm"]
    },
    "fedora": {
        "34": ["38", "39"],
        "35": ["38", "39"],
        "36": ["38", "39"],
        "37": ["38", "39"],
        "38": ["38", "39"],
        "39": ["39"]
    },
    "rockylinux": {
        "8": ["8", "9"],
        "9": ["9"]
    },
    "ubuntu": {
        "trusty": ["focal", "jammy"],
        "xenial": ["focal", "jammy"],
        "bionic": ["focal", "jammy"],
        "focal": ["focal", "jammy"],
        "jammy": ["jammy"]
    }
}

def upgrade(pm_in):
    by_os = {}
    # apply upgrades and flatten to set
    for p in pm_in:
        os = p["OS"]
        os_ver = p["OS_VER"]
        if os not in by_os.keys():
            by_os[os] = set()

        if os not in upgrades.keys():
            by_os[os].add(os_ver)
        else:
            by_os[os] = by_os[os].union(upgrades[os][os_ver])

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

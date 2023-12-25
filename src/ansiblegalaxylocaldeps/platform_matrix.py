import logging
import json

latest_pairs = {
    "alpine": set(["3.18", "3.19"]),
    "debian": set(["bookworm", "bullseye"]),
    "fedora": set(["38", "39"]),
    "rockylinux": set(["8", "9"]),
    "ubuntu": set(["focal", "jammy"])
}

upgrades = {
    "alpine": {
        "3.19": set(["3.19"]),
        "edge": set(["edge"])
    },
    "debian": {
        "bookworm": set(["bookworm"])
    },
    "fedora": {
        "39": set(["39"])
    },
    "rockylinux": {
        "9": set(["9"])
    },
    "ubuntu": {
        "jammy": set(["jammy"])
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
            bo |= set([os_ver])


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

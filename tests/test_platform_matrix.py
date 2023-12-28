from unittest import TestCase
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ansiblegalaxylocaldeps.platform_matrix import from_dcb_osl, upgrade

class TestDeps(TestCase):

    def test_from_dcb_osl(self):
        y = load(
"""
---
- alpine_3.19
- ubuntu_jammy
""",
            Loader=Loader
        )
        pm = from_dcb_osl(y)
        self.assertEqual(len(pm), 2, 'count from converted dcb-os.yml')
        self.assertEqual(pm[0]["OS"], "alpine")
        self.assertEqual(pm[0]["OS_VER"], "3.19")
        self.assertEqual(pm[1]["OS"], "ubuntu")
        self.assertEqual(pm[1]["OS_VER"], "jammy")

    def test_upgrade(self):
        pm = upgrade([
            {
                "OS": "alpine",
                "OS_VER": "3.17"
            },
            {
                "OS": "alpine",
                "OS_VER": "3.18"
            }
        ])
        self.assertEqual(len(pm), 2, 'count from converted dcb-os.yml')
        self.assertEqual(pm[0]["OS"], "alpine")
        self.assertEqual(pm[0]["OS_VER"], "3.18")
        self.assertEqual(pm[1]["OS"], "alpine")
        self.assertEqual(pm[1]["OS_VER"], "3.19")

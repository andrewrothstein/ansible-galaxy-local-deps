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
- alpine_3.21
- ubuntu_noble
""",
            Loader=Loader
        )
        pm = from_dcb_osl(y)
        self.assertEqual(len(pm), 2, 'count from converted dcb-os.yml')
        self.assertEqual(pm[0]["OS"], "alpine")
        self.assertEqual(pm[0]["OS_VER"], "3.21")
        self.assertEqual(pm[1]["OS"], "ubuntu")
        self.assertEqual(pm[1]["OS_VER"], "noble")

    def test_upgrade(self):
        pm = upgrade([
            {
                "OS": "alpine",
                "OS_VER": "3.20"
            },
            {
                "OS": "alpine",
                "OS_VER": "3.21"
            }
        ])
        self.assertEqual(len(pm), 2, 'count from converted dcb-os.yml')
        self.assertEqual(pm[0]["OS"], "alpine")
        self.assertEqual(pm[0]["OS_VER"], "3.21")
        self.assertEqual(pm[1]["OS"], "alpine")
        self.assertEqual(pm[1]["OS_VER"], "3.22")

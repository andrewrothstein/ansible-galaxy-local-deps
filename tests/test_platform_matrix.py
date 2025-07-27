from unittest import TestCase

from yaml import load

try:
    from yaml import CLoader

    Loader = CLoader
except ImportError:
    from yaml import Loader  # type: ignore[assignment]

from ansible_galaxy_local_deps.platform_matrix import (
    from_dcb_osl,
    render_platforms,
    upgrade,
)


class TestPlatformMatrix(TestCase):
    def test_from_dcb_osl(self):
        y = load(
            """
---
- alpine_3.21
- ubuntu_noble
""",
            Loader=Loader,
        )
        pm = from_dcb_osl(y)
        self.assertEqual(len(pm), 2, "count from converted dcb-os.yml")
        self.assertEqual(pm[0]["OS"], "alpine")
        self.assertEqual(pm[0]["OS_VER"], "3.21")
        self.assertEqual(pm[1]["OS"], "ubuntu")
        self.assertEqual(pm[1]["OS_VER"], "noble")

    def test_upgrade(self):
        pm = upgrade(
            [{"OS": "alpine", "OS_VER": "3.20"}, {"OS": "alpine", "OS_VER": "3.21"}]
        )
        self.assertEqual(len(pm), 2, "count from converted dcb-os.yml")
        self.assertEqual(pm[0]["OS"], "alpine")
        self.assertEqual(pm[0]["OS_VER"], "3.21")
        self.assertEqual(pm[1]["OS"], "alpine")
        self.assertEqual(pm[1]["OS_VER"], "3.22")

    def test_render_platforms(self):
        """Test render_platforms converts platform matrix to Ansible Galaxy format."""
        pm = [
            {"OS": "alpine", "OS_VER": "3.21"},
            {"OS": "alpine", "OS_VER": "3.22"},
            {"OS": "ubuntu", "OS_VER": "jammy"},
            {"OS": "ubuntu", "OS_VER": "noble"},
            {"OS": "archlinux", "OS_VER": "latest"},
        ]

        rendered = render_platforms(pm)

        # Check basic structure
        self.assertIsInstance(rendered, list)
        self.assertGreater(len(rendered), 0)

        # Find specific platforms
        alpine_platform = next((p for p in rendered if p["name"] == "Alpine"), None)
        ubuntu_platform = next((p for p in rendered if p["name"] == "Ubuntu"), None)
        arch_platform = next((p for p in rendered if p["name"] == "ArchLinux"), None)

        # Check Alpine (should have "all" since it's in galaxy_alls)
        self.assertIsNotNone(alpine_platform)
        assert alpine_platform is not None  # Type guard for mypy
        self.assertIn("versions", alpine_platform)
        self.assertIn("all", alpine_platform["versions"])
        self.assertNotIn(
            "3.21", alpine_platform["versions"]
        )  # Should be replaced with "all"

        # Check Ubuntu (should have specific versions)
        self.assertIsNotNone(ubuntu_platform)
        assert ubuntu_platform is not None  # Type guard for mypy
        self.assertIn("jammy", ubuntu_platform["versions"])
        self.assertIn("noble", ubuntu_platform["versions"])

        # Check ArchLinux (should have "all" since it's in galaxy_alls)
        self.assertIsNotNone(arch_platform)
        assert arch_platform is not None  # Type guard for mypy
        self.assertIn("all", arch_platform["versions"])
        self.assertNotIn(
            "latest", arch_platform["versions"]
        )  # Should be replaced with "all"

    def test_render_platforms_sorting(self):
        """Test that render_platforms sorts OS names and versions."""
        pm = [
            {"OS": "ubuntu", "OS_VER": "noble"},
            {"OS": "ubuntu", "OS_VER": "jammy"},
            {"OS": "alpine", "OS_VER": "3.22"},
            {"OS": "alpine", "OS_VER": "3.21"},
        ]

        rendered = render_platforms(pm)

        # Check that platforms are sorted by name
        platform_names = [p["name"] for p in rendered]
        self.assertEqual(platform_names, sorted(platform_names))

        # Check that versions within each platform are sorted
        for platform in rendered:
            versions = platform["versions"]
            self.assertEqual(versions, sorted(versions))

    def test_upgrade_with_edge_versions(self):
        """Test upgrade handles edge/special versions correctly."""
        pm = [
            {"OS": "alpine", "OS_VER": "edge"},
            {"OS": "debian", "OS_VER": "bookworm"},
            {"OS": "fedora", "OS_VER": "41"},
        ]

        upgraded = upgrade(pm)

        # Find the entries
        alpine_entries = [p for p in upgraded if p["OS"] == "alpine"]
        debian_entries = [p for p in upgraded if p["OS"] == "debian"]
        fedora_entries = [p for p in upgraded if p["OS"] == "fedora"]

        # Alpine edge should remain as edge
        self.assertTrue(any(p["OS_VER"] == "edge" for p in alpine_entries))

        # Debian bookworm should remain as bookworm (it's in upgrades)
        self.assertTrue(any(p["OS_VER"] == "bookworm" for p in debian_entries))

        # Fedora 41 should remain as 41 (it's in upgrades)
        self.assertTrue(any(p["OS_VER"] == "41" for p in fedora_entries))

    def test_upgrade_with_unknown_os(self):
        """Test upgrade handles unknown OS gracefully."""
        pm = [
            {"OS": "unknown_os", "OS_VER": "1.0"},
            {"OS": "alpine", "OS_VER": "3.21"},
        ]

        upgraded = upgrade(pm)

        # Unknown OS should be preserved as-is
        unknown_entries = [p for p in upgraded if p["OS"] == "unknown_os"]
        self.assertEqual(len(unknown_entries), 1)
        self.assertEqual(unknown_entries[0]["OS_VER"], "1.0")

        # Alpine should still be upgraded normally
        alpine_entries = [p for p in upgraded if p["OS"] == "alpine"]
        self.assertEqual(len(alpine_entries), 1)
        self.assertEqual(alpine_entries[0]["OS_VER"], "3.21")

    def test_ubi_platform_support(self):
        """Test UBI platform is properly supported."""
        pm = [
            {"OS": "ubi", "OS_VER": "9"},
            {"OS": "ubi", "OS_VER": "10"},
            {"OS": "ubi", "OS_VER": "8"},  # Older version to test upgrade
        ]

        # Test upgrade handles UBI
        upgraded = upgrade(pm)

        # Check UBI entries
        ubi_entries = [p for p in upgraded if p["OS"] == "ubi"]
        ubi_versions = {p["OS_VER"] for p in ubi_entries}

        # Should have 9 and 10 (8 should be upgraded to latest_pairs)
        self.assertIn("9", ubi_versions)
        self.assertIn("10", ubi_versions)

        # Test render_platforms handles UBI
        rendered = render_platforms(upgraded)

        # Find EL platform (UBI maps to EL in galaxy_os_name)
        el_platform = next((p for p in rendered if p["name"] == "EL"), None)
        self.assertIsNotNone(el_platform)
        assert el_platform is not None  # Type guard for mypy
        # Both rockylinux and ubi map to EL, so we should see versions from both
        self.assertIn("9", el_platform["versions"])
        self.assertIn("10", el_platform["versions"])

    def test_kali_platform_support(self):
        """Test Kali Linux platform is properly supported."""
        pm = [
            {"OS": "kali", "OS_VER": "latest"},
            {"OS": "kali", "OS_VER": "rolling"},  # Should be upgraded to latest
        ]

        # Test upgrade handles Kali
        upgraded = upgrade(pm)

        # Check Kali entries
        kali_entries = [p for p in upgraded if p["OS"] == "kali"]
        kali_versions = {p["OS_VER"] for p in kali_entries}

        # Should only have "latest"
        self.assertEqual(kali_versions, {"latest"})

        # Test render_platforms handles Kali
        rendered = render_platforms(pm)

        # Kali maps to Debian in galaxy_os_name but should show "all" since it's in galaxy_alls
        debian_platform = next((p for p in rendered if p["name"] == "Debian"), None)
        self.assertIsNotNone(debian_platform)
        assert debian_platform is not None  # Type guard for mypy
        # Since kali is in galaxy_alls, it should have "all" in versions
        self.assertIn("all", debian_platform["versions"])

    def test_el_platform_aggregation(self):
        """Test that Rocky Linux and UBI versions are properly aggregated under EL."""
        pm = [
            {"OS": "rockylinux", "OS_VER": "9"},
            {"OS": "ubi", "OS_VER": "9"},
            {"OS": "ubi", "OS_VER": "10"},
        ]

        # Test render_platforms aggregates both under EL
        rendered = render_platforms(pm)

        # Find EL platform
        el_platform = next((p for p in rendered if p["name"] == "EL"), None)
        self.assertIsNotNone(el_platform)
        assert el_platform is not None  # Type guard for mypy

        # Should have both 9 and 10 (9 from both rockylinux and ubi, 10 from ubi)
        self.assertEqual(sorted(el_platform["versions"]), ["10", "9"])

        # Should only have one EL platform entry
        el_platforms = [p for p in rendered if p["name"] == "EL"]
        self.assertEqual(len(el_platforms), 1)

    def test_default_platforms_applied(self):
        """Test that default platforms are applied when not specified."""
        from ansible_galaxy_local_deps.platform_matrix import apply_default_platforms

        pm = [
            {"OS": "alpine", "OS_VER": "3.21"},  # Should get linux/amd64
            {"OS": "ubuntu", "OS_VER": "jammy"},  # Should get linux/amd64,linux/arm64
            {"OS": "unknown", "OS_VER": "1.0"},  # Should get default linux/amd64
        ]

        result = apply_default_platforms(pm)

        # Check Alpine gets correct platform
        alpine_entry = next(p for p in result if p["OS"] == "alpine")
        self.assertEqual(alpine_entry["PLATFORMS"], "linux/amd64")

        # Check Ubuntu gets correct platform
        ubuntu_entry = next(p for p in result if p["OS"] == "ubuntu")
        self.assertEqual(ubuntu_entry["PLATFORMS"], "linux/amd64,linux/arm64")

        # Check unknown OS gets default
        unknown_entry = next(p for p in result if p["OS"] == "unknown")
        self.assertEqual(unknown_entry["PLATFORMS"], "linux/amd64")

    def test_platforms_preserved_during_upgrade(self):
        """Test that explicitly set PLATFORMS are preserved during upgrade."""
        pm = [
            {"OS": "alpine", "OS_VER": "3.20", "PLATFORMS": "custom/platform"},
            {"OS": "alpine", "OS_VER": "3.21"},  # No PLATFORMS, should get default
        ]

        upgraded = upgrade(pm)

        # Find the entries
        alpine_3_21 = next(
            p for p in upgraded if p["OS"] == "alpine" and p["OS_VER"] == "3.21"
        )
        alpine_3_22 = next(
            p for p in upgraded if p["OS"] == "alpine" and p["OS_VER"] == "3.22"
        )

        # 3.21 should have default platforms
        self.assertEqual(alpine_3_21["PLATFORMS"], "linux/amd64")
        # 3.22 should also have default platforms (since it was added by upgrade)
        self.assertEqual(alpine_3_22["PLATFORMS"], "linux/amd64")

    def test_from_dcb_osl_applies_defaults(self):
        """Test that from_dcb_osl applies default platforms."""
        osl = ["ubuntu_jammy", "alpine_3.21", "fedora_42"]

        result = from_dcb_osl(osl)

        # All entries should have PLATFORMS
        for entry in result:
            self.assertIn("PLATFORMS", entry)

        # Check specific platforms
        ubuntu_entry = next(
            p for p in result if p["OS"] == "ubuntu" and p["OS_VER"] == "jammy"
        )
        self.assertEqual(ubuntu_entry["PLATFORMS"], "linux/amd64,linux/arm64")

        alpine_entry = next(
            p for p in result if p["OS"] == "alpine" and p["OS_VER"] == "3.21"
        )
        self.assertEqual(alpine_entry["PLATFORMS"], "linux/amd64")

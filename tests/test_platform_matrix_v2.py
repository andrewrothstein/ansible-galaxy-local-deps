import json
from unittest import TestCase
from unittest.mock import Mock, patch

import ansible_galaxy_local_deps.platform_matrix as pm


class TestPlatformMatrixV2(TestCase):
    """Test the new platform matrix functionality with external defaults loading."""

    def setUp(self):
        # Save original module state
        self.orig_latest_pairs = pm.latest_pairs.copy()
        self.orig_upgrades = pm.upgrades.copy()
        self.orig_default_platforms = pm.default_platforms.copy()
        self.orig_default_upstream = pm.default_upstream.copy()

    def tearDown(self):
        # Restore original module state
        pm.latest_pairs = self.orig_latest_pairs
        pm.upgrades = self.orig_upgrades
        pm.default_platforms = self.orig_default_platforms
        pm.default_upstream = self.orig_default_upstream

    def test_populate_defaults_from_matrix(self):
        """Test populating defaults from a platform matrix."""
        test_matrix = [
            {"OS": "alpine", "OS_VER": "3.20", "PLATFORMS": "linux/amd64"},
            {"OS": "alpine", "OS_VER": "3.21", "PLATFORMS": "linux/amd64"},
            {"OS": "ubuntu", "OS_VER": "jammy", "PLATFORMS": "linux/amd64,linux/arm64"},
            {
                "OS": "kali",
                "OS_VER": "latest",
                "UPSTREAM_ORG": "kalilinux",
                "UPSTREAM_OS": "kali-rolling",
                "PLATFORMS": "linux/amd64",
            },
        ]

        pm.populate_defaults_from_matrix(test_matrix)

        # Check latest_pairs
        self.assertEqual(pm.latest_pairs["alpine"], {"3.20", "3.21"})
        self.assertEqual(pm.latest_pairs["ubuntu"], {"jammy"})
        self.assertEqual(pm.latest_pairs["kali"], {"latest"})

        # Check default_platforms
        self.assertEqual(pm.default_platforms[("alpine", "3.20")], "linux/amd64")
        self.assertEqual(pm.default_platforms[("alpine", "3.21")], "linux/amd64")
        self.assertEqual(
            pm.default_platforms[("ubuntu", "jammy")], "linux/amd64,linux/arm64"
        )

        # Check default_upstream
        self.assertIn(("kali", "latest"), pm.default_upstream)
        self.assertEqual(
            pm.default_upstream[("kali", "latest")]["UPSTREAM_ORG"], "kalilinux"
        )
        self.assertEqual(
            pm.default_upstream[("kali", "latest")]["UPSTREAM_OS"], "kali-rolling"
        )

    def test_apply_default_platforms_with_upstream(self):
        """Test applying defaults including upstream fields."""
        # Set up test defaults
        pm.default_platforms = {
            ("ubi", "9"): "linux/amd64,linux/arm64",
        }
        pm.default_upstream = {
            ("ubi", "9"): {
                "UPSTREAM_ORG": "redhat",
                "UPSTREAM_OS": "ubi9",
                "UPSTREAM_OS_VER": "latest",
            }
        }

        # Test data without PLATFORMS or UPSTREAM fields
        test_pm = [{"OS": "ubi", "OS_VER": "9"}]

        result = pm.apply_default_platforms(test_pm)

        # Check that defaults were applied
        self.assertEqual(result[0]["PLATFORMS"], "linux/amd64,linux/arm64")
        self.assertEqual(result[0]["UPSTREAM_ORG"], "redhat")
        self.assertEqual(result[0]["UPSTREAM_OS"], "ubi9")
        self.assertEqual(result[0]["UPSTREAM_OS_VER"], "latest")

    def test_apply_default_platforms_preserves_existing(self):
        """Test that existing values are not overwritten."""
        # Set up test defaults
        pm.default_platforms = {
            ("alpine", "3.21"): "linux/amd64,linux/arm64",  # Different from input
        }
        pm.default_upstream = {
            ("alpine", "3.21"): {
                "UPSTREAM_ORG": "default_org",
                "UPSTREAM_OS": "default_os",
            }
        }

        # Test data with existing values
        test_pm = [
            {
                "OS": "alpine",
                "OS_VER": "3.21",
                "PLATFORMS": "linux/amd64",  # Should not be overwritten
                "UPSTREAM_ORG": "custom_org",  # Should not be overwritten
            }
        ]

        result = pm.apply_default_platforms(test_pm)

        # Check that existing values were preserved
        self.assertEqual(result[0]["PLATFORMS"], "linux/amd64")
        self.assertEqual(result[0]["UPSTREAM_ORG"], "custom_org")
        # But missing upstream field should be added
        self.assertEqual(result[0]["UPSTREAM_OS"], "default_os")

    def test_upgrade_preserves_all_extra_fields(self):
        """Test that upgrade preserves all extra fields including UPSTREAM_*."""
        # Set up minimal defaults for upgrade to work
        pm.latest_pairs = {"custom": {"v1", "v2"}}
        pm.upgrades = {}

        test_pm = [
            {
                "OS": "custom",
                "OS_VER": "v1",
                "PLATFORMS": "linux/amd64",
                "UPSTREAM_ORG": "myorg",
                "UPSTREAM_OS": "custom-os",
                "CUSTOM_FIELD": "custom_value",
            }
        ]

        result = pm.upgrade(test_pm)

        # Find the v1 entry
        v1_entry = next(e for e in result if e["OS_VER"] == "v1")

        # Check all fields were preserved
        self.assertEqual(v1_entry["PLATFORMS"], "linux/amd64")
        self.assertEqual(v1_entry["UPSTREAM_ORG"], "myorg")
        self.assertEqual(v1_entry["UPSTREAM_OS"], "custom-os")
        self.assertEqual(v1_entry["CUSTOM_FIELD"], "custom_value")

    @patch("ansible_galaxy_local_deps.platform_matrix.os.path.exists")
    @patch("builtins.open")
    def test_load_default_platform_matrix_from_module_dir(self, mock_open, mock_exists):
        """Test loading default matrix from module directory."""
        test_matrix = [{"OS": "test", "OS_VER": "1.0", "PLATFORMS": "linux/test"}]

        # Mock file exists only in module directory
        def exists_side_effect(path):
            return (
                "default-platform-matrix-v1.json" in path
                and "ansible_galaxy_local_deps" in path
            )

        mock_exists.side_effect = exists_side_effect

        # Mock file content
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.read = Mock(return_value=json.dumps(test_matrix))
        mock_open.return_value = mock_file

        # Mock json.load to return our test data
        with patch("json.load", return_value=test_matrix):
            result = pm.load_default_platform_matrix()

        self.assertEqual(result, test_matrix)

    def test_load_default_platform_matrix_fallback(self):
        """Test fallback when no default matrix file is found."""
        with patch(
            "ansible_galaxy_local_deps.platform_matrix.os.path.exists",
            return_value=False,
        ):
            result = pm.load_default_platform_matrix()

        self.assertIsNone(result)

    def test_init_builtin_defaults(self):
        """Test that built-in defaults are properly initialized."""
        # Clear current state
        pm.latest_pairs = {}
        pm.upgrades = {}
        pm.default_platforms = {}

        # Initialize built-in defaults
        pm._init_builtin_defaults()

        # Check that defaults were populated
        self.assertIn("alpine", pm.latest_pairs)
        self.assertIn("ubuntu", pm.latest_pairs)
        self.assertIn("alpine", pm.upgrades)
        self.assertIn(("alpine", "3.21"), pm.default_platforms)
        self.assertIn(("ubuntu", "jammy"), pm.default_platforms)

    def test_from_dcb_osl_with_defaults(self):
        """Test from_dcb_osl applies defaults including upstream info."""
        # Set up test defaults
        pm.default_platforms = {
            ("test", "v1"): "linux/amd64,linux/arm64",
        }
        pm.default_upstream = {
            ("test", "v1"): {
                "UPSTREAM_ORG": "testorg",
            }
        }
        pm.latest_pairs = {"test": {"v1"}}
        pm.upgrades = {}

        result = pm.from_dcb_osl(["test_v1"])

        # Check that defaults were applied
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["OS"], "test")
        self.assertEqual(result[0]["OS_VER"], "v1")
        self.assertEqual(result[0]["PLATFORMS"], "linux/amd64,linux/arm64")
        self.assertEqual(result[0]["UPSTREAM_ORG"], "testorg")

    def test_version_sorting_handles_numbers_correctly(self):
        """Test that version sorting handles numeric versions correctly."""
        test_matrix = [
            {"OS": "fedora", "OS_VER": "39"},
            {"OS": "fedora", "OS_VER": "40"},
            {"OS": "fedora", "OS_VER": "41"},
            {"OS": "fedora", "OS_VER": "42"},
        ]

        pm.populate_defaults_from_matrix(test_matrix)

        # Check that latest_pairs contains the last 2 versions
        # Note: string sorting of "39", "40", "41", "42" works correctly
        self.assertEqual(pm.latest_pairs["fedora"], {"41", "42"})

    def test_upgrade_with_external_defaults(self):
        """Test upgrade using externally loaded defaults."""
        # Simulate having loaded external defaults
        pm.latest_pairs = {
            "alpine": {"3.21", "3.22"},
            "ubuntu": {"jammy", "noble"},
        }
        pm.upgrades = {
            "alpine": {"3.20": {"3.21", "3.22"}},
            "ubuntu": {"focal": {"jammy", "noble"}},
        }
        pm.default_platforms = {
            ("alpine", "3.21"): "linux/amd64",
            ("alpine", "3.22"): "linux/amd64",
            ("ubuntu", "jammy"): "linux/amd64,linux/arm64",
            ("ubuntu", "noble"): "linux/amd64,linux/arm64",
        }

        # Test upgrading old versions
        test_pm = [
            {"OS": "alpine", "OS_VER": "3.20"},
            {"OS": "ubuntu", "OS_VER": "focal"},
        ]

        result = pm.upgrade(test_pm)

        # Check that versions were upgraded
        os_versions = {(e["OS"], e["OS_VER"]) for e in result}
        self.assertIn(("alpine", "3.21"), os_versions)
        self.assertIn(("alpine", "3.22"), os_versions)
        self.assertIn(("ubuntu", "jammy"), os_versions)
        self.assertIn(("ubuntu", "noble"), os_versions)

        # Check that platforms were applied
        for entry in result:
            self.assertIn("PLATFORMS", entry)

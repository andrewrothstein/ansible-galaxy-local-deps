import json
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

from ansible_galaxy_local_deps.gengithubactions import (
    build_yml,
    mksubdirs,
    render_meta_main,
    upgrade_platform_matrix,
)


class TestGenGithubActions(TestCase):
    def test_build_yml_v1(self):
        """Test build_yml function with v1 version."""
        result = build_yml("v1")

        self.assertEqual(result["on"], "push")
        self.assertIn("jobs", result)
        self.assertIn("bake-ansible-images-v1", result["jobs"])
        self.assertEqual(
            result["jobs"]["bake-ansible-images-v1"]["uses"],
            "andrewrothstein/.github/.github/workflows/bake-ansible-images-v1.yml@develop",
        )

    def test_build_yml_v2(self):
        """Test build_yml function with v2 version."""
        result = build_yml("v2")

        self.assertEqual(result["on"], "push")
        self.assertIn("jobs", result)
        self.assertIn("bake-ansible-images-v1", result["jobs"])
        self.assertEqual(
            result["jobs"]["bake-ansible-images-v1"]["uses"],
            "andrewrothstein/.github/.github/workflows/bake-ansible-images-v2.yml@develop",
        )

    def test_mksubdirs_creates_nested_directories(self):
        """Test mksubdirs creates nested directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mksubdirs(tmpdir, [".github", "workflows"])

            # Check that directories were created
            github_dir = os.path.join(tmpdir, ".github")
            workflows_dir = os.path.join(tmpdir, ".github", "workflows")

            self.assertTrue(os.path.isdir(github_dir))
            self.assertTrue(os.path.isdir(workflows_dir))

    def test_mksubdirs_handles_existing_directories(self):
        """Test mksubdirs handles already existing directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Pre-create the directories
            os.makedirs(os.path.join(tmpdir, ".github", "workflows"))

            # Should not raise an error
            mksubdirs(tmpdir, [".github", "workflows"])

            # Directories should still exist
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, ".github", "workflows")))

    @patch("ansible_galaxy_local_deps.gengithubactions.slurp")
    @patch("ansible_galaxy_local_deps.gengithubactions.dump")
    def test_render_meta_main_with_valid_data(self, mock_dump, mock_slurp):
        """Test render_meta_main with valid meta/main.yml data."""
        # Mock the slurped meta/main.yml content
        mock_slurp.slurp_meta_main_yml.return_value = {
            "galaxy_info": {
                "author": "test_author",
                "description": "Test role",
                "license": ["MIT", "Apache"],  # List that should be flattened
                "min_ansible_version": 2.9,  # Float that should be stringified
            }
        }

        # Test platform matrix
        test_pm = [
            {"OS": "ubuntu", "OS_VER": "jammy"},
            {"OS": "alpine", "OS_VER": "3.21"},
        ]

        # Call the function
        render_meta_main("/test/role", test_pm)

        # Verify the meta/main.yml was modified correctly
        mock_dump.dump_meta_main_yml.assert_called_once()
        call_args = mock_dump.dump_meta_main_yml.call_args[0]

        self.assertEqual(call_args[0], "/test/role")
        modified_data = call_args[1]

        # Check license was flattened
        self.assertEqual(modified_data["galaxy_info"]["license"], "MIT")

        # Check min_ansible_version was stringified
        self.assertEqual(modified_data["galaxy_info"]["min_ansible_version"], "2.9")

        # Check namespace was added
        self.assertEqual(modified_data["galaxy_info"]["namespace"], "andrewrothstein")

    @patch("ansible_galaxy_local_deps.gengithubactions.slurp")
    def test_render_meta_main_missing_file(self, mock_slurp):
        """Test render_meta_main when meta/main.yml is missing."""
        mock_slurp.slurp_meta_main_yml.return_value = None

        # Should return early without error
        render_meta_main("/test/role", [])

        # Verify it logged an error but didn't crash
        mock_slurp.slurp_meta_main_yml.assert_called_once_with("/test/role")

    @patch("ansible_galaxy_local_deps.gengithubactions.slurp")
    def test_render_meta_main_missing_galaxy_info(self, mock_slurp):
        """Test render_meta_main when galaxy_info section is missing."""
        mock_slurp.slurp_meta_main_yml.return_value = {
            "dependencies": []  # No galaxy_info section
        }

        # Should return early without error
        render_meta_main("/test/role", [])

    @patch("ansible_galaxy_local_deps.gengithubactions.slurp")
    @patch("ansible_galaxy_local_deps.gengithubactions.dump")
    def test_render_meta_main_computes_role_name(self, mock_dump, mock_slurp):
        """Test render_meta_main computes role_name from directory."""
        mock_slurp.slurp_meta_main_yml.return_value = {
            "galaxy_info": {
                "author": "test_author",
            }
        }

        # Test with ansible- prefix
        render_meta_main("/path/to/ansible-test-role", [])

        call_args = mock_dump.dump_meta_main_yml.call_args[0]
        modified_data = call_args[1]

        # Check role_name was computed correctly
        self.assertEqual(modified_data["galaxy_info"]["role_name"], "test-role")

    @patch("ansible_galaxy_local_deps.gengithubactions.os.path.exists")
    @patch("ansible_galaxy_local_deps.gengithubactions.os.remove")
    @patch("ansible_galaxy_local_deps.gengithubactions.slurp")
    @patch("ansible_galaxy_local_deps.gengithubactions.dump")
    @patch("ansible_galaxy_local_deps.gengithubactions.platform_matrix")
    def test_upgrade_platform_matrix_from_dcb_os(
        self, mock_pm, mock_dump, mock_slurp, mock_remove, mock_exists
    ):
        """Test upgrade_platform_matrix when dcb-os.yml exists."""
        # Setup mocks
        mock_exists.return_value = True  # dcb-os.yml exists
        mock_slurp.slurp_dcb_os_yml.return_value = ["alpine_3.21", "ubuntu_noble"]
        mock_slurp.slurp_meta_main_yml.return_value = {"galaxy_info": {}}
        mock_pm.from_dcb_osl.return_value = [
            {"OS": "alpine", "OS_VER": "3.21"},
            {"OS": "ubuntu", "OS_VER": "noble"},
        ]

        # Call function
        upgrade_platform_matrix("/test/role")

        # Verify dcb-os.yml was processed and removed
        mock_slurp.slurp_dcb_os_yml.assert_called_once_with("/test/role")
        mock_pm.from_dcb_osl.assert_called_once_with(["alpine_3.21", "ubuntu_noble"])
        mock_remove.assert_called_once_with("/test/role/dcb-os.yml")

        # Verify platform matrix was saved
        mock_dump.dump_platform_matrix_json.assert_called_once()

    @patch("ansible_galaxy_local_deps.gengithubactions.os.path.exists")
    @patch("ansible_galaxy_local_deps.gengithubactions.slurp")
    @patch("ansible_galaxy_local_deps.gengithubactions.dump")
    @patch("ansible_galaxy_local_deps.gengithubactions.platform_matrix")
    def test_upgrade_platform_matrix_from_json(
        self, mock_pm, mock_dump, mock_slurp, mock_exists
    ):
        """Test upgrade_platform_matrix when using platform-matrix-v1.json."""
        # Setup mocks
        mock_exists.return_value = False  # dcb-os.yml doesn't exist
        test_pm_data = [
            {"OS": "alpine", "OS_VER": "3.20"},
            {"OS": "ubuntu", "OS_VER": "jammy"},
        ]
        mock_slurp.slurp_platform_matrix_json.return_value = test_pm_data
        mock_slurp.slurp_meta_main_yml.return_value = {"galaxy_info": {}}
        mock_pm.upgrade.return_value = [
            {"OS": "alpine", "OS_VER": "3.21"},
            {"OS": "alpine", "OS_VER": "3.22"},
            {"OS": "ubuntu", "OS_VER": "jammy"},
            {"OS": "ubuntu", "OS_VER": "noble"},
        ]

        # Call function
        upgrade_platform_matrix("/test/role")

        # Verify platform matrix was loaded and upgraded
        mock_slurp.slurp_platform_matrix_json.assert_called_once_with("/test/role")
        mock_pm.upgrade.assert_called_once_with(test_pm_data)

        # Verify platform matrix was saved
        mock_dump.dump_platform_matrix_json.assert_called_once()

    @patch("ansible_galaxy_local_deps.gengithubactions.os.path.exists")
    @patch("ansible_galaxy_local_deps.gengithubactions.slurp")
    def test_upgrade_platform_matrix_missing_files(self, mock_slurp, mock_exists):
        """Test upgrade_platform_matrix when no platform files exist."""
        mock_exists.return_value = False
        mock_slurp.slurp_platform_matrix_json.return_value = None

        # Should return early without error
        upgrade_platform_matrix("/test/role")

        # Verify it tried to load the file
        mock_slurp.slurp_platform_matrix_json.assert_called_once_with("/test/role")

    def test_integration_with_test_data(self):
        """Test with actual platform-matrix-v1.json test data."""
        # Read the test platform matrix file
        test_file = os.path.join(os.path.dirname(__file__), "platform-matrix-v1.json")

        with open(test_file) as f:
            test_data = json.load(f)

        # Import platform_matrix module to test integration
        from ansible_galaxy_local_deps.platform_matrix import galaxy_os_name, upgrade

        # Test upgrade function with test data
        # The test data already has latest versions, so upgrade should return similar data
        upgraded = upgrade(test_data)

        # Verify we have expected OS entries
        os_versions = {(p["OS"], p["OS_VER"]) for p in upgraded}

        # Check some expected entries exist
        self.assertIn(("alpine", "3.21"), os_versions)
        self.assertIn(("alpine", "3.22"), os_versions)
        self.assertIn(("ubuntu", "jammy"), os_versions)
        self.assertIn(("ubuntu", "noble"), os_versions)

        # Test render_platforms only with supported OS types
        # Filter to only OS types that are in galaxy_os_name mapping
        supported_platforms = [p for p in upgraded if p["OS"] in galaxy_os_name]

        # Import and test render_platforms
        from ansible_galaxy_local_deps.platform_matrix import render_platforms

        rendered = render_platforms(supported_platforms)

        # Verify rendered format
        self.assertIsInstance(rendered, list)
        self.assertGreater(len(rendered), 0)  # Should have at least some platforms

        for platform in rendered:
            self.assertIn("name", platform)
            self.assertIn("versions", platform)
            self.assertIsInstance(platform["versions"], list)
            self.assertGreater(
                len(platform["versions"]), 0
            )  # Each platform should have versions

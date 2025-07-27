import json
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

import yaml

from ansible_galaxy_local_deps.slurp import (
    slurp_dcb_os_yml,
    slurp_json,
    slurp_meta_main_yml,
    slurp_meta_requirements_yml,
    slurp_platform_matrix_json,
    slurp_script_yml,
    slurp_test_requirements_yml,
    slurp_yml,
)


class TestSlurp(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir)

    def test_slurp_yml_valid_file(self):
        """Test slurp_yml with a valid YAML file."""
        test_data = {"key": "value", "list": [1, 2, 3]}
        test_file = os.path.join(self.test_dir, "test.yml")

        with open(test_file, "w") as f:
            yaml.dump(test_data, f)

        result = slurp_yml(self.test_dir, "test.yml")
        self.assertEqual(result, test_data)

    def test_slurp_yml_missing_file(self):
        """Test slurp_yml with a missing file."""
        result = slurp_yml(self.test_dir, "missing.yml")
        self.assertIsNone(result)

    def test_slurp_yml_invalid_yaml(self):
        """Test slurp_yml with invalid YAML content."""
        test_file = os.path.join(self.test_dir, "invalid.yml")

        with open(test_file, "w") as f:
            f.write("invalid: yaml: content: [")

        result = slurp_yml(self.test_dir, "invalid.yml")
        self.assertIsNone(result)

    @patch("ansible_galaxy_local_deps.slurp.open", side_effect=PermissionError)
    @patch("ansible_galaxy_local_deps.slurp.finder.find")
    def test_slurp_yml_permission_error(self, mock_find, mock_open):
        """Test slurp_yml with permission error."""
        mock_find.return_value = "/some/file.yml"
        result = slurp_yml("/some/dir", "file.yml")
        self.assertIsNone(result)

    def test_slurp_json_valid_file(self):
        """Test slurp_json with a valid JSON file."""
        test_data = {"key": "value", "number": 42}
        test_file = os.path.join(self.test_dir, "test.json")

        with open(test_file, "w") as f:
            json.dump(test_data, f)

        result = slurp_json(self.test_dir, "test.json")
        self.assertEqual(result, test_data)

    def test_slurp_json_missing_file(self):
        """Test slurp_json with a missing file."""
        result = slurp_json(self.test_dir, "missing.json")
        self.assertIsNone(result)

    def test_slurp_json_invalid_json(self):
        """Test slurp_json with invalid JSON content."""
        test_file = os.path.join(self.test_dir, "invalid.json")

        with open(test_file, "w") as f:
            f.write("{invalid json")

        result = slurp_json(self.test_dir, "invalid.json")
        self.assertIsNone(result)

    def test_slurp_meta_main_yml(self):
        """Test slurp_meta_main_yml."""
        meta_dir = os.path.join(self.test_dir, "meta")
        os.makedirs(meta_dir)

        test_data = {"galaxy_info": {"author": "test"}}
        test_file = os.path.join(meta_dir, "main.yml")

        with open(test_file, "w") as f:
            yaml.dump(test_data, f)

        result = slurp_meta_main_yml(self.test_dir)
        self.assertEqual(result, test_data)

    def test_slurp_meta_requirements_yml(self):
        """Test slurp_meta_requirements_yml."""
        meta_dir = os.path.join(self.test_dir, "meta")
        os.makedirs(meta_dir)

        test_data = [{"role": "test-role"}]
        test_file = os.path.join(meta_dir, "requirements.yml")

        with open(test_file, "w") as f:
            yaml.dump(test_data, f)

        result = slurp_meta_requirements_yml(self.test_dir)
        self.assertEqual(result, test_data)

    def test_slurp_test_requirements_yml(self):
        """Test slurp_test_requirements_yml."""
        test_data = [{"role": "test-role", "version": "v1.0.0"}]
        test_file = os.path.join(self.test_dir, "test-requirements.yml")

        with open(test_file, "w") as f:
            yaml.dump(test_data, f)

        result = slurp_test_requirements_yml(self.test_dir)
        self.assertEqual(result, test_data)

    def test_slurp_dcb_os_yml(self):
        """Test slurp_dcb_os_yml."""
        test_data = ["alpine_3.21", "ubuntu_noble"]
        test_file = os.path.join(self.test_dir, "dcb-os.yml")

        with open(test_file, "w") as f:
            yaml.dump(test_data, f)

        result = slurp_dcb_os_yml(self.test_dir)
        self.assertEqual(result, test_data)

    def test_slurp_script_yml(self):
        """Test slurp_script_yml."""
        test_data = {"script": "test.sh", "args": ["arg1", "arg2"]}
        test_file = os.path.join(self.test_dir, "script.yml")

        with open(test_file, "w") as f:
            yaml.dump(test_data, f)

        result = slurp_script_yml(self.test_dir)
        self.assertEqual(result, test_data)

    def test_slurp_platform_matrix_json(self):
        """Test slurp_platform_matrix_json."""
        test_data = [
            {"OS": "alpine", "OS_VER": "3.21"},
            {"OS": "ubuntu", "OS_VER": "jammy"},
        ]
        test_file = os.path.join(self.test_dir, "platform-matrix-v1.json")

        with open(test_file, "w") as f:
            json.dump(test_data, f)

        result = slurp_platform_matrix_json(self.test_dir)
        self.assertEqual(result, test_data)

    @patch("ansible_galaxy_local_deps.slurp.open")
    @patch("ansible_galaxy_local_deps.slurp.finder.find")
    def test_slurp_yml_unexpected_error(self, mock_find, mock_open):
        """Test slurp_yml with unexpected error."""
        mock_find.return_value = "/some/file.yml"
        mock_open.side_effect = Exception("Unexpected error")

        result = slurp_yml("/some/dir", "file.yml")
        self.assertIsNone(result)

    @patch("ansible_galaxy_local_deps.slurp.open")
    @patch("ansible_galaxy_local_deps.slurp.finder.find")
    def test_slurp_json_unexpected_error(self, mock_find, mock_open):
        """Test slurp_json with unexpected error."""
        mock_find.return_value = "/some/file.json"
        mock_open.side_effect = Exception("Unexpected error")

        result = slurp_json("/some/dir", "file.json")
        self.assertIsNone(result)

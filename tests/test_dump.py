import json
import os
import tempfile
from unittest import TestCase
from unittest.mock import mock_open, patch

import yaml

from ansible_galaxy_local_deps.dump import (
    IndentDumper,
    dump_dcb_os_yml,
    dump_github_actions_build_yml,
    dump_gitignore,
    dump_json,
    dump_meta_main_yml,
    dump_meta_requirements_yml,
    dump_platform_matrix_json,
    dump_requirements_txt,
    dump_requirements_yml,
    dump_test_requirements_yml,
    dump_txt,
    dump_yml,
)


class TestDump(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir)

    def test_dump_txt_simple(self):
        """Test dump_txt with simple text content."""
        content = "Hello, World!"
        dump_txt(self.test_dir, "test.txt", content)

        output_file = os.path.join(self.test_dir, "test.txt")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            self.assertEqual(f.read(), content)

    def test_dump_txt_creates_directories(self):
        """Test dump_txt creates nested directories."""
        content = "test content"
        dump_txt(self.test_dir, "subdir/nested/test.txt", content)

        output_file = os.path.join(self.test_dir, "subdir", "nested", "test.txt")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            self.assertEqual(f.read(), content)

    @patch("ansible_galaxy_local_deps.dump.open", side_effect=PermissionError)
    def test_dump_txt_permission_error(self, mock_open_func):
        """Test dump_txt raises PermissionError."""
        with self.assertRaises(PermissionError):
            dump_txt(self.test_dir, "test.txt", "content")

    @patch("ansible_galaxy_local_deps.dump.os.makedirs", side_effect=OSError("Error"))
    def test_dump_txt_os_error(self, mock_makedirs):
        """Test dump_txt raises OSError."""
        with self.assertRaises(OSError):
            dump_txt(self.test_dir, "test.txt", "content")

    def test_dump_yml_dict(self):
        """Test dump_yml with dictionary data."""
        data = {"key": "value", "nested": {"inner": 123}}
        dump_yml(self.test_dir, "test.yml", data)

        output_file = os.path.join(self.test_dir, "test.yml")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = yaml.safe_load(f)
            self.assertEqual(loaded, data)

    def test_dump_yml_list(self):
        """Test dump_yml with list data."""
        data = [{"role": "test-role-1"}, {"role": "test-role-2"}]
        dump_yml(self.test_dir, "test.yml", data)

        output_file = os.path.join(self.test_dir, "test.yml")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = yaml.safe_load(f)
            self.assertEqual(loaded, data)

    def test_dump_yml_creates_directories(self):
        """Test dump_yml creates nested directories."""
        data = {"test": "data"}
        dump_yml(self.test_dir, "meta/main.yml", data)

        output_file = os.path.join(self.test_dir, "meta", "main.yml")
        self.assertTrue(os.path.exists(output_file))

    @patch("ansible_galaxy_local_deps.dump.open", side_effect=yaml.YAMLError("Error"))
    def test_dump_yml_yaml_error(self, mock_open_func):
        """Test dump_yml raises YAMLError."""
        with self.assertRaises(yaml.YAMLError):
            dump_yml(self.test_dir, "test.yml", {"data": "value"})

    def test_dump_json_dict(self):
        """Test dump_json with dictionary data."""
        data = {"key": "value", "number": 42}
        dump_json(self.test_dir, "test.json", data)

        output_file = os.path.join(self.test_dir, "test.json")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = json.load(f)
            self.assertEqual(loaded, data)

    def test_dump_json_list(self):
        """Test dump_json with list data."""
        data = [{"OS": "alpine", "OS_VER": "3.21"}]
        dump_json(self.test_dir, "test.json", data)

        output_file = os.path.join(self.test_dir, "test.json")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = json.load(f)
            self.assertEqual(loaded, data)

    def test_dump_json_creates_directories(self):
        """Test dump_json creates nested directories."""
        data = {"test": "data"}
        dump_json(self.test_dir, "subdir/test.json", data)

        output_file = os.path.join(self.test_dir, "subdir", "test.json")
        self.assertTrue(os.path.exists(output_file))

    @patch("ansible_galaxy_local_deps.dump.json.dump", side_effect=TypeError("Error"))
    @patch("ansible_galaxy_local_deps.dump.open", new_callable=mock_open)
    @patch("ansible_galaxy_local_deps.dump.os.makedirs")
    def test_dump_json_type_error(self, mock_makedirs, mock_open_func, mock_json_dump):
        """Test dump_json raises TypeError."""
        with self.assertRaises(TypeError):
            dump_json(self.test_dir, "test.json", {"data": set()})

    def test_dump_meta_main_yml(self):
        """Test dump_meta_main_yml."""
        data = {"galaxy_info": {"author": "test"}}
        dump_meta_main_yml(self.test_dir, data)

        output_file = os.path.join(self.test_dir, "meta", "main.yml")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = yaml.safe_load(f)
            self.assertEqual(loaded, data)

    def test_dump_meta_requirements_yml(self):
        """Test dump_meta_requirements_yml."""
        data = [{"role": "test-role"}]
        dump_meta_requirements_yml(self.test_dir, data)

        output_file = os.path.join(self.test_dir, "meta", "requirements.yml")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = yaml.safe_load(f)
            self.assertEqual(loaded, data)

    def test_dump_requirements_yml(self):
        """Test dump_requirements_yml."""
        data = [{"role": "test-role", "version": "v1.0.0"}]
        dump_requirements_yml(self.test_dir, data)

        output_file = os.path.join(self.test_dir, "requirements.yml")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = yaml.safe_load(f)
            self.assertEqual(loaded, data)

    def test_dump_requirements_txt(self):
        """Test dump_requirements_txt."""
        content = "ansible>=2.9\njinja2>=2.11"
        dump_requirements_txt(self.test_dir, content)

        output_file = os.path.join(self.test_dir, "requirements.txt")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            self.assertEqual(f.read(), content)

    def test_dump_dcb_os_yml(self):
        """Test dump_dcb_os_yml."""
        data = ["alpine_3.21", "ubuntu_noble"]
        dump_dcb_os_yml(self.test_dir, data)

        output_file = os.path.join(self.test_dir, "dcb-os.yml")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = yaml.safe_load(f)
            self.assertEqual(loaded, data)

    def test_dump_platform_matrix_json(self):
        """Test dump_platform_matrix_json."""
        data = [{"OS": "alpine", "OS_VER": "3.21"}]
        dump_platform_matrix_json(self.test_dir, data)

        output_file = os.path.join(self.test_dir, "platform-matrix-v1.json")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = json.load(f)
            self.assertEqual(loaded, data)

    def test_dump_test_requirements_yml(self):
        """Test dump_test_requirements_yml."""
        data = [{"role": "test-role"}]
        dump_test_requirements_yml(self.test_dir, data)

        output_file = os.path.join(self.test_dir, "test-requirements.yml")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = yaml.safe_load(f)
            self.assertEqual(loaded, data)

    def test_dump_github_actions_build_yml(self):
        """Test dump_github_actions_build_yml."""
        data = {"on": "push", "jobs": {"test": {"runs-on": "ubuntu-latest"}}}
        dump_github_actions_build_yml(self.test_dir, data)

        output_file = os.path.join(self.test_dir, ".github", "workflows", "build.yml")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            loaded = yaml.safe_load(f)
            self.assertEqual(loaded, data)

    def test_dump_gitignore(self):
        """Test dump_gitignore."""
        dump_gitignore(self.test_dir)

        output_file = os.path.join(self.test_dir, ".gitignore")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            content = f.read()
            self.assertIn("**~*.retry", content)
            self.assertIn("Dockerfile.*", content)
            self.assertIn("requirements.yml", content)
            self.assertIn("!meta/requirements.yml", content)
            self.assertIn("**/*undo-tree*", content)
            self.assertIn(".ansible", content)

    def test_indent_dumper(self):
        """Test IndentDumper produces properly indented YAML."""
        data = {
            "level1": {"level2": {"level3": "value"}},
            "list": ["item1", "item2"],
        }

        import io

        stream = io.StringIO()
        yaml.dump(data, stream=stream, Dumper=IndentDumper)
        result = stream.getvalue()

        # Check that the YAML is properly indented
        lines = result.strip().split("\n")
        # level2 should be indented
        level2_line = next(line for line in lines if "level2:" in line)
        self.assertTrue(level2_line.startswith("  "))
        # level3 should be further indented
        level3_line = next(line for line in lines if "level3:" in line)
        self.assertTrue(level3_line.startswith("    "))

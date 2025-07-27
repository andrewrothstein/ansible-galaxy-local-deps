import os
import tempfile
from unittest import TestCase

from ansible_galaxy_local_deps.finder import (
    find,
    find_dcb_os,
    find_gha_buildyml,
    find_meta_main,
)


class TestFinder(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir)

    def test_find_existing_file(self):
        """Test find returns path for existing file."""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        result = find(self.test_dir, "test.txt")
        self.assertEqual(result, test_file)

    def test_find_missing_file(self):
        """Test find returns None for missing file."""
        result = find(self.test_dir, "missing.txt")
        self.assertIsNone(result)

    def test_find_nested_file(self):
        """Test find with nested path."""
        nested_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(nested_dir)

        test_file = os.path.join(nested_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        result = find(self.test_dir, os.path.join("subdir", "test.txt"))
        self.assertEqual(result, test_file)

    def test_find_directory_returns_none(self):
        """Test find returns None for directories."""
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)

        result = find(self.test_dir, "subdir")
        self.assertIsNone(result)

    def test_find_meta_main_exists(self):
        """Test find_meta_main with existing meta/main.yml."""
        meta_dir = os.path.join(self.test_dir, "meta")
        os.makedirs(meta_dir)

        main_file = os.path.join(meta_dir, "main.yml")
        with open(main_file, "w") as f:
            f.write("---\n")

        result = find_meta_main(self.test_dir)
        self.assertEqual(result, main_file)

    def test_find_meta_main_missing(self):
        """Test find_meta_main with missing meta/main.yml."""
        result = find_meta_main(self.test_dir)
        self.assertIsNone(result)

    def test_find_dcb_os_exists(self):
        """Test find_dcb_os with existing dcb-os.yml."""
        dcb_file = os.path.join(self.test_dir, "dcb-os.yml")
        with open(dcb_file, "w") as f:
            f.write("---\n")

        result = find_dcb_os(self.test_dir)
        self.assertEqual(result, dcb_file)

    def test_find_dcb_os_missing(self):
        """Test find_dcb_os with missing dcb-os.yml."""
        result = find_dcb_os(self.test_dir)
        self.assertIsNone(result)

    def test_find_gha_buildyml_exists(self):
        """Test find_gha_buildyml with existing .github/workflows/build.yml."""
        github_dir = os.path.join(self.test_dir, ".github", "workflows")
        os.makedirs(github_dir)

        build_file = os.path.join(github_dir, "build.yml")
        with open(build_file, "w") as f:
            f.write("---\n")

        result = find_gha_buildyml(self.test_dir)
        self.assertEqual(result, build_file)

    def test_find_gha_buildyml_missing(self):
        """Test find_gha_buildyml with missing .github/workflows/build.yml."""
        result = find_gha_buildyml(self.test_dir)
        self.assertIsNone(result)

    def test_find_absolute_path(self):
        """Test find works with absolute paths."""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        # Use absolute path as role_dir
        result = find(os.path.abspath(self.test_dir), "test.txt")
        self.assertEqual(result, os.path.abspath(test_file))

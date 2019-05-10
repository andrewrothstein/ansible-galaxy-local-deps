from unittest import TestCase
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ansiblegalaxylocaldeps.deps import effkey, extract_dependencies

class TestDeps(TestCase):

    def test_effkey(self):
        self.assertEqual(effkey({'role': 'a', 'src' : 'b'}), 'role', 'EffKey role before src')
        self.assertEqual(effkey({'src': 'a'}), 'src', 'EffKey only src')
        self.assertIsNone(effkey({'foo': 'bar'}), 'EffKey neither src nor role')

    def test_extract_dependencies(self):
        y = load("""---
dependencies:
  - role: test-role-1
  - role: test-role-2
        """, Loader=Loader)
        o = extract_dependencies(y)
        self.assertEqual(len(o), 2, 'count of simple extract_dependencies')
        self.assertEqual(o[0]['role'], 'test-role-1', 'simple extracted role name (1)')
        self.assertEqual(o[1]['role'], 'test-role-2', 'simple extracted role name (2)')


    def test_extract_dependencies_with_version(self):
        y = load("""---
dependencies:
  - role: test-role-1
    version: v1.0.0
  - role: test-role-2
    version: v2.0.0
        """, Loader=Loader)
        o = extract_dependencies(y)
        self.assertEqual(len(o), 2, 'count of extract_dependencies with versions')
        self.assertEqual(o[0]['role'], 'test-role-1', 'extracted role name (1)')
        self.assertEqual(o[0]['version'], 'v1.0.0', 'extracted role version (1)')
        self.assertEqual(o[1]['role'], 'test-role-2', 'extracted role name (2))')
        self.assertEqual(o[1]['version'], 'v2.0.0', 'extracted role version (2)')



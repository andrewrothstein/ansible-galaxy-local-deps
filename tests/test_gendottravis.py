from unittest import TestCase
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ansiblegalaxylocaldeps.gendottravis import extract_osl_from_dottravis, from_dcb_os_yml

class TestGenDotTravis(TestCase):
    def test_extract_osl_from_dottravis(self):
        y = load("""---
env:
  - OS=xyz
  - OS=abc
""", Loader=Loader)
        osl = extract_osl_from_dottravis(y)
        self.assertEqual(len(osl), 2, 'osl length')
        self.assertEqual(osl[0], 'xyz', 'chopped OS= correctly')

    def test_from_dcb_os_yml(self):
        osl = ['xyz', 'abc']
        python_ver = '1.2.3.4'
        r = from_dcb_os_yml(osl, python_ver)
        self.assertEqual(r['python'], python_ver)
        self.assertEqual(len(r['env']), 2)
        self.assertEqual(r['env'][0], 'OS=xyz')
        self.assertEqual(r['env'][1], 'OS=abc')

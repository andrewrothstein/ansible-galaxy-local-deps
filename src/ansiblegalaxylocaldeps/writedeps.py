import argparse
import logging
import os
import sys
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup

from typing import Union

def run(role_dir: str):
  log = logging.getLogger('ansible-galaxy-local-deps.writedeps.run')
  o = deps.slurp(role_dir)
  of = os.path.join(role_dir, 'requirements.yml')
  log.info('writing out {0} dependencies to {1}...'.format(len(o), of))
  with open(of, 'w') as w:
    w.write(dump(o))

def main():
  loggingsetup.go()

  parser = argparse.ArgumentParser(
    description='generates a requirements.yml from an Ansible roles meta/main.yml file'
  )
  parser.add_argument('roledirs', nargs='*', default=['.'])
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(roledir)

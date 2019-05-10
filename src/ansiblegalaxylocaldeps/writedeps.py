import sys
import yaml
import os
import logging
import argparse

import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.deps as deps

from typing import Union

def run(role_dir: str):
  log = logging.getLogger('ansible-galaxy-local-deps.writedeps.run')
  o = deps.slurp(role_dir)
  of = os.path.join(role_dir, 'requirements.yml')
  log.info('writing out {0} dependencies to {1}...'.format(len(o), of))
  with open(of, 'w') as w:
    w.write(yaml.dump(o))

def main():
  loggingsetup.go()

  parser = argparse.ArgumentParser(
    description='generates a requirements.yml from an Ansible roles meta/main.yml file'
  )
  parser.add_argument('roledirs', nargs='+', default=['.'])
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(roledir)

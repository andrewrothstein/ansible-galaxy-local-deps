import argparse
import logging
import os
import sys

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp

def run(role_dir: str) -> None:
  mm = slurp.slurp_meta_main(role_dir)
  y = deps.extract_dependencies(mm)
  dump.dump_requirements_yml(role_dir, y)

def main() -> None:
  loggingsetup.go()

  parser = argparse.ArgumentParser(
    description='generates a requirements.yml from an Ansible roles meta/main.yml file'
  )
  parser.add_argument('roledirs', nargs='*', default=['.'])
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(roledir)

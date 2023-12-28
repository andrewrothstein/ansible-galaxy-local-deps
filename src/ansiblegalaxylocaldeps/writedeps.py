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
  if 'dependencies' in mm:
    dump.dump_requirements_yml(
      role_dir,
      deps.extract_dependencies(mm['dependencies'])
    )

def main() -> None:
  loggingsetup.go()

  parser = argparse.ArgumentParser(
    description='extracts dependencies from meta/main.yml and writes out meta/requirements.yml'
  )
  parser.add_argument('roledirs', nargs='*', default=[os.getcwd()])
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(roledir)

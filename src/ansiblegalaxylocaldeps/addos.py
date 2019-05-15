import argparse
import logging
import os
import sys

import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp


def run(role_dir: str, ifcontains: str, add: str) -> None:
  osl = slurp.slurp_dcb_os_yml(role_dir)
  if osl is not None:
    s = set(osl)
    if ifcontains in s and not add in s:
      s.add(add)
      l = list(s)
      l.sort()
      dump.dump_dcb_os_yml(role_dir, l)


def main() -> None:
  loggingsetup.go()

  parser = argparse.ArgumentParser(
    description='modified a dependency in an Ansible roles meta/main.yml file'
  )
  parser.add_argument('roledirs', nargs='*', default=['.'])
  parser.add_argument('--ifcontains')
  parser.add_argument('--add')
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(roledir, args.ifcontains, args.add)

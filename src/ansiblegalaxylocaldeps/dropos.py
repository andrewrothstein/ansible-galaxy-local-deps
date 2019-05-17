import argparse
import logging
import os
import sys

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp


def run(role_dir: str, ifcontainsrole: str, todrop: str) -> None:
  mm = slurp.slurp_meta_main(role_dir)
  droles = deps.extract_dependencies(mm) if mm is not None else None
  if droles is not None:
    for role in droles:
      role_name = role['role']
      if role_name == ifcontainsrole:
        osl = slurp.slurp_dcb_os_yml(role_dir)
        if osl is not None:
          new_osl = []
          for os in osl:
            if not todrop in os:
              new_osl.append(os)
          l = list(set(new_osl))
          l.sort()
          dump.dump_dcb_os_yml(role_dir, l)
          return None

def main() -> None:
  loggingsetup.go()

  parser = argparse.ArgumentParser(
    description='modified a dependency in an Ansible roles meta/main.yml file'
  )
  parser.add_argument('roledirs', nargs='*', default=['.'])
  parser.add_argument('--ifcontainsrole')
  parser.add_argument('--todrop')
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(roledir, args.ifcontainsrole, args.todrop)

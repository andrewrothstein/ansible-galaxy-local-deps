import argparse
import logging
import os
import sys

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp

def fmt_role(r: str, v: str):
  if v is None:
    return {'role': r}
  else:
    return {'role': r, 'version': v}

def run(role_dir: str, from_role: str, from_ver: str, to_role: str, to_ver: str) -> None:
  mm = slurp.slurp_meta_main(role_dir)
  if mm is not None:
    o = []
    y = deps.extract_dependencies(mm)
    if y is not None:
      modified = False
      for r in y:
        if 'role' in r and from_role == r['role']:
          if from_ver is None:
            o.append(fmt_role(to_role, to_ver))
            modified = True
          elif 'version' in r and r['version'] == from_ver:
            o.append(fmt_role(to_role, to_ver))
            modified = True
          else:
            o.append(r)
        else:
          o.append(r)
      if modified:
        mm['dependencies'] = o
        dump.dump_meta_main(role_dir, mm)


def main() -> None:
  loggingsetup.go()

  parser = argparse.ArgumentParser(
    description='modified a dependency in an Ansible roles meta/main.yml file'
  )
  parser.add_argument('roledirs', nargs='*', default=['.'])
  parser.add_argument('--fromrole')
  parser.add_argument('--fromver', default=None)
  parser.add_argument('--torole')
  parser.add_argument('--tover', default=None)
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(roledir, args.fromrole, args.fromver, args.torole, args.tover)

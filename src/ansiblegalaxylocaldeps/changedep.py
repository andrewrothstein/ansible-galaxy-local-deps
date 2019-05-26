import argparse
import logging
import os
import sys

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp

def adjust_role(role_map, ek: str, r: str, v: str):
  if ek != 'role':
    role_map['role'] = role_map[ek]
    role_map.pop(ek)
  if v is None:
    role_map['role'] = r
  else:
    role_map['role'] = r
    role_map['version'] = v
  return role_map

def rewrite_deps(
    d_yml,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str
):
  modified = False
  o = []
  for r in d_yml:
    ek = deps.effkey(r)
    if ek is not None and from_role == r[ek]:
      if from_ver is None:
        o.append(adjust_role(r, ek, to_role, to_ver))
        modified = True
      elif 'version' in r and r['version'] == from_ver:
        o.append(adjust_role(r, ek, to_role, to_ver))
        modified = True
      else:
        o.append(r)
    else:
      o.append(r)
  return o if modified else None

def rewrite_meta_main(
    role_dir: str,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str
):
  mm = slurp.slurp_meta_main(role_dir)
  if mm is not None:
    o = []
    y = deps.extract_dependencies(mm)
    if y is not None:
      modified = rewrite_deps(
        y,
        from_role,
        from_ver,
        to_role,
        to_ver
      )
      if modified:
        mm['dependencies'] = modified
        dump.dump_meta_main(role_dir, mm)

def rewrite_test_requirements_yml(
    role_dir: str,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str
):
  tr = slurp.slurp_test_requirements_yml(role_dir)
  if tr:
    mtr = rewrite_deps(
      tr,
      from_role,
      from_ver,
      to_role,
      to_ver
    )
    if mtr:
      dump.dump_test_requirements_yml(role_dir, mtr)

def run(
    role_dir: str,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str
) -> None:
  rewrite_meta_main(
    role_dir,
    from_role,
    from_ver,
    to_role,
    to_ver
  )
  rewrite_test_requirements_yml(
    role_dir,
    from_role,
    from_ver,
    to_role,
    to_ver
  )

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

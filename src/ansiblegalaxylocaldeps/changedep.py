import argparse
import logging
import os
import sys

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp

def adjust_role(role_map, ek: str, r: str, v: str):
  if ek != 'name':
    role_map['name'] = role_map[ek]
    role_map.pop(ek)
  if v is None:
    role_map['name'] = r
  else:
    role_map['name'] = r
    role_map['version'] = v
  return role_map

def rewrite(
    r_yml,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str
):
  if r_yml is None:
    return None

  o = []
  modified = False
  for r in r_yml:
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

def rewrite_meta_requirements_yml(
    role_dir: str,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str
):
  modified = rewrite(
    slurp.slurp_meta_requirements_yml(role_dir),
    from_role,
    from_ver,
    to_role,
    to_ver
  )
  if modified:
    dump.dump_meta_requirements_yml(role_dir, modified)

def rewrite_test_requirements_yml(
    role_dir: str,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str
):
  modified = rewrite(
    slurp.slurp_test_requirements_yml(role_dir),
    from_role,
    from_ver,
    to_role,
    to_ver
  )
  if modified:
    dump.dump_test_requirements_yml(role_dir, modified)

def run(
    role_dir: str,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str
) -> None:
  log = logging.getLogger('ansible-galaxy-local-deps-change-dep')

  log.info(
    "changing role {0} to {1}".format(
      from_role if from_ver is None else "{0}:{1}".format(from_role, from_ver),
      to_role if to_ver is None else "{0}:{1}".format(to_role, to_ver)
    )
  )
  rewrite_meta_requirements_yml(
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
    description="modified dependencies in meta/requirements.yml and test-requirements.yml files"
  )
  parser.add_argument('roledirs', nargs='*', default=[os.getcwd()])
  parser.add_argument('--role')
  parser.add_argument('--fromver', default=None)
  parser.add_argument('--torole', default=None)
  parser.add_argument('--tover', default=None)
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(
      roledir,
      args.role,
      args.fromver,
      args.role if args.torole is None else args.torole,
      args.tover
    )

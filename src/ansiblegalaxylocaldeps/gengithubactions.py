import argparse
import logging
import os
from typing import List

import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp
import ansiblegalaxylocaldeps.platform_matrix as platform_matrix

def build_yml(ver: str="v1"):
    return {
        'on': 'push',
        'jobs': {
            'bake-ansible-images-v1': {
                'uses': 'andrewrothstein/.github/.github/workflows/bake-ansible-images-{}.yml@develop'.format(ver)
            }
        }
    }

def migrate_dcb_os(
        role_dir: str
):
    dcb_os = os.path.join(role_dir, "dcb-os.yml")
    if os.path.exists(dcb_os):
        pm = platform_matrix.from_dcb_osl(
            slurp.slurp_dcb_os_yml(role_dir)
        )
        dump.dump_platform_matrix_json(role_dir, pm)
        os.remove(dcb_os)
    else:
        pm = platform_matrix.upgrade(
            slurp.slurp_platform_matrix_json(role_dir)
            )
        dump.dump_platform_matrix_json(role_dir, pm)

def mksubdirs(role_dir: str, subs: List[str]):
    d = role_dir
    for s in subs:
        d = os.path.join(d, s)
        if not os.path.isdir(d):
            os.mkdir(d, 0o755)

def main():
    loggingsetup.go()
    parser = argparse.ArgumentParser(
        description='generates a .github/workflows/build.yml for building/testing Ansible roles with docker buildx bake'
    )
    log = logging.getLogger('ansible-galaxy-local-deps.gengithubactions.main')
    parser.add_argument('roledirs', nargs='*', default=['.'])
    parser.add_argument('--ver', default="v1")
    args = parser.parse_args()
    for role_dir in args.roledirs:
        mksubdirs(role_dir, [".github", "workflows"])
        migrate_dcb_os(role_dir)
        dump.dump_github_actions_build_yml(role_dir, build_yml(args.ver))
        dump.dump_gitignore(role_dir)

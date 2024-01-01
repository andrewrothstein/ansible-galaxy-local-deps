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

def render_meta_main(role_dir: str, pm):
    log = logging.getLogger('ansible-galaxy-local-deps.gengithubactions.render_meta_main')
    mm = slurp.slurp_meta_main_yml(role_dir)

    # flatten the license list
    l = mm['galaxy_info']['license']
    if isinstance(l, list):
        mm['galaxy_info']['license'] = l[0]

    min_ansible_version = mm['galaxy_info']['min_ansible_version']
    if isinstance(min_ansible_version, float):
        mm['galaxy_info']['min_ansible_version'] = str(min_ansible_version)

    mm['galaxy_info']['platforms'] = platform_matrix.render_platforms(pm)

    if 'namespace' not in mm['galaxy_info']:
        mm['galaxy_info']['namespace'] = 'andrewrothstein'

    if 'role_name' not in mm['galaxy_info']:
        log.info('computing role_name from role directory: {}'.format(role_dir))
        d = os.path.basename(role_dir)
        if d.startswith('ansible-'):
            rn = d.removeprefix('ansible-')
            log.info('computed role_name: {}'.format(rn))
            mm['galaxy_info']['role_name'] = rn

    dump.dump_meta_main_yml(role_dir, mm)

def upgrade_platform_matrix(
        role_dir: str
):
    dcb_os = os.path.join(role_dir, "dcb-os.yml")
    pm = None
    if os.path.exists(dcb_os):
        pm = platform_matrix.from_dcb_osl(
            slurp.slurp_dcb_os_yml(role_dir)
        )
        os.remove(dcb_os)
    else:
        pm = platform_matrix.upgrade(
            slurp.slurp_platform_matrix_json(role_dir)
            )
    dump.dump_platform_matrix_json(role_dir, pm)
    render_meta_main(role_dir, pm)

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
    parser.add_argument('roledirs', nargs='*', default=[os.getcwd()])
    parser.add_argument('--ver', default="v1")
    args = parser.parse_args()
    for role_dir in args.roledirs:
        mksubdirs(role_dir, [".github", "workflows"])
        upgrade_platform_matrix(role_dir)
        dump.dump_github_actions_build_yml(role_dir, build_yml(args.ver))
        dump.dump_gitignore(role_dir)

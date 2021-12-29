import argparse
import logging
import os
from typing import List

import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp

def dump_requirements_txt(
        role_dir: str,
        dcb_ver: str
):
    dump.dump_requirements_txt(
        role_dir,
        '\n'.join([
            'dcb == {}'.format(dcb_ver)
        ])
    )

def build_steps(
    role_dir: str,
    registry: str = 'ghcr.io'
    ):
    syml = slurp.slurp_script_yml(role_dir)
    if syml:
        return syml
    else:
        return [
            {
                'name': 'dcb #ftw',
                'run' : ' '.join([
                    'dcb',
                    '--upstreamregistry', registry,
                    '--upstreamgroup andrewrothstein',
                    '--upstreamapp docker-ansible',
                    '--targetregistry', registry,
                    '--targetuser', '${{ github.actor }}',
                    '--targetpwd', '${{ github.token }}',
                    '--snippet from.j2 ansible-test-role.j2',
                    '--pullall',
                    '--writeall',
                    '--buildall',
                    '--pushall',
                    '--alltags ${{ matrix.os }}'
                    ])
            }
        ]

def from_dcb_os_yml(
        steps: str,
        osl: List[str],
        ci_dist: str,
        python_ver: str
):
    return {
        'name': 'dcb',
        'on': ['push'],
        'jobs': {
            'build': {
                'runs-on': ci_dist,
                'strategy': {
                    'matrix': {
                        'os': osl,
                        'python-versions': [python_ver]
                    }
                },
                'steps': [
                    {
                        'uses': 'actions/checkout@v2'
                    },
                    {
                        'name': 'Set up Python ${{ matrix.python-version }}',
                        'uses': 'actions/setup-python@v2',
                        'with': {
                            'python-version': '${{ matrix.python-version }}'
                        }
                    },
                    {
                        'name': 'Install Python dependencies',
                        'run': "\n".join([
                            'python -m pip install --upgrade pip',
                            'if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; fi'
                        ])
                    }
                ] + steps
            }
        }
    }

def from_dcb_os(
        role_dir: str,
        ci_dist: str,
        python_ver: str,
        dcb_ver: str
):
    osl = slurp.slurp_dcb_os_yml(role_dir)
    steps = build_steps(role_dir)
    build_yml = from_dcb_os_yml(
        steps,
        osl,
        ci_dist,
        python_ver
    ) if osl is not None else None

    if build_yml is not None:
        dump.dump_github_actions_build_yml(role_dir, build_yml)
        dump_requirements_txt(role_dir, dcb_ver)
        dump.dump_gitignore(role_dir)

def mksubdirs(role_dir: str, subs: List[str]):
    d = role_dir
    for s in subs:
        d = os.path.join(d, s)
        if not os.path.isdir(d):
            os.mkdir(d, 0o755)

def main():
    loggingsetup.go()
    parser = argparse.ArgumentParser(
        description='generates a .github/workflows/build.yml for building/testing Ansible roles with dcb/docker'
    )
    log = logging.getLogger('ansible-galaxy-local-deps.gengithubactions.main')
    parser.add_argument('roledirs', nargs='*', default=['.'])
    parser.add_argument('-c', '--cidist', default='ubuntu-latest')
    parser.add_argument('-p', '--pythonver', default='3.9')
    parser.add_argument('-d', '--dcbver', default='0.1.2')
    args = parser.parse_args()
    for role_dir in args.roledirs:
        mksubdirs(role_dir, [".github", "workflows"])
        from_dcb_os(
            role_dir,
            args.cidist,
            args.pythonver,
            args.dcbver
        )

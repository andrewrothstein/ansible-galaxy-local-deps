import argparse
import logging
import os
from typing import List

import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp

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
                'name': 'task #ftw',
                'run': " ".join([
                    'task',
                    '-t taskmono/ansible-test-role.yml',
                    '"targetuser=${{ github.actor }}"',
                    '"targetpwd=${{ github.token }}"',
                    '"alltags=${{ matrix.os }}"'
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
                    'fail-fast': False,
                    'matrix': {
                        'os': osl,
                        'python-version': [python_ver]
                    }
                },
                'steps': [
                    {
                        'uses': 'actions/checkout@v3'
                    },
                    {
                        'name': 'install python ${{ matrix.python-version }}',
                        'uses': 'actions/setup-python@v4',
                        'with': {
                            'python-version': '${{ matrix.python-version }}'
                        }
                    },
                    {
                        'name': 'install task',
                        'uses': 'arduino/setup-task@v1',
                        'with': {
                            'repo-token': '${{ github.token }}'
                        }
                    },
                    {
                        'name': 'task ver',
                        'run': 'task --version'
                    },
                    {
                        'name': 'download task mono',
                        'uses': 'actions/checkout@v2',
                        'with': {
                            'repository': 'andrewrothstein/tasks',
                            'ref': 'develop',
                            'path': 'taskmono'
                        }
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
    parser.add_argument('-p', '--pythonver', default='3.11')
    parser.add_argument('-d', '--dcbver', default='0.1.3')
    args = parser.parse_args()
    for role_dir in args.roledirs:
        mksubdirs(role_dir, [".github", "workflows"])
        from_dcb_os(
            role_dir,
            args.cidist,
            args.pythonver,
            args.dcbver
        )

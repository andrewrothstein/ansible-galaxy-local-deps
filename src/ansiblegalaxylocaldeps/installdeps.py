import argparse
import logging
import os
from subprocess import check_call
import sys

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp

def install(r: str, v: str=None) -> None:
    log = logging.getLogger('ansible-galaxy-local-deps.installdeps.install')
    log.info('installing {0} version {1}...'.format(r, v))
    p = ','.join([r, v]) if v is not None else r
    check_call(['ansible-galaxy', '-f', 'install', p])

def run(role_dir: str) -> None:
    log = logging.getLogger('ansible-galaxy-local-deps.installdeps.run')
    mm = slurp.slurp_meta_main(role_dir)
    y = deps.extract_dependencies(mm)
    if y:
        for d in y:
            if 'role' in d:
                install(d['role'], d['version'] if 'version' in d else None)
            else:
                log.info('ignoring key {}'.format(d))
        else:
            log.info('no dependencies')

def main():
    loggingsetup.go()

    parser = argparse.ArgumentParser(
        description='uses ansible-galaxy to install all of an Ansible roles meta/main.yml specified requirements'
    )
    parser.add_argument('roledirs', nargs='*', default=['.'])
    args = parser.parse_args()
    for roledir in args.roledirs:
        run(roledir)


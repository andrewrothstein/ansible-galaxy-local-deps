import argparse
import logging
import os
from subprocess import check_call
import sys

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp

def install_role(r: str, v: str=None) -> None:
    log = logging.getLogger('ansible-galaxy-local-deps.installdeps.install')
    log.info('installing {0} version {1}...'.format(r, v))
    p = ','.join([r, v]) if v is not None else r
    check_call(['ansible-galaxy', 'install', '-f', p])


def install_all(y) -> None:
    if y is not None:
        for d in y:
            efk = deps.effkey(d)
            if efk is not None:
                install_role(
                    d[efk],
                    d['version'] if 'version' in d else None
                )
            else:
                log.info('ignoring key {}'.format(d))
    else:
        log.info('no dependencies')

def run(role_dir: str) -> None:
    log = logging.getLogger(
        'ansible-galaxy-local-deps.installdeps.run'
    )
    install_all(
        deps.extract_dependencies(
            slurp.slurp_meta_requirements(role_dir)
        )
    )
    install_all(
        deps.extract_dependencies(
            slurp.slurp_test_requirements(role_dir)
        )
    )


def main():
    loggingsetup.go()

    parser = argparse.ArgumentParser(
        description='uses ansible-galaxy to install all dependencies from test-requirements.yml and meta/requirements.yml'
    )
    parser.add_argument('roledirs', nargs='*', default=[os.getcwd()])
    args = parser.parse_args()
    for roledir in args.roledirs:
        run(roledir)

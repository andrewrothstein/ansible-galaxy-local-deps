import argparse
import logging
import os
from subprocess import check_call
import sys

import ansiblegalaxylocaldeps.deps as deps
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup

from typing import Union

def install(r, v):
    log = logging.getLogger('ansible-galaxy-local-deps.installdeps.install')
    log.info('installing {0} version {1}...'.format(r, v))
    check_call(['ansible-galaxy', '-f', 'install', ','.join([r, v])])

def install_sans_ver(r):
    log = logging.getLogger('ansible-galaxy-local-deps.installdeps.install_sans_ver')
    log.info('installing latest {0}...'.format(r))
    check_call(['ansible-galaxy', '-f', 'install', r])

def run(role_dir: str):
    log = logging.getLogger('ansible-galaxy-local-deps.installdeps.run')
    o = deps.slurp(role_dir)
    if o:
        for d in o:
            if 'role' in d:
                if 'version' in d:
                    install(d['role'], d['version'])
                else:
                    install_sans_ver(d['role'])
            else:
                print('ignoring', d)
        else:
            log.info('no dependencies')

def main():
    loggingsetup.go()

    parser = argparse.ArgumentParser(
        description='uses ansible-galaxy to install all of an Ansible roles meta/main.yml specified requirements'
    )
    parser.add_argument('roledirs', nargs='+', default=['.'])
    args = parser.parse_args()
    for roledir in args.roledirs:
        run(roledir)


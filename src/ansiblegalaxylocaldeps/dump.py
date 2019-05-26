import logging
import os
import sys
from yaml import dump as ydump
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


def dump_txt(role_dir: str, f: str, t: str) -> None:
    log = logging.getLogger('ansible-galaxy-local-deps.dump.dump_txt')
    of = os.path.join(role_dir, f)
    log.info('writing out {}...'.format(of))
    with open(of, 'w') as w:
        w.write(t)

def dump_yml(role_dir: str, f: str, y: str) -> None:
    log = logging.getLogger('ansible-galaxy-local-deps.dump.dump_yml')
    of = os.path.join(role_dir, f)
    log.info('writing out {}...'.format(of))
    with open(of, 'w') as w:
        w.write(ydump(y))

def dump_meta_main(role_dir: str, y) -> None:
    dump_yml(role_dir, os.path.join('meta', 'main.yml'), y)

def dump_requirements_yml(role_dir: str, y) -> None:
    dump_yml(role_dir, 'requirements.yml', y)

def dump_dottravis_yml(role_dir: str, dott) -> None:
    dump_yml(role_dir, '.travis.yml', dott)

def dump_requirements_txt(role_dir: str, t: str) -> None:
    dump_txt(role_dir, 'requirements.txt', t)

def dump_dcb_os_yml(role_dir: str, y) -> None:
    dump_yml(role_dir, 'dcb-os.yml', y)

def dump_test_requirements_yml(role_dir: str, y) -> None:
    dump_yml(role_dir, 'test-requirements.yml', y)

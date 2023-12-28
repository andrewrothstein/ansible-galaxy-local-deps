import logging
import os
import json
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from ansiblegalaxylocaldeps import finder as finder

def slurp_yml(role_dir: str, f: str):
    log = logging.getLogger('ansible-galaxy-local-deps.slurp.slurp_yml')
    fq = finder.find(role_dir, f)
    if fq:
        log.info('found {0}. slurping...'.format(fq))
        with open(fq, 'r') as ifq:
            return load(ifq, Loader=Loader)
    return None

def slurp_json(role_dir: str, f: str):
    log = logging.getLogger('ansible-galaxy-local-deps.slurp.slurp_json')
    fq = finder.find(role_dir, f)
    if fq:
        log.info('found {0}. slurping...'.format(fq))
        with open(fq, 'r') as ifq:
            return json.load(ifq)
    return None

def slurp_meta_main_yml(role_dir: str):
    return slurp_yml(
        role_dir,
        os.path.join('meta', 'main.yml')
    )

def slurp_meta_requirements_yml(role_dir: str):
    return slurp_yml(
        role_dir,
        os.path.join('meta', 'requirements.yml')
    )

def slurp_test_requirements_yml(role_dir: str):
    return slurp_yml(role_dir, 'test-requirements.yml')

def slurp_dcb_os_yml(role_dir: str):
    return slurp_yml(role_dir, 'dcb-os.yml')

def slurp_script_yml(role_dir: str):
    return slurp_yml(role_dir, 'script.yml')

def slurp_platform_matrix_json(role_dir: str):
    return slurp_json(role_dir, 'platform-matrix-v1.json')

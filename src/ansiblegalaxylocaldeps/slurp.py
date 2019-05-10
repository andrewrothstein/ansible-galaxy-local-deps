import logging
import os
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from ansiblegalaxylocaldeps import finder as finder

def slurp(role_dir: str, f: str):
    log = logging.getLogger('ansible-galaxy-local-deps.slurp.slurp')
    fq = finder.find(role_dir, f)
    if fq:
        log.info('found {0}. slurping...'.format(fq))
        with open(fq, 'r') as ifq:
            return load(ifq, Loader=Loader)
    return None

def slurp_meta_main(role_dir: str):
    return slurp(role_dir, os.path.join('meta', 'main.yml'))

def slurp_dottravis(role_dir: str):
    return slurp(role_dir, '.travis.yml')

def slurp_dcb_os_yml(role_dir: str):
    return slurp(role_dir, 'dcb-os.yml')

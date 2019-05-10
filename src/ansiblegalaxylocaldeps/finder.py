import logging
import os

from typing import Union

def find(role_dir: str, f: str) -> Union[str, None]:
    log = logging.getLogger('ansible-galaxy-local-deps.finder.find')
    fq = os.path.join(role_dir, f)
    log.info('looking for {0}...'.format(fq))
    return fq if os.path.isfile(fq) else None

def find_meta_main(role_dir: str) -> Union[str, None]:
    return find(role_dir, os.path.join('meta', 'main.yml'))

def find_dcb_os(role_dir: str) -> Union[str, None]:
    return find(role_dir, 'dcb-os.yml')

def find_dottravis(role_dir: str) -> Union[str, None]:
    return find(role_dir, '.travis.yml')


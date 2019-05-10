import logging
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from typing import Union

import ansiblegalaxylocaldeps.finder as finder

def effkey(d) -> Union[str, None]:
  if 'role' in d:
    return 'role'
  elif 'src' in d:
    return 'src'
  else:
    return None

def extract_dependencies(y):
  log = logging.getLogger('ansible-galaxy-local-deps.deps.extract_dependencies')
  o = []
  if 'dependencies' in y:
    for d in y['dependencies']:
      key = effkey(d)
      if key:
        r = d[key]
        if 'version' in d:
          o.append({'role' : r, 'version' : d['version']})
        else:
          o.append({'role' : r})
      else:
        log.warn('ignoring key: {0}'.format(d))
  return o

def slurp(role_dir: str):
  log = logging.getLogger('ansible-galaxy-local-deps.deps.slurp')
  meta_main = finder.find_meta_main(role_dir)
  if meta_main:
    log.info('found. looking for dependencies in {0}...'.format(meta_main))
    with open(meta_main, 'r') as f:
      y = load(f, Loader=Loader)
    return extract_dependencies(y)
  return None

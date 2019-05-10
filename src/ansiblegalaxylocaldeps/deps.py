import logging

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
  if y is not None and 'dependencies' in y:
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


import logging

from typing import Union

import ansiblegalaxylocaldeps.finder as finder

def effkey(d) -> Union[str, None]:
  if 'name' in d:
    return 'name'
  elif 'role' in d:
    return 'role'
  elif 'src' in d:
    return 'src'
  else:
    return None

def extract_dependencies(y):
  """extract dependencies from a requirements.yml yaml data"""
  log = logging.getLogger('ansible-galaxy-local-deps.deps.extract_dependencies')
  o = []
  for r in y:
    key = effkey(d)
    if key:
      d['name'] = d[key]
        if key != 'name':
          d.pop(key)
        o.append(d)
      else:
        log.warn('ignoring dependency: {0}'.format(d))
  return o

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

def extract_dependencies(requirements_yml):
  """extract dependencies from a requirements.yml yaml data"""
  log = logging.getLogger('ansible-galaxy-local-deps.deps.extract_dependencies')
  o = []
  for r in requirements_yml:
    key = effkey(r)
    if key:
      r['name'] = r[key]
      if key != 'name':
        r.pop(key)
      o.append(r)
    else:
      log.warn('ignoring dependency: {0}'.format(r))
  return o

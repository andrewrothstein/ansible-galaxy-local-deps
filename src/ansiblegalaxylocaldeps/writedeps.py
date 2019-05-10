import sys
import yaml
import os
import logging
import argparse
from typing import Union

def effkey(d) -> Union[str, None]:
  if 'role' in d:
    return 'role'
  elif 'src' in d:
    return 'src'
  else:
    return None

def find(role_dir: str, f: str) -> Union[str, None]:
  log = logging.getLogger('ansible-galaxy-local-deps-write.find')
  fq = os.path.join(role_dir, f)
  log.info('looking for {0}...'.format(fq))
  if os.path.isfile(fq):
    return fq
  return None

def find_meta_main(role_dir: str):
  return find(role_dir, os.path.join('meta', 'main.yml'))

def extract_dependencies(y):
  log = logging.getLogger('ansible-galaxy-local-deps-write.extract_dependencies')
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

def run(role_dir: str):
  log = logging.getLogger('ansible-galaxy-local-deps-write.run')
  meta_main = find_meta_main(role_dir)
  if meta_main is not None:
    log.info('found. looking for dependencies in {0}...'.format(meta_main))
    with open(meta_main, 'r') as f:
      y = yaml.load(f, Loader=yaml.FullLoader)
    o = extract_dependencies(y)
    of = os.path.join(role_dir, 'requirements.yml')
    log.info('writing out {0} dependencies to {1}...'.format(len(o), of))
    with open(of, 'w') as w:
      w.write(yaml.dump(o))

def main():
  logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
  )

  parser = argparse.ArgumentParser(
    description='generates a requirements.yml from an Ansible roles meta/main.yml file'
  )
  parser.add_argument('roledirs', nargs='+', default=['.'])
  args = parser.parse_args()
  for roledir in args.roledirs:
    run(roledir)

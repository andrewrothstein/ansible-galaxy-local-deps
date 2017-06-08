import sys
import yaml
import os
import logging

def effkey(d):
  if 'role' in d:
    return 'role'
  elif 'src' in d:
    return 'src'
  else:
    return None

def run():
  log = logging.getLogger("ansible-galaxy-local-deps-write")

  meta_main = 'meta/main.yml'
  log.info('looking for {0}...'.format(meta_main))
  if os.path.isfile(meta_main):
    log.info('found. looking for dependencies in {0}...'.format(meta_main))
    with open(meta_main, 'r') as f:
      y = yaml.load(f)
      if 'dependencies' in y:
	log.info('found {0} dependencies...'.format(len(y['dependencies'])))
	o = []
	for d in y['dependencies']:
	  key = effkey(d)
          if key:
	    r = d[key]
            if 'version' in d:
              o.append({'src' : r, 'version' : d['version']})
            else:
              o.append({'src' : r})
          else:
            log.warn('ignoring {0}'.format(d))

	log.info('writing out requirements.yml...')
	with open('requirements.yml', 'w') as r:
          r.write(yaml.dump(o))
      else:
	log.info('no dependencies')
  else:
    log.info('{0} not found'.format(meta_main))

def main():
  logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
  )
  run()

import sys
import yaml
import os
from subprocess import check_call

def install(r, v):
    print('installing', r, 'version', v, '...')
    check_call(['ansible-galaxy', '-f', 'install', r + ',' + v])

def install_sans_ver(r):
    print('installing latest', r, '...')
    check_call(['ansible-galaxy', '-f', 'install', r])

def main(args=None):
    meta_main = 'meta/main.yml'
    print('looking for', meta_main, '...')
    if os.path.isfile(meta_main):
        print('found. looking for dependencies...')
        with open(meta_main, 'r') as f:
            y = yaml.load(f)
            if 'dependencies' in y:
                for d in y['dependencies']:
                    if 'role' in d:
                        if 'version' in d:
                            install(d['role'], d['version'])
                        else:
                            install_sans_ver(d['role'])
                    else:
                        print('ignoring', d)
            else:
                print('no dependencies')
    else:
        print(meta_main, 'not found.')

if __name__ == "__main__" :
    main()

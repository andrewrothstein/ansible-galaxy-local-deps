import sys
import yaml
import os

def main(args=None):
    meta_main = 'meta/main.yml'
    print('looking for', meta_main, '...')
    if os.path.isfile(meta_main):
        print('found. looking for dependencies...')
        with open(meta_main, 'r') as f:
            y = yaml.load(f)
            if 'dependencies' in y:
                o = []
                for d in y['dependencies']:
                    if 'role' in d:
                        if 'version' in d:
                            o.append({'src' : d['role'], 'version' : d['version']})
                        else:
                            o.append({'src' : d['role']})
                    else:
                        print('ignoring', d)
                with open('requirements.yml', 'w') as r:
                    r.write(yaml.dump(o))
            else:
                print('no dependencies')
    else:
        print(meta_main, 'not found.')

if __name__ == "__main__" :
    main()

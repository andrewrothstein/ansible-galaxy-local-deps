import argparse
from typing import List

import ansiblegalaxylocaldeps.dump as dump
import ansiblegalaxylocaldeps.loggingsetup as loggingsetup
import ansiblegalaxylocaldeps.slurp as slurp


def extract_osl_from_dottravis(dottravis) -> List[str]:
    osl = []
    for fmtos in dottravis['env']:
        if fmtos.startswith('OS='):
            osl.append(fmtos[3:])
    return osl

def fmt_osl(osl: List[str]) -> List[str]:
    return ['OS={}'.format(o) for o in osl]

def dump_requirements_txt(
        role_dir: str,
        dcb_ver: str,
        ansiblegalaxylocaldeps_ver: str
):
    requirements_txt = '\n'.join([
        'ansible-galaxy-local-deps == {}'.format(ansiblegalaxylocaldeps_ver),
        'dcb == {}'.format(dcb_ver)
        ])
    dump.dump_requirements_txt(role_dir, requirements_txt)

def from_dcb_os_yml(
        osl: List[str],
        python_ver: str
):
    return {
        'dist': 'xenial',
        'sudo': 'required',
        'services': ['docker'],
        'language': 'python',
        'python': python_ver,
        'branches' : {
            'except': ['/^v\d+\.\d+(\.\d+)?(-\S*)?$/']
        },
        'env': fmt_osl(osl),
        'script': [
            'ansible-galaxy-local-deps-write',
            ' '.join([
                'dcb',
                '--upstreamgroup andrewrothstein',
                '--upstreamapp docker-ansible-role',
                '--alltags ${OS}',
                '--pullall',
                '--writeall',
                '--buildall',
                '--pushall'
                ])
            ]
    }


def from_dcb_os(
        role_dir: str,
        python_ver: str,
        dcb_ver: str,
        ansiblegalaxylocaldeps_ver: str
):
    osl = slurp.slurp_dcb_os_yml(role_dir)
    dtt = from_dcb_os_yml(osl, python_ver)
    dump.dump_dottravis_yml(role_dir, dtt)
    dump_requirements_txt(role_dir, dcb_ver, ansiblegalaxylocaldeps_ver)

def from_dottravis(
        role_dir: str,
        python_ver: str,
        dcb_ver: str,
        ansiblegalaxylocaldeps_ver: str
):
    dtt = slurp.slurp_dottravis(role_dir)
    osl = extract_osl_from_dottravis(dtt)
    dtt['env'] = fmt_osl(osl)
    dtt['python'] = python_ver
    dump.dump_dottravis_yml(role_dir, dtt)
    dump_requirements_txt(role_dir, dcb_ver, ansiblegalaxylocaldeps_ver)
    dump.dump_dcb_os_yml(role_dir, osl)

def main():
    loggingsetup.go()
    parser = argparse.ArgumentParser(
        description='generates a .travis.yml from building/testing Ansible roles with dcb/docker'
    )
    parser.add_argument('roledirs', nargs='*', default=['.'])
    parser.add_argument('-p', '--pythonver', default='3.7')
    parser.add_argument('-d', '--dcbver', default='0.0.17')
    parser.add_argument('-l', '--ansiblegalaxylocaldepsver', default='0.0.14')
    parser.add_argument('-a', '--action', default='from_dottravis')
    args = parser.parse_args()
    for role_dir in args.roledirs:
        if args.action == 'from_dcb_os':
            from_dcb_os(role_dir, args.pythonver, args.dcbver, args.ansiblegalaxylocaldepsver)
        elif args.action == 'from_dottravis':
            from_dottravis(role_dir, args.pythonver, args.dcbver, args.ansiblegalaxylocaldepsver)
        else:
            log.warning('unknown action: {}'.format(args.action))


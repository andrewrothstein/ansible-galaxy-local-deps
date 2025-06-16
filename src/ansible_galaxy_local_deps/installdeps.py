import argparse
import logging
import os
from subprocess import check_call

import ansible_galaxy_local_deps.deps as deps
import ansible_galaxy_local_deps.logging_setup as logging_setup
import ansible_galaxy_local_deps.slurp as slurp


def install_role(r: str, v: str = None) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps.installdeps.install")
    log.info("installing {0} version {1}...".format(r, v))
    p = ",".join([r, v]) if v is not None else r
    check_call(["ansible-galaxy", "install", "-f", p])


def install_all(y) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps.installdeps.install_all")
    if y is not None:
        for d in y:
            efk = deps.effkey(d)
            if efk is not None:
                install_role(d[efk], d["version"] if "version" in d else None)
            else:
                log.info("ignoring key {}".format(d))
    else:
        log.info("no dependencies")


def run(role_dir: str) -> None:
    install_all(deps.extract_dependencies(slurp.slurp_meta_requirements_yml(role_dir)))
    install_all(deps.extract_dependencies(slurp.slurp_test_requirements_yml(role_dir)))


def main():
    logging_setup.go()

    parser = argparse.ArgumentParser(
        description="uses ansible-galaxy to install all dependencies from test-requirements.yml and meta/requirements.yml"
    )
    parser.add_argument("roledirs", nargs="*", default=[os.getcwd()])
    args = parser.parse_args()
    for roledir in args.roledirs:
        run(roledir)

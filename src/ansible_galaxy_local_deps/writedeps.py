import argparse
import os

import ansible_galaxy_local_deps.deps as deps
import ansible_galaxy_local_deps.dump as dump
import ansible_galaxy_local_deps.logging_setup as loggingsetup
import ansible_galaxy_local_deps.slurp as slurp


def run(role_dir: str) -> None:
    mm = slurp.slurp_meta_main(role_dir)
    if "dependencies" in mm:
        dump.dump_requirements_yml(
            role_dir, deps.extract_dependencies(mm["dependencies"])
        )


def main() -> None:
    loggingsetup.go()

    parser = argparse.ArgumentParser(
        description="extracts dependencies from meta/main.yml and writes out meta/requirements.yml"
    )
    parser.add_argument("roledirs", nargs="*", default=[os.getcwd()])
    args = parser.parse_args()
    for roledir in args.roledirs:
        run(roledir)

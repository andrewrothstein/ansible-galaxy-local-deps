import os
from typing import Annotated

import cyclopts

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


app = cyclopts.App(
    name="ansible-galaxy-local-deps-write",
    help="extracts dependencies from meta/main.yml and writes out meta/requirements.yml"
)


@app.default
def main(
    *roledirs: Annotated[
        str,
        cyclopts.Parameter(
            help="Role directories to extract dependencies from. If not specified, uses current directory."
        )
    ]
) -> None:
    """Extract and write Ansible role dependencies."""
    loggingsetup.go()

    # Default to current directory if no directories specified
    dirs_to_process = list(roledirs) if roledirs else [os.getcwd()]

    for roledir in dirs_to_process:
        run(roledir)

import logging
import os

# B404: subprocess import is required for core functionality
# This tool's purpose is to wrap ansible-galaxy commands
from subprocess import check_call  # nosec B404
from typing import Annotated, Any

import cyclopts

import ansible_galaxy_local_deps.deps as deps
import ansible_galaxy_local_deps.logging_setup as logging_setup
import ansible_galaxy_local_deps.slurp as slurp


def install_role(r: str, v: str | None = None) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps.installdeps.install")
    log.info(f"installing {r} version {v}...")
    p = ",".join([r, v]) if v is not None else r
    # B603: subprocess call is safe - we're NOT using shell=True (which is good!)
    # B607: partial path is fine - ansible-galaxy should be in user's PATH
    # The command arguments come from parsed YAML files, not raw user input
    check_call(["ansible-galaxy", "install", "-f", p])  # nosec B603,B607


def install_all(y: list[dict[str, Any]] | None) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps.installdeps.install_all")
    if y is not None:
        for d in y:
            efk = deps.effkey(d)
            if efk is not None:
                install_role(d[efk], d.get("version", None))
            else:
                log.info(f"ignoring key {d}")
    else:
        log.info("no dependencies")


def run(role_dir: str) -> None:
    install_all(deps.extract_dependencies(slurp.slurp_meta_requirements_yml(role_dir)))
    install_all(deps.extract_dependencies(slurp.slurp_test_requirements_yml(role_dir)))


app = cyclopts.App(
    name="ansible-galaxy-local-deps-install",
    help="uses ansible-galaxy to install all dependencies from test-requirements.yml and meta/requirements.yml",
)


@app.default
def main(
    *roledirs: Annotated[
        str,
        cyclopts.Parameter(
            help="Role directories to install dependencies for. If not specified, uses current directory."
        ),
    ],
) -> None:
    """Install Ansible role dependencies using ansible-galaxy."""
    logging_setup.go()
    log = logging.getLogger("ansible-galaxy-local-deps.installdeps.main")

    # Default to current directory if no directories specified
    dirs_to_process = list(roledirs) if roledirs else [os.getcwd()]

    for roledir in dirs_to_process:
        # Validate role directory exists and is a directory
        if not os.path.exists(roledir):
            log.error(f"Role directory does not exist: {roledir}")
            raise cyclopts.ValidationError(f"Role directory does not exist: {roledir}")
        if not os.path.isdir(roledir):
            log.error(f"Path is not a directory: {roledir}")
            raise cyclopts.ValidationError(f"Path is not a directory: {roledir}")

        # Validate it's an absolute path or convert it
        roledir = os.path.abspath(roledir)

        try:
            run(roledir)
        except Exception as e:
            log.error(f"Failed to install dependencies for {roledir}: {e}")
            raise

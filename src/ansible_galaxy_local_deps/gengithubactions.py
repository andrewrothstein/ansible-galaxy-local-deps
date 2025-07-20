import logging
import os
from typing import Annotated, Any, Literal

import cyclopts

import ansible_galaxy_local_deps.dump as dump
import ansible_galaxy_local_deps.logging_setup as loggingsetup
import ansible_galaxy_local_deps.platform_matrix as platform_matrix
import ansible_galaxy_local_deps.slurp as slurp


def build_yml(ver: str = "v1") -> dict[str, Any]:
    return {
        "on": "push",
        "jobs": {
            "bake-ansible-images-v1": {
                "uses": "andrewrothstein/.github/.github/workflows/bake-ansible-images-{}.yml@develop".format(
                    ver
                )
            }
        },
    }


def render_meta_main(role_dir: str, pm: list[dict[str, Any]]) -> None:
    log = logging.getLogger(
        "ansible-galaxy-local-deps.gengithubactions.render_meta_main"
    )
    mm = slurp.slurp_meta_main_yml(role_dir)

    if mm is None:
        log.error("Could not find meta/main.yml in {}".format(role_dir))
        return

    if "galaxy_info" not in mm:
        log.error("No galaxy_info section found in meta/main.yml")
        return

    # flatten the license list
    if "license" in mm["galaxy_info"]:
        lic = mm["galaxy_info"]["license"]
        if isinstance(lic, list):
            mm["galaxy_info"]["license"] = lic[0]

    if "min_ansible_version" in mm["galaxy_info"]:
        min_ansible_version = mm["galaxy_info"]["min_ansible_version"]
        if isinstance(min_ansible_version, float):
            mm["galaxy_info"]["min_ansible_version"] = str(min_ansible_version)

    mm["galaxy_info"]["platforms"] = platform_matrix.render_platforms(pm)

    if "namespace" not in mm["galaxy_info"]:
        mm["galaxy_info"]["namespace"] = "andrewrothstein"

    if "role_name" not in mm["galaxy_info"]:
        log.info("computing role_name from role directory: {}".format(role_dir))
        d = os.path.basename(role_dir)
        if d.startswith("ansible-"):
            rn = d.removeprefix("ansible-")
            log.info("computed role_name: {}".format(rn))
            mm["galaxy_info"]["role_name"] = rn

    dump.dump_meta_main_yml(role_dir, mm)


def upgrade_platform_matrix(role_dir: str) -> None:
    log = logging.getLogger(
        "ansible-galaxy-local-deps.gengithubactions.upgrade_platform_matrix"
    )
    dcb_os = os.path.join(role_dir, "dcb-os.yml")
    pm = None
    if os.path.exists(dcb_os):
        dcb_data = slurp.slurp_dcb_os_yml(role_dir)
        if dcb_data is None:
            log.error("Could not read dcb-os.yml in {}".format(role_dir))
            return
        pm = platform_matrix.from_dcb_osl(dcb_data)
        try:
            os.remove(dcb_os)
        except PermissionError:
            log.error("Permission denied removing: {}".format(dcb_os))
            raise
        except OSError as e:
            log.error("Error removing {}: {}".format(dcb_os, e))
            raise
    else:
        pm_data = slurp.slurp_platform_matrix_json(role_dir)
        if pm_data is None:
            log.error("Could not find platform-matrix-v1.json in {}".format(role_dir))
            return
        pm = platform_matrix.upgrade(pm_data)
    dump.dump_platform_matrix_json(role_dir, pm)
    render_meta_main(role_dir, pm)


def mksubdirs(role_dir: str, subs: list[str]) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps.gengithubactions.mksubdirs")
    d = role_dir
    for s in subs:
        d = os.path.join(d, s)
        if not os.path.isdir(d):
            try:
                os.mkdir(d, 0o755)
            except PermissionError:
                log.error("Permission denied creating directory: {}".format(d))
                raise
            except OSError as e:
                log.error("Error creating directory {}: {}".format(d, e))
                raise


app = cyclopts.App(
    name="gengithubactions",
    help="generates a .github/workflows/build.yml for building/testing Ansible roles with docker buildx bake",
)


@app.default
def main(
    *roledirs: Annotated[
        str,
        cyclopts.Parameter(
            help="Role directories to generate GitHub Actions for. If not specified, uses current directory."
        ),
    ],
    ver: Annotated[
        Literal["v1", "v2"],
        cyclopts.Parameter(help="Version of the GitHub Actions workflow"),
    ] = "v1",
) -> None:
    """Generate GitHub Actions workflow for Ansible roles."""
    loggingsetup.go()
    log = logging.getLogger("ansible-galaxy-local-deps.gengithubactions.main")

    # Default to current directory if no directories specified
    dirs_to_process = list(roledirs) if roledirs else [os.getcwd()]

    for role_dir in dirs_to_process:
        # Validate role directory exists and is a directory
        if not os.path.exists(role_dir):
            log.error("Role directory does not exist: {}".format(role_dir))
            raise cyclopts.ValidationError(f"Role directory does not exist: {role_dir}")
        if not os.path.isdir(role_dir):
            log.error("Path is not a directory: {}".format(role_dir))
            raise cyclopts.ValidationError(f"Path is not a directory: {role_dir}")

        # Validate it's an absolute path or convert it
        role_dir = os.path.abspath(role_dir)

        try:
            mksubdirs(role_dir, [".github", "workflows"])
            upgrade_platform_matrix(role_dir)
            dump.dump_github_actions_build_yml(role_dir, build_yml(ver))
            dump.dump_gitignore(role_dir)
        except Exception as e:
            log.error(
                "Failed to generate GitHub Actions for {}: {}".format(role_dir, e)
            )
            raise

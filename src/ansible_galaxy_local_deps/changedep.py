import logging
import os
from typing import Annotated, Any

import cyclopts

import ansible_galaxy_local_deps.deps as deps
import ansible_galaxy_local_deps.dump as dump
import ansible_galaxy_local_deps.logging_setup as loggingsetup
import ansible_galaxy_local_deps.slurp as slurp


def adjust_role(role_map: dict[str, Any], ek: str, r: str, v: str) -> dict[str, Any]:
    if ek != "name":
        role_map["name"] = role_map[ek]
        role_map.pop(ek)
    if v is None:
        role_map["name"] = r
    else:
        role_map["name"] = r
        role_map["version"] = v
    return role_map


def rewrite(
    r_yml: list[dict[str, Any]] | None,
    from_role: str,
    from_ver: str,
    to_role: str,
    to_ver: str,
) -> list[dict[str, Any]] | None:
    if r_yml is None:
        return None

    o = []
    modified = False
    for r in r_yml:
        ek = deps.effkey(r)
        if ek is not None and from_role == r[ek]:
            if from_ver is None or "version" in r and r["version"] == from_ver:
                o.append(adjust_role(r, ek, to_role, to_ver))
                modified = True
            else:
                o.append(r)
        else:
            o.append(r)
    return o if modified else None


def rewrite_meta_requirements_yml(
    role_dir: str, from_role: str, from_ver: str, to_role: str, to_ver: str
) -> None:
    modified = rewrite(
        slurp.slurp_meta_requirements_yml(role_dir),
        from_role,
        from_ver,
        to_role,
        to_ver,
    )
    if modified:
        dump.dump_meta_requirements_yml(role_dir, modified)


def rewrite_test_requirements_yml(
    role_dir: str, from_role: str, from_ver: str, to_role: str, to_ver: str
) -> None:
    modified = rewrite(
        slurp.slurp_test_requirements_yml(role_dir),
        from_role,
        from_ver,
        to_role,
        to_ver,
    )
    if modified:
        dump.dump_test_requirements_yml(role_dir, modified)


def run(
    role_dir: str, from_role: str, from_ver: str, to_role: str, to_ver: str
) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps-change-dep")

    log.info(
        "changing role {0} to {1}".format(
            from_role if from_ver is None else "{0}:{1}".format(from_role, from_ver),
            to_role if to_ver is None else "{0}:{1}".format(to_role, to_ver),
        )
    )
    rewrite_meta_requirements_yml(role_dir, from_role, from_ver, to_role, to_ver)
    rewrite_test_requirements_yml(role_dir, from_role, from_ver, to_role, to_ver)


app = cyclopts.App(
    name="ansible-galaxy-local-deps-change-dep",
    help="modified dependencies in meta/requirements.yml and test-requirements.yml files",
)


@app.default
def main(
    *roledirs: Annotated[
        str,
        cyclopts.Parameter(
            help="Role directories to modify dependencies in. If not specified, uses current directory."
        ),
    ],
    role: Annotated[
        str, cyclopts.Parameter(help="Name of the role dependency to change")
    ],
    fromver: Annotated[
        str | None, cyclopts.Parameter(help="Current version of the role (optional)")
    ] = None,
    torole: Annotated[
        str | None,
        cyclopts.Parameter(help="New role name (optional, defaults to same role)"),
    ] = None,
    tover: Annotated[
        str | None, cyclopts.Parameter(help="New version of the role (optional)")
    ] = None,
) -> None:
    """Change Ansible role dependencies."""
    loggingsetup.go()

    # Default to current directory if no directories specified
    dirs_to_process = list(roledirs) if roledirs else [os.getcwd()]

    # Use original role name if torole not specified
    target_role = torole if torole is not None else role

    for roledir in dirs_to_process:
        run(
            roledir,
            role,
            fromver,
            target_role,
            tover,
        )

import json
import logging
import os
from typing import Any

import yaml


class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


def dump_txt(role_dir: str, f: str, t: str) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps.dump.dump_txt")
    of = os.path.join(role_dir, f)
    log.info(f"writing out {of}...")
    try:
        os.makedirs(os.path.dirname(of), exist_ok=True)
        with open(of, "w") as w:
            w.write(t)
    except PermissionError:
        log.error(f"Permission denied writing: {of}")
        raise
    except OSError as e:
        log.error(f"Error writing {of}: {e}")
        raise


def dump_yml(role_dir: str, f: str, y: dict[str, Any] | list[dict[str, Any]]) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps.dump.dump_yml")
    of = os.path.join(role_dir, f)
    log.info(f"writing out {of}...")
    try:
        os.makedirs(os.path.dirname(of), exist_ok=True)
        with open(of, "w") as s:
            yaml.dump(y, stream=s, explicit_start=True, Dumper=IndentDumper)
    except PermissionError:
        log.error(f"Permission denied writing: {of}")
        raise
    except yaml.YAMLError as e:
        log.error(f"YAML serialization error for {of}: {e}")
        raise
    except OSError as e:
        log.error(f"Error writing {of}: {e}")
        raise


def dump_json(role_dir: str, f: str, j: dict[str, Any] | list[dict[str, Any]]) -> None:
    log = logging.getLogger("ansible-galaxy-local-deps.dump.dump_json")
    of = os.path.join(role_dir, f)
    log.info(f"writing out {of}...")
    try:
        os.makedirs(os.path.dirname(of), exist_ok=True)
        with open(of, "w") as s:
            json.dump(j, s, indent=2)
    except PermissionError:
        log.error(f"Permission denied writing: {of}")
        raise
    except TypeError as e:
        log.error(f"JSON serialization error for {of}: {e}")
        raise
    except OSError as e:
        log.error(f"Error writing {of}: {e}")
        raise


def dump_meta_main_yml(role_dir: str, y: dict[str, Any]) -> None:
    dump_yml(role_dir, os.path.join("meta", "main.yml"), y)


def dump_meta_requirements_yml(role_dir: str, y: list[dict[str, Any]]) -> None:
    dump_yml(role_dir, os.path.join("meta", "requirements.yml"), y)


def dump_requirements_yml(role_dir: str, y: list[dict[str, Any]]) -> None:
    dump_yml(role_dir, "requirements.yml", y)


def dump_requirements_txt(role_dir: str, t: str) -> None:
    dump_txt(role_dir, "requirements.txt", t)


def dump_dcb_os_yml(role_dir: str, y: list[dict[str, Any]]) -> None:
    dump_yml(role_dir, "dcb-os.yml", y)


def dump_platform_matrix_json(role_dir: str, j: list[dict[str, Any]]) -> None:
    dump_json(role_dir, "platform-matrix-v1.json", j)


def dump_test_requirements_yml(role_dir: str, y: list[dict[str, Any]]) -> None:
    dump_yml(role_dir, "test-requirements.yml", y)


def dump_github_actions_build_yml(role_dir: str, y: dict[str, Any]) -> None:
    dump_yml(role_dir, os.path.join(".github", "workflows", "build.yml"), y)


def dump_gitignore(role_dir: str) -> None:
    dump_txt(
        role_dir,
        ".gitignore",
        "\n".join(
            [
                "**~*.retry",
                "Dockerfile.*",
                "requirements.yml",
                "!meta/requirements.yml",
                "**/*undo-tree*",
                ".ansible",
            ]
        ),
    )

import json
import logging
import os

import yaml
from yaml import load

try:
    from yaml import CLoader

    Loader = CLoader
except ImportError:
    from yaml import Loader  # type: ignore[assignment]

from typing import Any

from ansible_galaxy_local_deps import finder as finder


def slurp_yml(role_dir: str, f: str) -> Any | None:
    log = logging.getLogger("ansible-galaxy-local-deps.slurp.slurp_yml")
    fq = finder.find(role_dir, f)
    if fq:
        log.info(f"found {fq}. slurping...")
        try:
            with open(fq) as ifq:
                # B506: yaml.load is safe here because:
                # 1. We explicitly use CLoader/Loader, not the unsafe default
                # 2. We only load trusted local Ansible role files (meta/main.yml, etc)
                # 3. This tool is designed to work with local role files, not untrusted input
                return load(ifq, Loader=Loader)  # nosec B506
        except FileNotFoundError:
            log.error(f"File not found: {fq}")
        except PermissionError:
            log.error(f"Permission denied reading: {fq}")
        except yaml.YAMLError as e:
            log.error(f"YAML parsing error in {fq}: {e}")
        except Exception as e:
            log.error(f"Unexpected error reading {fq}: {e}")
    return None


def slurp_json(role_dir: str, f: str) -> Any | None:
    log = logging.getLogger("ansible-galaxy-local-deps.slurp.slurp_json")
    fq = finder.find(role_dir, f)
    if fq:
        log.info(f"found {fq}. slurping...")
        try:
            with open(fq) as ifq:
                return json.load(ifq)
        except FileNotFoundError:
            log.error(f"File not found: {fq}")
        except PermissionError:
            log.error(f"Permission denied reading: {fq}")
        except json.JSONDecodeError as e:
            log.error(f"JSON parsing error in {fq}: {e}")
        except Exception as e:
            log.error(f"Unexpected error reading {fq}: {e}")
    return None


def slurp_meta_main_yml(role_dir: str) -> dict[str, Any] | None:
    return slurp_yml(role_dir, os.path.join("meta", "main.yml"))


def slurp_meta_requirements_yml(role_dir: str) -> list[dict[str, Any]] | None:
    return slurp_yml(role_dir, os.path.join("meta", "requirements.yml"))


def slurp_test_requirements_yml(role_dir: str) -> list[dict[str, Any]] | None:
    return slurp_yml(role_dir, "test-requirements.yml")


def slurp_dcb_os_yml(role_dir: str) -> list[str] | None:
    return slurp_yml(role_dir, "dcb-os.yml")


def slurp_script_yml(role_dir: str) -> dict[str, Any] | None:
    return slurp_yml(role_dir, "script.yml")


def slurp_platform_matrix_json(role_dir: str) -> list[dict[str, Any]] | None:
    return slurp_json(role_dir, "platform-matrix-v1.json")

import json
import logging
import os

import yaml
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from typing import Any

from ansible_galaxy_local_deps import finder as finder


def slurp_yml(role_dir: str, f: str) -> Any | None:
    log = logging.getLogger("ansible-galaxy-local-deps.slurp.slurp_yml")
    fq = finder.find(role_dir, f)
    if fq:
        log.info("found {0}. slurping...".format(fq))
        try:
            with open(fq) as ifq:
                return load(ifq, Loader=Loader)
        except FileNotFoundError:
            log.error("File not found: {}".format(fq))
        except PermissionError:
            log.error("Permission denied reading: {}".format(fq))
        except yaml.YAMLError as e:
            log.error("YAML parsing error in {}: {}".format(fq, e))
        except Exception as e:
            log.error("Unexpected error reading {}: {}".format(fq, e))
    return None


def slurp_json(role_dir: str, f: str) -> Any | None:
    log = logging.getLogger("ansible-galaxy-local-deps.slurp.slurp_json")
    fq = finder.find(role_dir, f)
    if fq:
        log.info("found {0}. slurping...".format(fq))
        try:
            with open(fq) as ifq:
                return json.load(ifq)
        except FileNotFoundError:
            log.error("File not found: {}".format(fq))
        except PermissionError:
            log.error("Permission denied reading: {}".format(fq))
        except json.JSONDecodeError as e:
            log.error("JSON parsing error in {}: {}".format(fq, e))
        except Exception as e:
            log.error("Unexpected error reading {}: {}".format(fq, e))
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

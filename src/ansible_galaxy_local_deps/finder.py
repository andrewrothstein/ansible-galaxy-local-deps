import logging
import os


def find(role_dir: str, f: str) -> str | None:
    log = logging.getLogger("ansible-galaxy-local-deps.finder.find")
    fq = os.path.join(role_dir, f)
    log.info(f"looking for {fq}...")
    return fq if os.path.isfile(fq) else None


def find_meta_main(role_dir: str) -> str | None:
    return find(role_dir, os.path.join("meta", "main.yml"))


def find_dcb_os(role_dir: str) -> str | None:
    return find(role_dir, "dcb-os.yml")


def find_gha_buildyml(role_dir: str) -> str | None:
    return find(role_dir, os.path.join(".github", "workflows", "build.yml"))

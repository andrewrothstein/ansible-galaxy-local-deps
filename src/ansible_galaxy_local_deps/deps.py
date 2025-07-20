import logging
from typing import Any


def effkey(d) -> str | None:
    if "name" in d:
        return "name"
    elif "role" in d:
        return "role"
    elif "src" in d:
        return "src"
    else:
        return None


def extract_dependencies(requirements_yml: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """extract dependencies from a requirements.yml yaml data"""
    log = logging.getLogger("ansible-galaxy-local-deps.deps.extract_dependencies")
    o = []
    for r in requirements_yml:
        key = effkey(r)
        if key:
            r["name"] = r[key]
            if key != "name":
                r.pop(key)
            o.append(r)
        else:
            log.warning("ignoring dependency: {0}".format(r))
    return o

# Platform Matrix Configuration

The platform matrix module now supports loading defaults from an external JSON file, allowing centralized management of platform configurations across multiple Ansible roles.

## External Configuration File

The module searches for `default-platform-matrix-v1.json` in the following locations (in order):
1. Package resources (bundled with the installed package)
2. Current working directory (for user overrides)
3. User's home directory (~/) (for user overrides)

## File Format

The JSON file should contain an array of platform entries:

```json
[
  {
    "OS": "alpine",
    "OS_VER": "3.21",
    "PLATFORMS": "linux/amd64"
  },
  {
    "OS": "ubi",
    "OS_VER": "9",
    "UPSTREAM_ORG": "redhat",
    "UPSTREAM_OS": "ubi9",
    "UPSTREAM_OS_VER": "latest",
    "PLATFORMS": "linux/amd64,linux/arm64"
  }
]
```

## Supported Fields

- **OS**: Operating system name (required)
- **OS_VER**: Operating system version (required)
- **PLATFORMS**: Comma-separated list of supported platforms (e.g., "linux/amd64,linux/arm64")
- **UPSTREAM_***: Any fields starting with "UPSTREAM_" are preserved and applied to platform entries

## Upgrade Behavior

When upgrading platform matrices:
1. Special versions (edge, latest, rolling, rawhide) are never upgraded
2. Regular versions are sorted, and the latest 2 versions are kept
3. Older versions are upgraded to the latest 2 versions
4. All extra fields (PLATFORMS, UPSTREAM_*, etc.) are preserved during upgrades

## Fallback Behavior

If no external configuration file is found, the module falls back to built-in defaults that maintain backward compatibility with existing behavior.

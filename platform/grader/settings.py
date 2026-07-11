"""Persisted tutor settings — the backing store for the in-app admin surface.

Saved as JSON next to .progress.json (the container symlinks it onto the
/app/state volume, so these settings survive a power-down exactly like your
progress). Holds whether the tutor is on, which provider/model, and the API key.

Trust model: this is a single-user, local, self-hosted study container. The key
is stored in plaintext in a gitignored, chmod-600 file on the user's own volume —
the same posture as a local dotfile (~/.aws/credentials, ~/.netrc). It is never
committed and never leaves the machine except in the API calls the user opts
into. The LDE_TUTOR_KEY / LDE_TUTOR_MODEL env vars still work and act as
defaults when nothing is saved (handy for headless/CI runs).
"""

from __future__ import annotations

import json
from pathlib import Path

SETTINGS_FILENAME = ".tutor.json"


def _path(repo_root: Path) -> Path:
    return repo_root / SETTINGS_FILENAME


def load(repo_root: Path) -> dict:
    """Return saved settings, or {} if none/corrupt. Never raises."""
    path = _path(repo_root)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text() or "{}")
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save(repo_root: Path, data: dict) -> dict:
    """Write settings (full replace) and lock the file to the owner (0600)."""
    path = _path(repo_root)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    try:
        path.chmod(0o600)  # a key lives here — keep it owner-only
    except OSError:  # pragma: no cover - filesystem-dependent
        pass
    return data

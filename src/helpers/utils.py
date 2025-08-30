"""Utility helpers for the API."""

from __future__ import annotations

from typing import Any, Tuple
from flask import jsonify


def json_error(message: str, status: int = 400) -> Tuple[Any, int]:
    """Return a JSON error response with the given status code."""
    return jsonify({"error": message}), status


def bump_version(version: str, bump: str) -> str:
    """Bump a semantic version string.

    Parameters
    ----------
    version:
        Current version string in the form ``"major.minor"``.
    bump:
        Either ``"major"`` or ``"minor"`` indicating which part to bump.

    Returns
    -------
    str
        The bumped version string.
    """

    major, minor = map(int, version.split("."))
    if bump == "major":
        return f"{major + 1}.0"
    return f"{major}.{minor + 1}"

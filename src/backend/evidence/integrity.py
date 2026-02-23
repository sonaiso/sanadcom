"""
Evidence Integrity Utilities
Provides SHA-256 tamper protection for uploaded evidence files.
"""

import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional


HASH_ALGORITHM = "SHA-256"


def compute_file_hash(file_path: str) -> str:
    """
    Compute SHA-256 hex digest of a file.

    Args:
        file_path: Absolute path to the file.

    Returns:
        64-character lowercase hex string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_bytes_hash(data: bytes) -> str:
    """
    Compute SHA-256 hex digest of raw bytes (e.g. from an upload stream).

    Args:
        data: Raw file bytes.

    Returns:
        64-character lowercase hex string.
    """
    return hashlib.sha256(data).hexdigest()


def verify_file_hash(file_path: str, expected_hash: str) -> bool:
    """
    Verify that a file's current SHA-256 digest matches the stored hash.

    Args:
        file_path: Absolute path to the file.
        expected_hash: Previously computed hex digest to compare against.

    Returns:
        True if the file is intact, False if tampered / missing.
    """
    try:
        current_hash = compute_file_hash(file_path)
        return current_hash.lower() == expected_hash.lower()
    except FileNotFoundError:
        return False

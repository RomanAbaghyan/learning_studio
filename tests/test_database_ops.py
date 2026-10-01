"""Exercise WAL snapshots and validate restores without touching learner accounts."""
import io
import sqlite3

import pytest

from tools.database import backup, restore, validate


def academy_database(path):
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=WAL")
    for table in ("users", "sessions", "state", "password_resets"):
        connection.execute(f"CREATE TABLE {table} (value TEXT)")
    connection.execute("INSERT INTO users VALUES ('saved learner')")
    connection.commit()
    return connection


def test_snapshot_includes_committed_wal_and_restores(tmp_path):
    source_path = tmp_path / "source.db"
    with academy_database(source_path) as source:
        snapshot = io.BytesIO()
        backup(source_path, snapshot)
        source.execute("DELETE FROM users")
        source.commit()
        restored_path = tmp_path / "restored.db"
        restore(restored_path, io.BytesIO(snapshot.getvalue()))
        validate(restored_path)
        with sqlite3.connect(restored_path) as restored:
            assert restored.execute("SELECT value FROM users").fetchall() == [("saved learner",)]


def test_invalid_restore_preserves_original_database(tmp_path):
    destination = tmp_path / "original.db"
    database = academy_database(destination)
    database.close()
    original = destination.read_bytes()
    with pytest.raises(sqlite3.DatabaseError):
        restore(destination, io.BytesIO(b"not a database"))
    assert destination.read_bytes() == original
    assert not list(tmp_path.glob("restore-*"))


def test_rejects_unrelated_sqlite_database(tmp_path):
    path = tmp_path / "unrelated.db"
    with sqlite3.connect(path) as database:
        database.execute("CREATE TABLE unrelated (value TEXT)")
    with pytest.raises(ValueError, match="required tables"):
        validate(path)

"""Validate a gzip SQLite backup before replacing the stopped app's database."""
from contextlib import closing
import gzip
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile


def restore(source, destination):
    destination = Path(destination)
    fd, name = tempfile.mkstemp(prefix=".restore-", suffix=".db", dir=destination.parent)
    staged = Path(name)
    try:
        with os.fdopen(fd, "wb") as output, gzip.GzipFile(fileobj=source) as archive:
            shutil.copyfileobj(archive, output)
            output.flush()
            os.fsync(output.fileno())
        with closing(sqlite3.connect(staged)) as conn:
            if conn.execute("PRAGMA integrity_check").fetchone() != ("ok",):
                raise ValueError("backup failed SQLite integrity check")
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {"users", "sessions", "state"} <= tables:
                raise ValueError("backup is not an Academy database")
        # The app must be stopped. Checkpoint the OLD DB before touching its
        # sidecars, so a failed replacement still leaves a complete old copy.
        if destination.exists():
            with closing(sqlite3.connect(destination)) as conn:
                if conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()[0]:
                    raise RuntimeError("database is busy; stop the app before restoring")
        for suffix in ("-wal", "-shm"):
            Path(str(destination) + suffix).unlink(missing_ok=True)
        os.replace(staged, destination)
        directory = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        staged.unlink(missing_ok=True)


if __name__ == "__main__":
    restore(sys.stdin.buffer, os.environ.get("ACADEMY_DB", "/data/academy.db"))

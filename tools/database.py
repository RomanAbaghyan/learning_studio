"""SQLite snapshots and offline restore. Backup bytes use stdout; diagnostics use stderr."""
import argparse
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile


def validate(path):
    with sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("SQLite integrity check failed")
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"users", "sessions", "state", "password_resets"} <= tables:
            raise ValueError("Not an Academy database: required tables are missing")


def backup(database, output):
    # SQLite's backup API includes committed WAL data without stopping the app.
    with tempfile.TemporaryDirectory() as directory:
        snapshot = Path(directory) / "snapshot.db"
        with sqlite3.connect(Path(database).resolve().as_uri() + "?mode=ro", uri=True) as source:
            with sqlite3.connect(snapshot) as target:
                source.backup(target)
        validate(snapshot)
        with snapshot.open("rb") as stream:
            shutil.copyfileobj(stream, output)


def restore(database, source):
    # Caller MUST stop all app processes sharing this database before restoring.
    destination = Path(database)
    fd, temporary = tempfile.mkstemp(prefix="restore-", suffix=".db", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            shutil.copyfileobj(source, stream)
            stream.flush()
            os.fsync(stream.fileno())
        validate(temporary)
        for suffix in ("-wal", "-shm"):
            Path(str(destination) + suffix).unlink(missing_ok=True)
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("backup", "restore", "validate"))
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()
    database = os.environ.get("ACADEMY_DB", "/data/academy.db")
    try:
        if args.action == "backup":
            backup(database, sys.stdout.buffer)
        elif args.action == "restore":
            restore(database, sys.stdin.buffer)
            print("Database restored", file=sys.stderr)
        elif args.file:
            validate(args.file)
            print("Valid Academy database", file=sys.stderr)
        else:
            parser.error("validate requires a backup file")
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Database operation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

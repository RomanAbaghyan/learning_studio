import gzip
import io
import sqlite3

import pytest

from deploy.restore import restore


def database(path, value):
    with sqlite3.connect(path) as conn:
        conn.executescript('CREATE TABLE users (name TEXT); CREATE TABLE sessions (id INTEGER); CREATE TABLE state (id INTEGER);')
        conn.execute('INSERT INTO users VALUES (?)', (value,))
    return path.read_bytes()


def test_restore_valid_database(tmp_path):
    destination = tmp_path / 'live.db'
    database(destination, 'old')
    data = database(tmp_path / 'backup.db', 'new')
    restore(io.BytesIO(gzip.compress(data)), destination)
    with sqlite3.connect(destination) as conn:
        assert conn.execute('SELECT name FROM users').fetchone() == ('new',)


@pytest.mark.parametrize('data', [b'not gzip', gzip.compress(b'not a database'), gzip.compress(b'')])
def test_invalid_restore_preserves_database(tmp_path, data):
    destination = tmp_path / 'live.db'
    original = database(destination, 'old')
    with pytest.raises((ValueError, OSError, sqlite3.DatabaseError, EOFError)):
        restore(io.BytesIO(data), destination)
    assert destination.read_bytes() == original
    assert not list(tmp_path.glob('.restore-*'))

import queue
from unittest.mock import Mock

import pytest

from runner import cpp_runner as runner


def test_failed_temp_allocation_returns_slot(monkeypatch):
    slots = queue.Queue()
    slots.put(0)
    monkeypatch.setattr(runner, '_slots', slots)
    monkeypatch.setattr(runner.tempfile, 'mkdtemp', Mock(side_effect=OSError('disk full')))
    with pytest.raises(OSError):
        runner.run_sandboxed('int main() {}')
    assert slots.get_nowait() == 0


def test_failed_cleanup_quarantines_slot(monkeypatch, tmp_path):
    slots = queue.Queue()
    slots.put(0)
    (tmp_path / '.io').mkdir()
    monkeypatch.setattr(runner, '_slots', slots)
    monkeypatch.setattr(runner, 'WORK', str(tmp_path))
    monkeypatch.setattr(runner, '_compile_and_run', Mock(return_value={}))
    monkeypatch.setattr(runner, '_cleanup_as', Mock(side_effect=RuntimeError('cleanup failed')))
    with pytest.raises(RuntimeError):
        runner.run_sandboxed('int main() {}')
    assert slots.empty()

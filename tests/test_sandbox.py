import pytest

from sudo_x.sandbox import Sandbox, SandboxInput


def test_sandbox_rejects_unsafe_paths(tmp_path):
    sandbox = Sandbox(tmp_path)
    with pytest.raises(ValueError):
        sandbox.run(SandboxInput(files={"../escape.py": "x"}))
    with pytest.raises(ValueError):
        sandbox.run(SandboxInput(files={".env": "secret"}))


def test_sandbox_requires_bwrap_and_preserves_original(tmp_path, monkeypatch):
    source = tmp_path / "project"
    source.mkdir()
    original = source / "sample.py"
    original.write_text("answer = 1\n")
    monkeypatch.setattr("sudo_x.sandbox.shutil.which", lambda _: None)
    with pytest.raises(ValueError, match="unavailable"):
        Sandbox(source).run(SandboxInput(files={"sample.py": "answer = 2\n"}))
    assert original.read_text() == "answer = 1\n"

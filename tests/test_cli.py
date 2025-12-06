from pathlib import Path

from lazy_log import cli
from lazy_log.cli import process_file


def test_process_file_missing_file_returns_one(tmp_path):
    assert process_file(tmp_path / "missing_file.py", fix=False) == 1


def test_process_file_skips_when_logging_not_imported(tmp_path):
    target = tmp_path / "script.py"
    target.write_text('name = "tester"\nlogger.info(f"{name}")', encoding="utf-8")

    result = process_file(target, fix=True, check_import=True)

    assert result == 0
    assert 'logger.info(f"{name}")' in target.read_text(encoding="utf-8")


def test_process_file_fix_applies_and_writes(tmp_path):
    target = tmp_path / "script.py"
    target.write_text(
        'import logging\nname = "tester"\nlogging.info(f"Hello {name}")',
        encoding="utf-8",
    )

    result = process_file(target, fix=True, check_import=True)

    updated = target.read_text(encoding="utf-8")
    assert result == 1
    assert 'logging.info("Hello %s", name)' in updated


def test_process_file_without_fix_reports_and_leaves_file(tmp_path, capsys):
    target = tmp_path / "script.py"
    target.write_text(
        'import logging\nname = "tester"\nlogging.info(f"Hello {name}")',
        encoding="utf-8",
    )

    result = process_file(target, fix=False, check_import=True)

    output, _ = capsys.readouterr()
    content = target.read_text(encoding="utf-8")
    assert result == 1
    assert "F-strings found in" in output
    assert "script.py" in output
    assert 'logging.info(f"Hello {name}")' in content


def test_process_file_without_issues_returns_zero(tmp_path):
    target = tmp_path / "clean.py"
    target.write_text(
        'import logging\nname = "tester"\nlogging.info("Hello %s", name)',
        encoding="utf-8",
    )

    result = process_file(target, fix=False, check_import=True)

    assert result == 0
    assert 'logging.info("Hello %s", name)' in target.read_text(encoding="utf-8")


def test_main_processes_file_and_prints_success(monkeypatch, tmp_path):
    target = tmp_path / "script.py"
    target.write_text("print('hi')", encoding="utf-8")
    calls: list[tuple[Path, bool]] = []

    def fake_process(file_path, fix, check_import=False):
        calls.append((Path(file_path), fix))
        return 0

    messages: list[str] = []
    monkeypatch.setattr(cli, "process_file", fake_process)
    monkeypatch.setattr(cli, "print_with_fallback", lambda msg: messages.append(msg))

    exit_code = cli.main([str(target)])

    assert exit_code == 0
    assert calls == [(target.resolve(), False)]
    assert messages and "Scanned 1 files" in messages[0]


def test_main_passes_fix_flag(monkeypatch, tmp_path):
    target = tmp_path / "fixme.py"
    target.write_text("print('hi')", encoding="utf-8")
    seen: dict[str, bool] = {}

    def fake_process(file_path, fix, check_import=False):
        seen["fix"] = fix
        return 0

    monkeypatch.setattr(cli, "process_file", fake_process)
    monkeypatch.setattr(cli, "print_with_fallback", lambda msg: None)

    exit_code = cli.main([str(target), "--fix"])

    assert exit_code == 0
    assert seen["fix"] is True


def test_main_excludes_paths(monkeypatch, tmp_path):
    keep = tmp_path / "keep.py"
    skip = tmp_path / "skip.py"
    keep.write_text("print('keep')", encoding="utf-8")
    skip.write_text("print('skip')", encoding="utf-8")
    called: list[str] = []

    def fake_process(file_path, fix, check_import=False):
        called.append(Path(file_path).name)
        return 0

    monkeypatch.setattr(cli, "process_file", fake_process)
    monkeypatch.setattr(cli, "print_with_fallback", lambda msg: None)

    exit_code = cli.main([str(tmp_path), "--exclude", "skip.py"])

    assert exit_code == 0
    assert called == ["keep.py"]


def test_main_skips_virtualenv_files(monkeypatch, tmp_path):
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "ignored.py").write_text("print('ignore')", encoding="utf-8")
    included = tmp_path / "run.py"
    included.write_text("print('run')", encoding="utf-8")
    processed: list[str] = []

    def fake_process(file_path, fix, check_import=False):
        processed.append(Path(file_path).name)
        return 0

    monkeypatch.setattr(cli, "process_file", fake_process)
    monkeypatch.setattr(cli, "print_with_fallback", lambda msg: None)

    exit_code = cli.main([str(tmp_path)])

    assert exit_code == 0
    assert processed == ["run.py"]


def test_main_warns_on_invalid_path(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "process_file",
        lambda *args, **kwargs: iter(()).throw(
            AssertionError("process_file should not be called")
        ),
    )

    exit_code = cli.main(["does_not_exist.py"])

    output, error = capsys.readouterr()
    assert exit_code == 0
    assert "not a valid file or directory" in error
    assert output == ""


def test_main_returns_one_when_issues_found(monkeypatch, tmp_path):
    target = tmp_path / "script.py"
    target.write_text("print('hi')", encoding="utf-8")
    monkeypatch.setattr(cli, "process_file", lambda *args, **kwargs: 1, raising=False)
    messages: list[str] = []
    monkeypatch.setattr(cli, "print_with_fallback", lambda msg: messages.append(msg))

    exit_code = cli.main([str(target)])

    assert exit_code == 1
    assert not messages

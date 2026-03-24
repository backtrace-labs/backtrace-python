from backtracepython.source_code_handler import SourceCodeHandler


def make_report(source_paths):
    """Build a minimal report whose main thread stack references the given file paths."""
    stack = [
        {"sourceCode": path, "line": 10, "funcName": "test"} for path in source_paths
    ]
    return {
        "mainThread": "main",
        "threads": {
            "main": {"stack": stack},
        },
    }


def test_collect_removes_unreadable_sources_without_runtime_error():
    """Reproduces RuntimeError: dictionary changed size during iteration.

    When every source file in the stack is unreadable, collect() used to pop
    entries from the source_code dict while iterating over it.
    """
    handler = SourceCodeHandler(tab_width=4, context_line_count=3)
    report = make_report(
        [
            "/nonexistent/path/a.py",
            "/nonexistent/path/b.py",
        ]
    )

    # Before the fix this raised:
    #   RuntimeError: dictionary changed size during iteration
    result = handler.collect(report)

    assert result["sourceCode"] == {}


def test_collect_keeps_readable_sources(tmp_path):
    """Verify that readable source files are collected normally."""
    source_file = tmp_path / "real.py"
    source_file.write_text("foobarbaz")

    handler = SourceCodeHandler(tab_width=4, context_line_count=1)
    report = make_report([str(source_file)])

    result = handler.collect(report)

    assert str(source_file) in result["sourceCode"]
    assert "text" in result["sourceCode"][str(source_file)]


def test_collect_mixed_readable_and_unreadable(tmp_path):
    """Mix of existing and missing files — only readable ones should survive."""
    source_file = tmp_path / "exists.py"
    source_file.write_text("foobarbaz")

    handler = SourceCodeHandler(tab_width=4, context_line_count=3)
    report = make_report(
        [
            "/nonexistent/path/missing.py",
            str(source_file),
            "/another/missing/file.py",
        ]
    )

    result = handler.collect(report)

    assert str(source_file) in result["sourceCode"]
    assert "/nonexistent/path/missing.py" not in result["sourceCode"]
    assert "/another/missing/file.py" not in result["sourceCode"]

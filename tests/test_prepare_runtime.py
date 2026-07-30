from types import SimpleNamespace

import pytest

import scripts.prepare_runtime as prepare_runtime


def test_blocking_maintenance_errors_stop_before_runtime_artifacts(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        prepare_runtime,
        "parse_args",
        lambda: SimpleNamespace(rebuild_vector_store=False, skip_vector_store=False),
    )
    monkeypatch.setattr(
        prepare_runtime.validate_rag_corpus,
        "validate",
        lambda **kwargs: [],
    )
    monkeypatch.setattr(
        prepare_runtime,
        "generate_maintenance_reports",
        lambda: {
            "counts": {"chunks": 12},
            "has_errors": True,
            "requires_attention": True,
            "severity_counts": {"error": 2, "warning": 3, "info": 0},
        },
    )
    monkeypatch.setattr(
        prepare_runtime,
        "rebuild_sqlite_metadata",
        lambda: pytest.fail("SQLite must not be rebuilt after a blocking finding"),
    )
    monkeypatch.setattr(
        prepare_runtime,
        "ensure_vector_store",
        lambda **kwargs: pytest.fail(
            "Chroma must not be rebuilt after a blocking finding"
        ),
    )
    monkeypatch.setattr(
        prepare_runtime,
        "run_health_checks",
        lambda **kwargs: pytest.fail(
            "Health checks must not run after a blocking finding"
        ),
    )

    with pytest.raises(SystemExit) as exc_info:
        prepare_runtime.main()

    assert exc_info.value.code == 1
    assert "maintenance found 2 blocking error(s)" in capsys.readouterr().out


def test_attention_warnings_do_not_block_runtime_artifacts(monkeypatch, capsys) -> None:
    calls = []
    monkeypatch.setattr(
        prepare_runtime,
        "parse_args",
        lambda: SimpleNamespace(rebuild_vector_store=False, skip_vector_store=True),
    )
    monkeypatch.setattr(
        prepare_runtime.validate_rag_corpus,
        "validate",
        lambda **kwargs: [],
    )
    monkeypatch.setattr(
        prepare_runtime,
        "generate_maintenance_reports",
        lambda: {
            "counts": {"chunks": 12},
            "has_errors": False,
            "requires_attention": True,
            "severity_counts": {"error": 0, "warning": 3, "info": 0},
        },
    )
    monkeypatch.setattr(
        prepare_runtime,
        "rebuild_sqlite_metadata",
        lambda: calls.append("sqlite") or {"chunks": 12},
    )
    monkeypatch.setattr(
        prepare_runtime,
        "run_health_checks",
        lambda **kwargs: calls.append(("health", kwargs))
        or SimpleNamespace(ok=True),
    )
    monkeypatch.setattr(
        prepare_runtime,
        "format_health_report",
        lambda health: "Health: OK",
    )

    prepare_runtime.main()

    assert calls == ["sqlite", ("health", {"require_vector_store": False})]
    assert "SQLite metadata ready with 12 chunks." in capsys.readouterr().out

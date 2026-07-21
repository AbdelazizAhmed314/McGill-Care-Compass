from pathlib import Path

import pandas as pd

import scripts.data.validate_rag_corpus as validator


def test_validate_local_artifacts_are_optional_by_default(monkeypatch, tmp_path: Path) -> None:
    missing_sqlite = tmp_path / "missing.sqlite"
    missing_vector = tmp_path / "missing_chroma"

    monkeypatch.setattr(validator, "SQLITE_DB", missing_sqlite)
    monkeypatch.setattr(validator, "VECTOR_DIR", missing_vector)
    monkeypatch.setattr(validator, "read_csv", lambda path, errors: pd.DataFrame())
    monkeypatch.setattr(validator, "read_manifest", lambda errors: {})

    default_errors = validator.validate(require_local_artifacts=False)
    strict_errors = validator.validate(require_local_artifacts=True)

    assert not any("rag_metadata.sqlite" in error for error in default_errors)
    assert any("missing.sqlite" in error for error in strict_errors)


def test_runtime_artifact_warnings_report_ignored_missing_artifacts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(validator, "SQLITE_DB", tmp_path / "missing.sqlite")
    monkeypatch.setattr(validator, "VECTOR_DIR", tmp_path / "missing_chroma")
    monkeypatch.setattr(validator, "ROOT", tmp_path)

    warnings = validator.collect_runtime_artifact_warnings(
        include_debug_files=False,
        pages=pd.DataFrame(),
    )

    assert len(warnings) == 2
    assert all("rebuildable ignored artifact" in warning for warning in warnings)

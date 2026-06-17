"""Data-loading helpers for curated service records."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from mcgill_care_compass.schema import ServiceRecord


def load_service_records(path: str | Path) -> list[ServiceRecord]:
    """Load service records from a CSV file."""

    frame = pd.read_csv(path).fillna("")
    return [ServiceRecord.model_validate(row) for row in frame.to_dict(orient="records")]

from pathlib import Path

import pandas as pd

from mcgill_care_compass.data_loading import load_service_records

DATASET = Path("data/datasets/curated_service_records.csv")


def test_curated_service_records_meet_june_21_counts() -> None:
    records = pd.read_csv(DATASET).fillna("")

    assert len(records) >= 40
    assert records["category_id"].nunique() >= 8
    assert (records["source_publisher"] == "McGill University").sum() >= 20
    assert records["category_id"].isin({"health_care", "mental_health"}).sum() >= 10
    assert records["record_id"].is_unique


def test_curated_service_records_load_with_app_schema() -> None:
    records = load_service_records(DATASET)

    assert len(records) >= 40
    assert all(record.official_source_url for record in records)
    assert all(record.last_verified_date for record in records)

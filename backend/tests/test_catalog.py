from app.infrastructure.database.catalog import ACHIEVEMENTS, CATALOG, validate_catalog


def test_catalog_is_consistent():
    validate_catalog()
    assert [item["slug"] for item in CATALOG] == [
        "phishing-investigation",
        "security-log-analysis",
        "anomaly-detection",
    ]
    assert len(ACHIEVEMENTS) == 8

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """
    Registration of custom markers.

    unit: Marker for testing pure functions, entities and VOs.
    integration: Testing the orchestrator (Use Case)
    in conjunction with in-memory repositories.
    """

    config.addinivalue_line(
        name="markers",
        line="unit: Pure tests of domain and utilities.",
    )
    config.addinivalue_line(
        name="markers",
        line="integration: Use case integration with fake ports.",
    )

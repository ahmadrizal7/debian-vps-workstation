from configurator.core.reporter.facts import FactsDatabase


def test_get_random_fact_category():
    fact = FactsDatabase.get_random_fact("docker")
    assert isinstance(fact, str)
    assert len(fact) > 0


def test_get_random_fact_unknown_category():
    # Should fall back to random from all
    fact = FactsDatabase.get_random_fact("nonexistent")
    assert isinstance(fact, str)


def test_get_all_categories():
    categories = FactsDatabase.get_all_categories()
    assert "docker" in categories
    assert "python" in categories

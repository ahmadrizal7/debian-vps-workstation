from configurator.ui.components import ActivityLog, ModuleCard, OverallProgress, ResourceGauge


def test_module_card_instantiation():
    card = ModuleCard()
    assert card is not None
    # Reactive properties check
    assert card.status == "pending"


def test_resource_gauge_instantiation():
    gauge = ResourceGauge()
    assert gauge is not None


def test_activity_log_instantiation():
    log = ActivityLog()
    assert log is not None


def test_overall_progress_instantiation():
    prog = OverallProgress()
    assert prog is not None

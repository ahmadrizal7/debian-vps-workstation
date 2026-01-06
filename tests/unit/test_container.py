import pytest

from configurator.core.container import CircularDependencyError, Container, ServiceNotFoundError


class MockService:
    def __init__(self, value="test"):
        self.value = value


class DependentService:
    def __init__(self, dependency):
        self.dependency = dependency


class CircularA:
    def __init__(self, b):
        self.b = b


class CircularB:
    def __init__(self, a):
        self.a = a


def test_singleton_registration():
    container = Container()
    container.singleton("service", lambda: MockService())

    instance1 = container.get("service")
    instance2 = container.get("service")

    assert isinstance(instance1, MockService)
    assert instance1 is instance2


def test_factory_registration():
    container = Container()
    container.factory("service", lambda: MockService())

    instance1 = container.get("service")
    instance2 = container.get("service")

    assert isinstance(instance1, MockService)
    assert instance1 is not instance2


def test_dependency_resolution():
    container = Container()
    container.singleton("dep", lambda: MockService("dep"))
    container.singleton("main", lambda c: DependentService(c.get("dep")))

    main = container.get("main")
    assert isinstance(main, DependentService)
    assert isinstance(main.dependency, MockService)
    assert main.dependency.value == "dep"


def test_service_not_found():
    container = Container()
    with pytest.raises(ServiceNotFoundError):
        container.get("nonexistent")


def test_circular_dependency():
    container = Container()
    # Note: Lambda usually captures closure, so this simple setup might not trigger logic
    # if we don't pass 'c' correctly or if we don't access it immediately.
    # But get() calls the factory which calls get().

    container.singleton("a", lambda c: c.get("b"))
    container.singleton("b", lambda c: c.get("a"))

    with pytest.raises(CircularDependencyError):
        container.get("a")


def test_factory_with_kwargs():
    container = Container()
    # Factory must accept container as first argument if it takes main args
    container.factory("service", lambda c, config: MockService(value=config["value"]))

    instance = container.make("service", config={"value": "dynamic"})
    assert instance.value == "dynamic"


def test_mocking():
    container = Container()
    mock_instance = MockService("mocked")

    container.mock("service", mock_instance)

    assert container.get("service") is mock_instance
    assert container.get("service").value == "mocked"

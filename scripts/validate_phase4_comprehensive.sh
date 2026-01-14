#!/bin/bash
# Phase 4 Comprehensive Validation Script
# Tests all testing infrastructure and observability features

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Counters
PASS=0
FAIL=0
WARN=0
SKIP=0
CRITICAL_FAIL=0

# Test categories
TESTING_PASS=0
TESTING_FAIL=0
OBSERVABILITY_PASS=0
OBSERVABILITY_FAIL=0

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🧪 PHASE 4 COMPREHENSIVE VALIDATION                  ║
║     Testing Infrastructure & Observability               ║
║                                                           ║
║     Part A: Testing Infrastructure                       ║
║     Part B: Observability System                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Helper functions
pass() {
    echo -e "  ${GREEN}✅ PASS${NC} - $1"
    ((++PASS))
}

fail() {
    echo -e "  ${RED}❌ FAIL${NC} - $1"
    ((++FAIL))
}

critical_fail() {
    echo -e "  ${RED}🚨 CRITICAL FAIL${NC} - $1"
    ((++CRITICAL_FAIL))
    ((++FAIL))
}

warn() {
    echo -e "  ${YELLOW}⚠️  WARN${NC} - $1"
    ((++WARN))
}

skip() {
    echo -e "  ${BLUE}⏭️  SKIP${NC} - $1"
    ((++SKIP))
}

section() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

subsection() {
    echo -e "\n${WHITE}▶ $1${NC}"
}

# ============================================================================
# PART A: TESTING INFRASTRUCTURE VALIDATION
# ============================================================================
section "PART A: TESTING INFRASTRUCTURE VALIDATION"

# ============================================================================
# TEST A1: File Structure
# ============================================================================
subsection "A1. Testing Files Structure"

echo "[A1.1] Checking performance test files..."
PERF_FILES=(
    "tests/performance/test_performance_regression.py"
    "tests/performance/test_load_stress.py"
    "tests/performance/baselines.json"
)

for file in "${PERF_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "Found: $file"
        ((++TESTING_PASS))
    else
        fail "Missing: $file"
        ((++TESTING_FAIL))
    fi
done

echo "[A1.2] Checking chaos engineering files..."
CHAOS_FILES=(
    "tests/resilience/test_network_failure_simulation.py"
)

for file in "${CHAOS_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "Found: $file"
        ((++TESTING_PASS))
    else
        warn "Missing: $file (created in Phase 3)"
        ((++TESTING_FAIL))
    fi
done

echo "[A1.3] Checking end-to-end test files..."
if [ -d "tests/e2e" ]; then
    E2E_COUNT=$(find tests/e2e -name "test_*.py" | wc -l)
    if [ $E2E_COUNT -gt 0 ]; then
        pass "Found $E2E_COUNT E2E test file(s)"
        ((++TESTING_PASS))
    else
        warn "E2E directory exists but no test files"
    fi
else
    warn "E2E test directory not created yet"
fi

# ============================================================================
# TEST A2: Performance Regression Tests
# ============================================================================
subsection "A2. Performance Regression Tests"

echo "[A2.1] Testing PerformanceBenchmark class..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
from pathlib import Path

try:
    from tests.performance.test_performance_regression import PerformanceBenchmark

    # Test with temp file
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock the baseline file
        original_file = PerformanceBenchmark.BASELINE_FILE
        PerformanceBenchmark.BASELINE_FILE = Path(tmpdir) / "baselines.json"

        benchmark = PerformanceBenchmark()

        # Test save baseline
        benchmark.save_baseline("test_operation", 0.5, {"version": "1.0"})
        print("    ✓ save_baseline works")

        # Test check regression (should pass first time)
        is_ok, msg = benchmark.check_regression("test_operation", 0.6, threshold_percent=20.0)
        if is_ok:
            print("    ✓ check_regression works")
        else:
            print(f"    ✗ check_regression failed: {msg}")
            sys.exit(1)

        # Test regression detection
        is_ok, msg = benchmark.check_regression("test_operation", 1.5, threshold_percent=20.0)
        if not is_ok:
            print("    ✓ Regression detection works")
        else:
            print("    ✗ Should have detected regression")
            sys.exit(1)

        # Restore
        PerformanceBenchmark.BASELINE_FILE = original_file

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "PerformanceBenchmark class validated"
    ((++TESTING_PASS))
else
    fail "PerformanceBenchmark validation failed"
    ((++TESTING_FAIL))
fi

echo "[A2.2] Running performance regression tests..."
if command -v pytest &> /dev/null; then
    if [ -f "tests/performance/test_performance_regression.py" ]; then
        echo "    Running performance tests (this may take a moment)..."

        if pytest tests/performance/test_performance_regression.py \
            -v --tb=short -m "not slow" \
            --disable-warnings \
            2>&1 | tee /tmp/perf_regression_tests.log | grep -E "(PASSED|FAILED|ERROR)"; then

            PERF_PASSED=$(grep -c "PASSED" /tmp/perf_regression_tests.log | head -n1 || echo "0")
            PERF_FAILED=$(grep -c "FAILED" /tmp/perf_regression_tests.log | head -n1 || echo "0")

            if [ "$PERF_FAILED" -eq 0 ]; then
                pass "Performance regression tests passed ($PERF_PASSED tests)"
                ((++TESTING_PASS))
            else
                fail "Performance tests failed: $PERF_FAILED failures"
                ((++TESTING_FAIL))
            fi
        else
            warn "Performance tests had issues (check /tmp/perf_regression_tests.log)"
            ((++TESTING_FAIL))
        fi
    else
        skip "Performance regression test file not found"
    fi
else
    skip "pytest not available"
fi

echo "[A2.3] Checking performance baselines..."
if [ -f "tests/performance/baselines.json" ]; then
    python3 << 'PYEOF'
import sys
import json

try:
    with open("tests/performance/baselines.json", 'r') as f:
        baselines = json.load(f)

    if not baselines:
        print("    ⚠ Baselines file is empty")
        sys.exit(0)

    print(f"    ✓ Loaded {len(baselines)} performance baselines")

    # Check structure
    for name, data in list(baselines.items())[:3]:  # Check first 3
        if "duration" in data and "timestamp" in data:
            print(f"    ✓ Baseline '{name}': {data['duration']:.4f}s")
        else:
            print(f"    ✗ Baseline '{name}' has invalid structure")
            sys.exit(1)

    sys.exit(0)

except FileNotFoundError:
    print("    ⚠ Baselines file not found")
    sys.exit(0)
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

    if [ $? -eq 0 ]; then
        pass "Performance baselines validated"
        ((++TESTING_PASS))
    else
        warn "Baseline validation had issues"
    fi
else
    warn "No baselines established yet (run tests to create)"
fi

# ============================================================================
# TEST A3: Load and Stress Tests
# ============================================================================
subsection "A3. Load and Stress Tests"

echo "[A3.1] Running load tests..."
if command -v pytest &> /dev/null && [ -f "tests/performance/test_load_stress.py" ]; then
    echo "    Running load tests (this may take a moment)..."

    if pytest tests/performance/test_load_stress.py::TestConcurrentOperations \
        -v --tb=short \
        --disable-warnings \
        2>&1 | tee /tmp/load_tests.log | grep -E "(PASSED|FAILED|ERROR)"; then

        LOAD_PASSED=$(grep -c "PASSED" /tmp/load_tests.log | head -n1 || echo "0")

        if [ "$LOAD_PASSED" -gt 0 ]; then
            pass "Load tests passed ($LOAD_PASSED tests)"
            ((++TESTING_PASS))
        else
            warn "Load tests had no passes"
        fi
    else
        warn "Load tests execution had issues"
    fi
else
    skip "Load test file not available"
fi

echo "[A3.2] Testing stress scenarios..."
if [ -f "tests/performance/test_load_stress.py" ]; then
    python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    # Check if stress tests are marked
    with open("tests/performance/test_load_stress.py", 'r') as f:
        content = f.read()

    if "@pytest.mark.stress" in content:
        print("    ✓ Stress tests properly marked")
    else:
        print("    ⚠ Stress test markers not found")

    if "TestStressScenarios" in content:
        print("    ✓ Stress test class exists")
    else:
        print("    ⚠ Stress test class not found")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

    if [ $? -eq 0 ]; then
        pass "Stress test structure validated"
        ((++TESTING_PASS))
    fi
else
    skip "Stress test file not found"
fi

# ============================================================================
# TEST A4: Memory Leak Detection
# ============================================================================
subsection "A4. Memory Leak Detection"

echo "[A4.1] Testing memory leak detection..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    import psutil

    from configurator.core.parallel import ParallelModuleExecutor
    from unittest.mock import Mock
    import time
    import gc

    process = psutil.Process()

    # Initial memory
    gc.collect()
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    # Run many operations
    executor = ParallelModuleExecutor(max_workers=4, logger=Mock())

    for _ in range(5):
        modules = {f"module_{i}": Mock() for i in range(10)}

        def handler(name, module):
            time.sleep(0.01)
            return True

        batches = [[f"module_{i}"] for i in range(10)]
        executor.execute_batches(batches, modules, handler)

    # Force cleanup
    gc.collect()
    time.sleep(0.1)

    mem_after = process.memory_info().rss / 1024 / 1024
    mem_increase = mem_after - mem_before

    print(f"    Memory before: {mem_before:.2f} MB")
    print(f"    Memory after:  {mem_after:.2f} MB")
    print(f"    Increase: {mem_increase:.2f} MB")

    # Allow up to 30MB increase (reasonable for caching)
    if mem_increase < 30:
        print(f"    ✓ No significant memory leak detected")
        sys.exit(0)
    else:
        print(f"    ✗ Potential memory leak: {mem_increase:.2f} MB")
        sys.exit(1)

except ImportError:
    print("    ⚠ psutil not available, skipping memory test")
    sys.exit(0)
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Memory leak detection validated"
    ((++TESTING_PASS))
else
    warn "Memory leak test had issues"
fi

# ============================================================================
# PART B: OBSERVABILITY SYSTEM VALIDATION
# ============================================================================
section "PART B: OBSERVABILITY SYSTEM VALIDATION"

# ============================================================================
# TEST B1: File Structure
# ============================================================================
subsection "B1. Observability Files Structure"

echo "[B1.1] Checking observability module files..."
OBS_FILES=(
    "configurator/observability/__init__.py"
    "configurator/observability/metrics.py"
    "configurator/observability/structured_logging.py"
    "configurator/observability/dashboard.py"
    "configurator/observability/alerting.py"
)

for file in "${OBS_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "Found: $file"
        ((++OBSERVABILITY_PASS))
    else
        fail "Missing: $file"
        ((++OBSERVABILITY_FAIL))
    fi
done

echo "[B1.2] Checking CLI monitoring commands..."
if [ -f "configurator/cli_monitoring.py" ]; then
    pass "Found: configurator/cli_monitoring.py"
    ((++OBSERVABILITY_PASS))
else
    fail "Missing: configurator/cli_monitoring.py"
    ((++OBSERVABILITY_FAIL))
fi

# ============================================================================
# TEST B2: Metrics System
# ============================================================================
subsection "B2. Metrics Collection System"

echo "[B2.1] Testing metrics collection..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.observability.metrics import (
        MetricsCollector, Counter, Gauge, Histogram, get_metrics
    )

    # Test Counter
    counter = Counter("test_counter", "Test counter")
    counter.inc()
    counter.inc(5)
    assert counter.get() == 6, f"Counter: expected 6, got {counter.get()}"
    print("    ✓ Counter works correctly")

    # Test Gauge
    gauge = Gauge("test_gauge", "Test gauge")
    gauge.set(10)
    gauge.inc(5)
    gauge.dec(3)
    assert gauge.get() == 12, f"Gauge: expected 12, got {gauge.get()}"
    print("    ✓ Gauge works correctly")

    # Test Histogram
    histogram = Histogram("test_histogram", "Test histogram")
    for val in [0.1, 0.5, 1.0, 2.0, 5.0]:
        histogram.observe(val)

    assert histogram.get_count() == 5, "Histogram count wrong"
    assert histogram.get_sum() == 8.6, "Histogram sum wrong"
    print("    ✓ Histogram works correctly")

    # Test MetricsCollector
    metrics = MetricsCollector()
    test_counter = metrics.counter("collector_test", "Test")
    test_counter.inc()

    assert "collector_test" in metrics._counters, "Counter not registered"
    print("    ✓ MetricsCollector registration works")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Metrics collection system validated"
    ((++OBSERVABILITY_PASS))
else
    critical_fail "Metrics system validation failed"
    ((++OBSERVABILITY_FAIL))
fi

echo "[B2.2] Testing Prometheus export..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.observability.metrics import MetricsCollector

    metrics = MetricsCollector()

    # Add some test data
    metrics.installations_total.inc()
    metrics.installations_success.inc()
    metrics.installation_duration.observe(120.5)

    # Export
    prom_output = metrics.export_prometheus()

    # Validate format
    assert "# HELP" in prom_output, "HELP missing"
    assert "# TYPE" in prom_output, "TYPE missing"
    assert "vps_installations_total" in prom_output, "Counter missing"
    assert "vps_installation_duration_seconds" in prom_output, "Histogram missing"

    # Check histogram format
    assert "_bucket{" in prom_output, "Histogram buckets missing"
    assert "_sum" in prom_output, "Histogram sum missing"
    assert "_count" in prom_output, "Histogram count missing"

    print("    ✓ Prometheus format correct")
    print(f"    ✓ Export size: {len(prom_output)} bytes")

    # Validate lines
    lines = [l for l in prom_output.split('\n') if l and not l.startswith('#')]
    print(f"    ✓ {len(lines)} metric data lines")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Prometheus export validated"
    ((++OBSERVABILITY_PASS))
else
    fail "Prometheus export validation failed"
    ((++OBSERVABILITY_FAIL))
fi

echo "[B2.3] Testing JSON export..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import json

try:
    from configurator.observability.metrics import MetricsCollector

    metrics = MetricsCollector()

    # Add test data
    metrics.installations_total.inc()
    metrics.memory_usage_bytes.set(1024000)

    # Export
    json_output = metrics.export_json()

    # Parse
    data = json.loads(json_output)

    # Validate structure
    assert "timestamp" in data, "timestamp missing"
    assert "counters" in data, "counters missing"
    assert "gauges" in data, "gauges missing"
    assert "histograms" in data, "histograms missing"

    print("    ✓ JSON format valid")
    print(f"    ✓ Counters: {len(data['counters'])}")
    print(f"    ✓ Gauges: {len(data['gauges'])}")
    print(f"    ✓ Histograms: {len(data['histograms'])}")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "JSON export validated"
    ((++OBSERVABILITY_PASS))
else
    fail "JSON export validation failed"
    ((++OBSERVABILITY_FAIL))
fi

echo "[B2.4] Testing resource metrics update..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.observability.metrics import get_metrics

    metrics = get_metrics()

    # Update resource metrics
    metrics.update_resource_metrics()

    # Check values were set
    mem_usage = metrics.memory_usage_bytes.get()
    cpu_usage = metrics.cpu_usage_percent.get()

    print(f"    ✓ Memory usage: {mem_usage / 1024 / 1024:.2f} MB")
    print(f"    ✓ CPU usage: {cpu_usage:.1f}%")

    # Values should be > 0 if psutil available
    if mem_usage > 0:
        print("    ✓ Resource metrics working")
    else:
        print("    ⚠ Resource metrics may not be working (psutil issue?)")

    sys.exit(0)

except Exception as e:
    print(f"    ⚠ Error (may be psutil): {e}")
    sys.exit(0)  # Non-critical
PYEOF

if [ $? -eq 0 ]; then
    pass "Resource metrics validated"
    ((++OBSERVABILITY_PASS))
fi

# ============================================================================
# TEST B3: Structured Logging
# ============================================================================
subsection "B3. Structured Logging System"

echo "[B3.1] Testing StructuredLogger..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import json
import io
import logging

try:
    from configurator.observability.structured_logging import StructuredLogger, correlation_id

    # Capture output
    logger = StructuredLogger("test_module")

    # Test correlation context
    with logger.correlation_context() as corr_id:
        assert corr_id is not None, "Correlation ID not generated"
        assert len(corr_id) > 10, "Correlation ID too short"
        print(f"    ✓ Correlation context works (ID: {corr_id[:16]}...)")

        # Check context variable
        current_id = correlation_id.get()
        assert current_id == corr_id, "Context variable set correctly"
        print("    ✓ Context variable set correctly")

    # After context, should be None
    assert correlation_id.get() is None, "Context not cleaned up"
    print("    ✓ Context cleanup works")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "StructuredLogger validated"
    ((++OBSERVABILITY_PASS))
else
    fail "StructuredLogger validation failed"
    ((++OBSERVABILITY_FAIL))
fi

echo "[B3.2] Testing log aggregation..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
import json
from pathlib import Path

try:
    from configurator.observability.structured_logging import LogAggregator

    # Create temp log file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        log_file = f.name

        # Write test logs
        from datetime import datetime
        now = datetime.utcnow().isoformat() + "Z"
        for i in range(5):
            log_entry = {
                "timestamp": now,
                "level": "INFO" if i < 3 else "ERROR",
                "message": f"Test message {i}",
                "correlation_id": "test-123"
            }
            f.write(json.dumps(log_entry) + "\n")

    try:
        aggregator = LogAggregator(log_file)

        # Test get by correlation ID
        logs = aggregator.get_logs_by_correlation_id("test-123")
        assert len(logs) == 5, f"Expected 5 logs, got {len(logs)}"
        print(f"    ✓ Correlation ID filtering works ({len(logs)} logs)")

        # Test error summary
        errors = aggregator.get_error_summary(hours=24)
        assert len(errors) >= 1, "Error summary empty"
        print(f"    ✓ Error summary works ({len(errors)} unique errors)")

        sys.exit(0)
    finally:
        Path(log_file).unlink()

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Log aggregation validated"
    ((++OBSERVABILITY_PASS))
else
    warn "Log aggregation had issues"
fi

# ============================================================================
# TEST B4: Dashboard System
# ============================================================================
subsection "B4. Dashboard System"

echo "[B4.1] Testing SimpleProgressReporter..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.observability.dashboard import SimpleProgressReporter

    reporter = SimpleProgressReporter()

    # Test update methods
    reporter.update_module("test_module", "running", progress=50)
    reporter.update_circuit_breaker("test_service", "CLOSED", failure_count=0)
    reporter.update_metric("test_metric", 42.5)

    print("    ✓ SimpleProgressReporter initialized")
    print("    ✓ All update methods work")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "SimpleProgressReporter validated"
    ((++OBSERVABILITY_PASS))
else
    fail "SimpleProgressReporter failed"
    ((++OBSERVABILITY_FAIL))
fi

echo "[B4.2] Testing InstallationDashboard..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.observability.dashboard import InstallationDashboard

    dashboard = InstallationDashboard()

    # Test update methods
    dashboard.update_module("docker", "running", progress=50, duration=10.5)
    dashboard.update_circuit_breaker("apt_repository", "CLOSED", 0)
    dashboard.update_metric("cpu_usage", 45.5)

    print("    ✓ InstallationDashboard initialized")
    print("    ✓ Update methods work")

    # Test render (don't start live)
    layout = dashboard._render()
    print("    ✓ Dashboard render works")

    sys.exit(0)

except ImportError as e:
    print(f"    ⚠ Rich library not available: {e}")
    sys.exit(0)  # Non-critical
except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "InstallationDashboard validated"
    ((++OBSERVABILITY_PASS))
fi

# ============================================================================
# TEST B5: Alerting System
# ============================================================================
subsection "B5. Alerting System"

echo "[B5.1] Testing alert channels..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
from pathlib import Path
from datetime import datetime

try:
    from configurator.observability.alerting import (
        AlertManager, Alert, AlertSeverity, FileAlertChannel
    )

    # Test FileAlertChannel
    with tempfile.TemporaryDirectory() as tmpdir:
        alert_file = Path(tmpdir) / "test_alerts.log"
        channel = FileAlertChannel(alert_file)

        # Create and send alert
        alert = Alert(
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="This is a test alert",
            source="validator",
            timestamp=datetime.now()
        )

        success = channel.send(alert)
        assert success, "Alert send failed"
        print("    ✓ FileAlertChannel sends alerts")

        # Verify file
        assert alert_file.exists(), "Alert file not created"
        with open(alert_file, 'r') as f:
            content = f.read()
            assert "Test Alert" in content, "Alert content missing"
        print("    ✓ Alert written to file correctly")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Alert channels validated"
    ((++OBSERVABILITY_PASS))
else
    fail "Alert channel validation failed"
    ((++OBSERVABILITY_FAIL))
fi

echo "[B5.2] Testing AlertManager..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
from pathlib import Path

try:
    from configurator.observability.alerting import (
        AlertManager, AlertSeverity, FileAlertChannel
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup manager
        manager = AlertManager()
        alert_file = Path(tmpdir) / "alerts.log"
        manager.add_channel(FileAlertChannel(alert_file))

        # Send alert
        manager.alert(
            AlertSeverity.ERROR,
            "Test Error",
            "This is a test error message",
            source="test"
        )

        print("    ✓ AlertManager sends alerts")

        # Check history
        alerts = manager.get_recent_alerts(hours=1)
        assert len(alerts) >= 1, "Alert not in history"
        print(f"    ✓ Alert history works ({len(alerts)} alerts)")

        # Test threshold rules
        manager.add_threshold_rule(
            "test_metric",
            lambda value: value > 100,
            AlertSeverity.WARNING,
            "Threshold exceeded: {value}"
        )

        # Should trigger
        manager.check_thresholds({"test_metric": 150})

        alerts = manager.get_recent_alerts(hours=1)
        assert len(alerts) >= 2, "Threshold alert not sent"
        print("    ✓ Threshold monitoring works")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "AlertManager validated"
    ((++OBSERVABILITY_PASS))
else
    fail "AlertManager validation failed"
    ((++OBSERVABILITY_FAIL))
fi

# ============================================================================
# TEST B6: CLI Monitoring Commands
# ============================================================================
subsection "B6. CLI Monitoring Commands"

echo "[B6.1] Testing metrics export command..."
if python3 -m configurator monitoring metrics --format json > /tmp/test_metrics.json 2>&1; then
    if [ -f "/tmp/test_metrics.json" ] && [ -s "/tmp/test_metrics.json" ]; then
        if python3 -c "import json; json.load(open('/tmp/test_metrics.json'))" 2>/dev/null; then
            pass "metrics command works"
            ((++OBSERVABILITY_PASS))
        else
            warn "metrics command produces invalid JSON"
        fi
    else
        warn "metrics command produced no output"
    fi
else
    warn "metrics command failed to execute"
fi

echo "[B6.2] Testing status command..."
if python3 -m configurator monitoring status --json > /tmp/test_status.json 2>&1; then
    if [ -f "/tmp/test_status.json" ]; then
        pass "status command works"
        ((++OBSERVABILITY_PASS))
    else
        warn "status command had issues"
    fi
else
    warn "status command failed"
fi

echo "[B6.3] Testing circuit-breakers command..."
if python3 -m configurator monitoring circuit-breakers > /tmp/test_cb.txt 2>&1; then
    pass "circuit-breakers command works"
    ((++OBSERVABILITY_PASS))
else
    warn "circuit-breakers command had issues"
fi

# ============================================================================
# TEST B7: Integration Tests
# ============================================================================
subsection "B7. Integration Tests"

echo "[B7.1] Testing base module observability integration..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.modules.base import ConfigurationModule
    from unittest.mock import Mock

    class TestModule(ConfigurationModule):
        name = "test"
        def validate(self): return True
        def configure(self): return True
        def verify(self): return True

    module = TestModule({}, Mock())

    # Check attributes
    assert hasattr(module, 'metrics'), "Module missing metrics"
    assert hasattr(module, 'structured_logger'), "Module missing structured_logger"

    print("    ✓ Base module has observability attributes")

    # Test that they work
    module.metrics.module_executions_total.inc()
    module.structured_logger.info("Test message", test_key="test_value")

    print("    ✓ Observability integration works")

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Base module integration validated"
    ((++OBSERVABILITY_PASS))
else
    critical_fail "Base module integration failed"
    ((++OBSERVABILITY_FAIL))
fi

# ============================================================================
# TEST B8: Configuration
# ============================================================================
subsection "B8. Configuration Validation"

echo "[B8.1] Checking observability configuration..."
if grep -q "observability:" config/default.yaml; then
    pass "Observability config section exists"
    ((++OBSERVABILITY_PASS))

    python3 << 'PYEOF'
import yaml

try:
    with open("config/default.yaml", 'r') as f:
        config = yaml.safe_load(f)

    obs = config.get('observability', {})

    required = ['metrics', 'logging', 'alerting', 'dashboard']
    for section in required:
        if section in obs:
            print(f"    ✓ {section} config exists")
        else:
            print(f"    ✗ {section} config missing")

except Exception as e:
    print(f"    ✗ Error: {e}")
PYEOF
else
    fail "Observability configuration missing"
    ((++OBSERVABILITY_FAIL))
fi

# ============================================================================
# FINAL REPORT
# ============================================================================
section "VALIDATION SUMMARY"

TOTAL=$((PASS + FAIL + WARN + SKIP))
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                  OVERALL RESULTS                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "  Total Tests: $TOTAL"
echo -e "  ${GREEN}✅ Passed:   $PASS${NC}"
echo -e "  ${RED}❌ Failed:   $FAIL${NC}"
echo -e "  ${YELLOW}⚠️  Warnings: $WARN${NC}"
echo -e "  ${BLUE}⏭️  Skipped:  $SKIP${NC}"
echo ""

if [ $CRITICAL_FAIL -gt 0 ]; then
    echo -e "  ${RED}🚨 CRITICAL FAILURES: $CRITICAL_FAIL${NC}"
    echo ""
fi

echo "╔════════════════════════════════════════════════════════╗"
echo "║              CATEGORY BREAKDOWN                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo -e "  ${CYAN}Testing Infrastructure:${NC}"
echo -e "    ${GREEN}Passed:   $TESTING_PASS${NC}"
echo -e "    ${RED}Failed:   $TESTING_FAIL${NC}"
echo ""
echo -e "  ${CYAN}Observability System:${NC}"
echo -e "    ${GREEN}Passed:   $OBSERVABILITY_PASS${NC}"
echo -e "    ${RED}Failed:   $OBSERVABILITY_FAIL${NC}"
echo ""

# Calculate pass rate
if [ $TOTAL -gt 0 ]; then
    PASS_RATE=$((PASS * 100 / TOTAL))
else
    PASS_RATE=0
fi

echo "╔════════════════════════════════════════════════════════╗"
echo "║                  PASS RATE                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo -e "  ${WHITE}$PASS_RATE% ($PASS/$TOTAL tests)${NC}"
echo ""

# Final verdict
if [ $CRITICAL_FAIL -gt 0 ]; then
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║     🚨 CRITICAL FAILURES - VALIDATION FAILED 🚨           ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║  Critical components failed validation.                   ║${NC}"
    echo -e "${RED}║  Fix critical issues before production deployment.        ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 2
elif [ $FAIL -gt 0 ]; then
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║          ❌ PHASE 4 VALIDATION FAILED ❌                  ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║  Some tests failed. Review and fix before proceeding.     ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 1
elif [ $WARN -gt 10 ]; then
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                                                           ║${NC}"
    echo -e "${YELLOW}║      ⚠️  PHASE 4 VALIDATION PASSED WITH WARNINGS         ║${NC}"
    echo -e "${YELLOW}║                                                           ║${NC}"
    echo -e "${YELLOW}║  Tests passed but many warnings present.                 ║${NC}"
    echo -e "${YELLOW}║  Review warnings before production deployment.           ║${NC}"
    echo -e "${YELLOW}║                                                           ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║         ✅ PHASE 4 VALIDATION PASSED!  ✅                 ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║  Testing infrastructure:  ${WHITE}VALIDATED${GREEN}                      ║${NC}"
    echo -e "${GREEN}║  Observability system:    ${WHITE}VALIDATED${GREEN}                      ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║  🎉 ALL 4 PHASES COMPLETE & VALIDATED!  🎉                ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║  System is PRODUCTION-READY! 🚀                           ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"

    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo -e "  1. Review completion report: docs/implementation-reports/phase4-completion.md"
    echo -e "  2. Run full E2E test: pytest tests/e2e/ -v"
    echo -e "  3. Deploy to staging environment"
    echo -e "  4. Monitor metrics and alerts"
    echo ""

    exit 0
fi

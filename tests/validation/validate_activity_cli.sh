#!/bin/bash
# Test activity monitoring CLI commands

echo "Activity Monitoring CLI Commands Test"
echo "============================================================"

FAILED=0

# Test 1: Help commands
echo ""
echo "1. Testing help commands..."

python3 -m configurator activity --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ activity --help works"
else
    echo "  ❌ activity --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator activity report --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ activity report --help works"
else
    echo "  ❌ activity report --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator activity anomalies --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ activity anomalies --help works"
else
    echo "  ❌ activity anomalies --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator activity log --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ activity log --help works"
else
    echo "  ❌ activity log --help failed"
    FAILED=$((FAILED + 1))
fi

# Final result
echo ""
echo "============================================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ All CLI commands validated (4/4 passed)"
    exit 0
else
    echo "❌ Some CLI commands failed ($FAILED failures)"
    exit 1
fi

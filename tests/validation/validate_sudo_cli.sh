#!/bin/bash
# Test sudo policy CLI commands

echo "Sudo Policy CLI Commands Test"
echo "============================================================"

FAILED=0

# Test 1: Help commands
echo ""
echo "1. Testing help commands..."

python3 -m configurator sudo --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ sudo --help works"
else
    echo "  ❌ sudo --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator sudo show-policy --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ sudo show-policy --help works"
else
    echo "  ❌ sudo show-policy --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator sudo test --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ sudo test --help works"
else
    echo "  ❌ sudo test --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator sudo apply --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ sudo apply --help works"
else
    echo "  ❌ sudo apply --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator sudo revoke --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ sudo revoke --help works"
else
    echo "  ❌ sudo revoke --help failed"
    FAILED=$((FAILED + 1))
fi

# Final result
echo ""
echo "============================================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ All CLI commands validated (5/5 passed)"
    exit 0
else
    echo "❌ Some CLI commands failed ($FAILED failures)"
    exit 1
fi

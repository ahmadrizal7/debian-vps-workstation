#!/bin/bash
# Test user lifecycle CLI commands

echo "User Lifecycle CLI Commands Test"
echo "============================================================"

FAILED=0

# Test 1: Help commands
echo ""
echo "1. Testing help commands..."

python3 -m configurator user --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ user --help works"
else
    echo "  ❌ user --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator user create --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ user create --help works"
else
    echo "  ❌ user create --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator user info --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ user info --help works"
else
    echo "  ❌ user info --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator user list --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ user list --help works"
else
    echo "  ❌ user list --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator user offboard --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ user offboard --help works"
else
    echo "  ❌ user offboard --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator user suspend --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ user suspend --help works"
else
    echo "  ❌ user suspend --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator user reactivate --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ user reactivate --help works"
else
    echo "  ❌ user reactivate --help failed"
    FAILED=$((FAILED + 1))
fi

# Test 2: List command
echo ""
echo "2. Testing list command..."
python3 -m configurator user list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ user list works"
else
    echo "  ❌ user list failed"
    FAILED=$((FAILED + 1))
fi

# Final result
echo ""
echo "============================================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ All CLI commands validated (8/8 passed)"
    exit 0
else
    echo "❌ Some CLI commands failed ($FAILED failures)"
    exit 1
fi

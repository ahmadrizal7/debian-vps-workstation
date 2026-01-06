#!/bin/bash
# Test team management CLI commands

echo "Team Management CLI Commands Test"
echo "============================================================"

FAILED=0

# Test 1: Help commands
echo ""
echo "1. Testing help commands..."

python3 -m configurator team --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ team --help works"
else
    echo "  ❌ team --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator team create --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ team create --help works"
else
    echo "  ❌ team create --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator team add-member --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ team add-member --help works"
else
    echo "  ❌ team add-member --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator team remove-member --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ team remove-member --help works"
else
    echo "  ❌ team remove-member --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator team info --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ team info --help works"
else
    echo "  ❌ team info --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator team list --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ team list --help works"
else
    echo "  ❌ team list --help failed"
    FAILED=$((FAILED + 1))
fi

# Test 2: List teams command
echo ""
echo "2. Testing list command..."

python3 -m configurator team list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ team list works"
else
    echo "  ❌ team list failed"
    FAILED=$((FAILED + 1))
fi

# Final result
echo ""
echo "============================================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ All CLI commands validated (7/7 passed)"
    exit 0
else
    echo "❌ Some CLI commands failed ($FAILED failures)"
    exit 1
fi

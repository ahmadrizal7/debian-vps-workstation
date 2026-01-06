#!/bin/bash
# Test temporary access CLI commands

echo "Temporary Access CLI Commands Test"
echo "============================================================"

FAILED=0

# Test 1: Help commands
echo ""
echo "1. Testing help commands..."

python3 -m configurator temp-access --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access --help works"
else
    echo "  ❌ temp-access --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator temp-access grant --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access grant --help works"
else
    echo "  ❌ temp-access grant --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator temp-access revoke --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access revoke --help works"
else
    echo "  ❌ temp-access revoke --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator temp-access extend --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access extend --help works"
else
    echo "  ❌ temp-access extend --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator temp-access approve-extension --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access approve-extension --help works"
else
    echo "  ❌ temp-access approve-extension --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator temp-access info --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access info --help works"
else
    echo "  ❌ temp-access info --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator temp-access list --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access list --help works"
else
    echo "  ❌ temp-access list --help failed"
    FAILED=$((FAILED + 1))
fi

python3 -m configurator temp-access check-expired --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access check-expired --help works"
else
    echo "  ❌ temp-access check-expired --help failed"
    FAILED=$((FAILED + 1))
fi

# Test 2: List command
echo ""
echo "2. Testing list command..."

python3 -m configurator temp-access list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access list works"
else
    echo "  ❌ temp-access list failed"
    FAILED=$((FAILED + 1))
fi

# Test 3: Check expired command
echo ""
echo "3. Testing check-expired command..."

python3 -m configurator temp-access check-expired > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ temp-access check-expired works"
else
    echo "  ❌ temp-access check-expired failed"
    FAILED=$((FAILED + 1))
fi

# Final result
echo ""
echo "============================================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ All CLI commands validated (10/10 passed)"
    exit 0
else
    echo "❌ Some CLI commands failed ($FAILED failures)"
    exit 1
fi

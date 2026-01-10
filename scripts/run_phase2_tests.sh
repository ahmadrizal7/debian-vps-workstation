#!/bin/bash
# Phase 2: XFCE Compositor & Polkit Rules Test Runner

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Phase 2: XFCE Compositor & Polkit Rules Test Suite      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Test results
UNIT_TESTS_PASSED=0
INTEGRATION_TESTS_PASSED=0
SECURITY_TESTS_PASSED=0

# Change to script directory
cd "$(dirname "$0")/.."

echo "📋 Phase 2: Unit Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/modules/test_desktop_phase2_unit.py -v; then
    echo -e "${GREEN}✅ Unit tests PASSED${NC}"
    UNIT_TESTS_PASSED=1
else
    echo -e "${RED}❌ Unit tests FAILED${NC}"
fi
echo ""

echo "📋 Phase 2: Security Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/security/test_phase2_security_penetration.py -v; then
    echo -e "${GREEN}✅ Security tests PASSED${NC}"
    SECURITY_TESTS_PASSED=1
else
    echo -e "${RED}❌ Security tests FAILED${NC}"
fi
echo ""

echo "📋 Phase 2: Integration Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/integration/test_desktop_phase2_integration.py -v; then
    echo -e "${GREEN}✅ Integration tests PASSED${NC}"
    INTEGRATION_TESTS_PASSED=1
else
    echo -e "${RED}❌ Integration tests FAILED${NC}"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Test Summary                                             ║"
echo "╚══════════════════════════════════════════════════════════╝"

TOTAL_PASSED=$((UNIT_TESTS_PASSED + INTEGRATION_TESTS_PASSED + SECURITY_TESTS_PASSED))
TOTAL_TESTS=3

echo "Automated Tests: $TOTAL_PASSED/$TOTAL_TESTS passed"
echo ""

if [ $UNIT_TESTS_PASSED -eq 1 ]; then echo -e "  ${GREEN}✓${NC} Unit Tests"; else echo -e "  ${RED}✗${NC} Unit Tests"; fi
if [ $SECURITY_TESTS_PASSED -eq 1 ]; then echo -e "  ${GREEN}✓${NC} Security Tests"; else echo -e "  ${RED}✗${NC} Security Tests"; fi
if [ $INTEGRATION_TESTS_PASSED -eq 1 ]; then echo -e "  ${GREEN}✓${NC} Integration Tests"; else echo -e "  ${RED}✗${NC} Integration Tests"; fi

echo ""

if [ $TOTAL_PASSED -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All automated tests PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests FAILED${NC}"
    exit 1
fi

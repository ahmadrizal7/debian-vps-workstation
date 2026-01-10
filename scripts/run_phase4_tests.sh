#!/bin/bash
# Phase 4: ZSH Environment Test Runner

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Phase 4: ZSH Environment Test Suite                     ║"
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
VALIDATION_TESTS_PASSED=0

# Change to script directory
cd "$(dirname "$0")/.."

echo "📋 Phase 4: Unit Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/modules/test_desktop_phase4_unit.py -v; then
    echo -e "${GREEN}✅ Unit tests PASSED${NC}"
    UNIT_TESTS_PASSED=1
else
    echo -e "${RED}❌ Unit tests FAILED${NC}"
fi
echo ""

echo "📋 Phase 4: Security Tests (Supply Chain)"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/security/test_phase4_supply_chain.py -v; then
    echo -e "${GREEN}✅ Security tests PASSED${NC}"
    SECURITY_TESTS_PASSED=1
else
    echo -e "${RED}❌ Security tests FAILED${NC}"
fi
echo ""

echo "📋 Phase 4: Validation Tests (Shell Scipts)"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/validation/test_phase4_shell_scripts.py -v; then
    echo -e "${GREEN}✅ Validation tests PASSED${NC}"
    VALIDATION_TESTS_PASSED=1
else
    echo -e "${RED}❌ Validation tests FAILED${NC}"
fi
echo ""

echo "📋 Phase 4: Integration Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/integration/test_desktop_phase4_integration.py -v; then
    echo -e "${GREEN}✅ Integration tests PASSED${NC}"
    INTEGRATION_TESTS_PASSED=1
else
    echo -e "${RED}❌ Integration tests FAILED${NC}"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Test Summary                                             ║"
echo "╚══════════════════════════════════════════════════════════╝"

TOTAL_PASSED=$((UNIT_TESTS_PASSED + INTEGRATION_TESTS_PASSED + SECURITY_TESTS_PASSED + VALIDATION_TESTS_PASSED))
TOTAL_TESTS=4

echo "Automated Tests: $TOTAL_PASSED/$TOTAL_TESTS passed"
echo ""

if [ $UNIT_TESTS_PASSED -eq 1 ]; then echo -e "  ${GREEN}✓${NC} Unit Tests"; else echo -e "  ${RED}✗${NC} Unit Tests"; fi
if [ $SECURITY_TESTS_PASSED -eq 1 ]; then echo -e "  ${GREEN}✓${NC} Security Tests"; else echo -e "  ${RED}✗${NC} Security Tests"; fi
if [ $VALIDATION_TESTS_PASSED -eq 1 ]; then echo -e "  ${GREEN}✓${NC} Validation Tests"; else echo -e "  ${RED}✗${NC} Validation Tests"; fi
if [ $INTEGRATION_TESTS_PASSED -eq 1 ]; then echo -e "  ${GREEN}✓${NC} Integration Tests"; else echo -e "  ${RED}✗${NC} Integration Tests"; fi

echo ""

if [ $TOTAL_PASSED -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All automated tests PASSED!${NC}"
    echo ""
    echo "Manual Verification Required:"
    echo "  1. Run: pytest tests/manual/test_phase4_terminal_experience.py"
    echo "  2. RDP into the VPS"
    echo "  3. Open Terminal (ZSH)"
    echo "  4. Verify prompt, plugins, and functionality"
    exit 0
else
    echo -e "${RED}❌ Some tests FAILED${NC}"
    exit 1
fi

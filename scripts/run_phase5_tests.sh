#!/bin/bash
# Comprehensive test runner for Phase 5

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Phase 5: Terminal Productivity Tools Tests              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TOTAL_TESTS=0

echo "🔐 Phase 1: Script Security Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/security/test_phase5_script_security.py -v --tb=short; then
    echo -e "${GREEN}✅ Script security tests PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ CRITICAL: Script security tests FAILED${NC}"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "📝 Phase 2: Configuration Validation Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/validation/test_phase5_config_validation.py -v --tb=short; then
    echo -e "${GREEN}✅ Configuration validation tests PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Configuration validation tests FAILED${NC}"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "📋 Phase 3: Unit Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/modules/test_desktop_phase5_unit.py -v \
    --cov=configurator.modules.desktop \
    --cov-append \
    --cov-report=term-missing; then
    echo -e "${GREEN}✅ Unit tests PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Unit tests FAILED${NC}"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "📋 Phase 4: Integration Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/integration/test_desktop_phase5_integration.py -v; then
    echo -e "${GREEN}✅ Integration tests PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Integration tests FAILED${NC}"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "🖥️  Phase 5: Terminal Workflow Tests (Manual)"
echo "─────────────────────────────────────────────────────────"
echo -e "${YELLOW}⚠️  Terminal workflow tests require manual validation: ${NC}"
echo ""
echo "   ${BLUE}Bat Configuration: ${NC}"
echo "      [ ] Syntax highlighting works"
echo "      [ ] Line numbers visible"
echo "      [ ] Git integration shows changes"
echo "      [ ] Theme matches terminal"
echo ""
echo "   ${BLUE}Exa Aliases:${NC}"
echo "      [ ] ll shows detailed listing with icons"
echo "      [ ] Git status column visible (in git repo)"
echo "      [ ] tree command works"
echo "      [ ] Sorted views work (lS, lt)"
echo ""
echo "   ${BLUE}Zoxide Navigation:${NC}"
echo "      [ ] z <partial-name> jumps correctly"
echo "      [ ] zi interactive mode works"
echo "      [ ] zoxide-stats shows database"
echo "      [ ] Learns frequently visited directories"
echo ""
echo "   ${BLUE}FZF Integration:${NC}"
echo "      [ ] Ctrl+R opens history search"
echo "      [ ] Preview window shows bat output"
echo "      [ ] Custom functions work (fcd, fe, fkill)"
echo ""
echo "   ${BLUE}Integration Scripts:${NC}"
echo "      [ ] preview script works with files/directories"
echo "      [ ] search script works (requires ripgrep)"
echo "      [ ] goto script works (interactive navigation)"
echo ""
echo "   ${BLUE}Workflow Functions:${NC}"
echo "      [ ] dev() function shows project overview"
echo "      [ ] sysinfo() function shows system info"
echo "      [ ] denv() function shows Docker environment"
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Test Summary                                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "Automated Tests: $TESTS_PASSED/$TOTAL_TESTS passed"
echo ""

if [ $TESTS_PASSED -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All automated tests PASSED! ${NC}"
    echo "Next step: Complete manual terminal workflow validation"
    exit 0
else
    echo -e "${RED}❌ Some tests FAILED${NC}"
    exit 1
fi

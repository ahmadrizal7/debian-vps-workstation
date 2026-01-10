#!/bin/bash
# Comprehensive test runner for Phase 4

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Phase 4: Zsh + Oh My Zsh + Powerlevel10k Tests          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TOTAL_TESTS=0

echo "🔐 Phase 1: Supply Chain Security Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/security/test_phase4_supply_chain.py -v --tb=short; then
    echo -e "${GREEN}✅ Supply chain security tests PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ CRITICAL: Supply chain tests FAILED${NC}"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "🐚 Phase 2: Shell Script Validation Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/validation/test_phase4_shell_scripts.py -v --tb=short; then
    echo -e "${GREEN}✅ Shell script validation tests PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ CRITICAL: Shell validation tests FAILED${NC}"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "📋 Phase 3: Unit Tests"
echo "─────────────────────────────────────────────────────────"
if python3 -m pytest tests/modules/test_desktop_phase4_unit.py -v \
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
if python3 -m pytest tests/integration/test_desktop_phase4_integration.py -v; then
    echo -e "${GREEN}✅ Integration tests PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ Integration tests FAILED${NC}"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo ""

echo "🖥️  Phase 5: Terminal Experience Tests (Manual)"
echo "─────────────────────────────────────────────────────────"
echo -e "${YELLOW}⚠️  Terminal UX tests require manual validation:  ${NC}"
echo ""
echo "   1. Deploy to test VM:   ./scripts/deploy_test.sh"
echo "   2. Run:   vps-configurator install --profile beginner"
echo "   3. Connect via RDP"
echo "   4. Open terminal and complete checklist:"
echo ""
echo "   ${BLUE}Shell Startup: ${NC}"
echo "      [ ] Terminal opens in <1 second"
echo "      [ ] Powerlevel10k instant prompt works"
echo "      [ ] Prompt shows icons (no boxes)"
echo ""
echo "   ${BLUE}Autosuggestions:${NC}"
echo "      [ ] Gray suggestions appear after typing"
echo "      [ ] Right arrow accepts suggestion"
echo ""
echo "   ${BLUE}Syntax Highlighting:${NC}"
echo "      [ ] Valid commands green, invalid red"
echo "      [ ] Highlights update in real-time"
echo ""
echo "   ${BLUE}FZF History:${NC}"
echo "      [ ] Ctrl+R opens fuzzy search"
echo "      [ ] Can filter and select history"
echo ""
echo "   ${BLUE}Aliases:${NC}"
echo "      [ ] ll works (detailed listing)"
echo "      [ ] gs works (git status)"
echo "      [ ] Modern tools have fallbacks"
echo ""
echo "   ${BLUE}Font Rendering:${NC}"
echo "      [ ] All icons visible (no boxes)"
echo "      [ ] Meslo Nerd Font active"
echo ""
echo "   ${BLUE}Customization:${NC}"
echo "      [ ] p10k configure wizard works"
echo ""
echo "   5. Document results in:   tests/manual/PHASE4_RESULTS.md"
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Test Summary                                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "Automated Tests: $TESTS_PASSED/$TOTAL_TESTS passed"
echo ""

if [ $TESTS_PASSED -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All automated tests PASSED! ${NC}"
    echo "Next step: Complete manual terminal experience validation"
    exit 0
else
    echo -e "${RED}❌ Some tests FAILED${NC}"
    exit 1
fi

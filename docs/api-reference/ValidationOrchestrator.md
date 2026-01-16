# ValidationOrchestrator

**Module:** `configurator.validators.orchestrator`

Orchestrates validation across multiple tiers.

Tier 1 (Critical): Must pass for installation to proceed
Tier 2 (High): Important but can be overridden by user
Tier 3 (Medium): Warnings only, installation continues

## Methods

### `__init__(self, console: Optional[rich.console.Console] = None, logger: Optional[logging.Logger] = None)`

Initialize validation orchestrator.

Args:
    console: Rich console for output (creates new if not provided)
    logger: Logger instance (creates new if not provided)

---

### `register_validator(self, tier: int, validator: configurator.validators.base.BaseValidator) -> None`

Register a validator in a specific tier.

Args:
    tier: Tier number (1=critical, 2=high, 3=medium)
    validator: Validator instance to register

Raises:
    ValueError: If tier is not 1, 2, or 3

---

### `run_validation(self, interactive: bool = True, auto_fix: bool = False) -> Tuple[bool, List[configurator.validators.base.ValidationResult]]`

Run tiered validation process.

Args:
    interactive: If True, prompt user for failures; if False, fail immediately
    auto_fix: If True, attempt automatic fixes for failures

Returns:
    Tuple of (overall_passed, all_results)

---

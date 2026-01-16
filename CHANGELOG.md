# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-16

### Added (Sprint 1)

- Tiered validation system (Critical/High/Medium)
- ValidationOrchestrator with Rich UI
- `@module`, `@depends_on`, `@conflicts_with` decorators
- SQLite-backed StateManager with checkpoint/resume
- 85%+ test coverage base

### Added (Sprint 2)

- Hybrid execution engine (Parallel + Pipeline)
- Enhanced progress reporter with Rich animations
- Full-screen TUI dashboard using Textual
- Enhanced hooks system with 15+ lifecycle events
- Plugin-based hook system

### Added (Sprint 3)

- Interactive configuration wizard (7 screens)
- Profile template system (5 built-in profiles)
- Profile builder with smart suggestions
- Dependency visualizer (ASCII tree + Mermaid)
- Interactive prompts (Confirm, Select, MultiSelect)
- Enhanced error formatting (WHAT/WHY/HOW)
- Module search and filtering

### Added (Sprint 4)

- Comprehensive user documentation (100+ pages)
- Developer guides and API reference
- CI/CD pipeline (GitHub Actions)
- Performance benchmarks
- Security scanning
- Release automation script

### Changed

- Improved installation speed (4x faster with parallel execution)
- Enhanced error messages with actionable solutions
- Better progress visualization

### Breaking Changes

- New validator system replaces SystemValidator
- Configuration file format updated (v1 → v2)
- See [Migration Guide](docs/migration/v1-to-v2.md)

### Migration

- Follow [v1 to v2 Migration Guide](docs/migration/v1-to-v2.md)

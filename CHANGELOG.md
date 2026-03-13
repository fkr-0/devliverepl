# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-03-13

### Added
- Complete core REPL server with detach()/shutdown() API
- Frame capture and context management system
- Object registry with @expose decorator
- Banner generation (minimal/rich/custom modes)
- Interactive REPL commands (%ls, %import, %where, %env, %help)
- Telnet server wrapper with asyncio integration
- Graceful shutdown handling with atexit support
- Configuration management via dataclass
- Full debugger integrations suite:
  - Standard library pdb
  - PuDB (curses TUI)
  - IPython debugger (ipdb)
  - pdb++ (enhanced pdb)
  - PatDB (pattern debugger)
  - Web-PDB (browser-based)
- Thread-safe daemon thread execution
- Comprehensive test suite (25 tests, 100% passing)
- Usage examples (basic, Flask, data pipeline)
- Full documentation and README
- GitHub release workflow for PyPI publishing

### Changed
- Initial stable release

## [0.1.0] - 2025-03-13

### Added
- Initial proof-of-concept
- Basic telnet REPL functionality

---

[0.2.0]: https://github.com/devliverepl/devliverepl/releases/tag/v0.2.0
[0.1.0]: https://github.com/devliverepl/devliverepl/releases/tag/v0.1.0

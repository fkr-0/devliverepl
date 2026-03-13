# devliverepl

> Self-sufficient debugging REPL for running Python programs

[![PyPI](https://img.shields.io/pypi/v/devliverepl)](https://pypi.org/project/devliverepl/)
[![Python](https://img.shields.io/pypi/pyversions/devliverepl)](https://pypi.org/project/devliverepl/)
[![License](https://img.shields.io/pypi/l/devliverepl)](LICENSE)

devliverepl provides an always-on ptpython REPL server accessible via telnet, enabling live inspection and debugging of running Python applications without interrupting execution.

## Features

- 🔄 **Live inspection** — Connect to running programs and inspect state
- 📦 **Context capture** — Automatic capture of locals/globals from call site
- 🎯 **Explicit exposure** — `@expose` decorator to mark important objects
- 🔍 **Debugger integration** — Built-in support for pdb, pudb, ipdb, pdbpp, patdb, webpdb
- 🎨 **Rich terminal** — ptpython with syntax highlighting and auto-completion
- 🛡️ **Thread-safe** — Daemon thread doesn't block your application
- 🚦 **Graceful shutdown** — Clean connection handling with atexit support

## Installation

```bash
# Basic installation
pip install devliverepl

# With uv
uv add devliverepl

# With optional debugger integrations
pip install devliverepl[debuggers]
uv add devliverepl --extra debuggers
```

## Quick Start

```python
import devliverepl

app_state = {"users": [], "status": "running"}

# Start the REPL - captures app_state
devliverepl.detach()

# Connect from another terminal:
# $ telnet localhost 8022
#
# In the REPL, you can access:
# >>> app_state
# {'users': [], 'status': 'running'}
# >>> app_state['users'].append('test')
```

## Usage

### Basic Usage

```python
import devliverepl

# Your application state
config = {"debug": True}
database = Database()

# Start REPL (captures locals)
devliverepl.detach(port=8022)

# ... application runs ...
```

### Exposing Objects

Use the `@expose` decorator to make objects available across all connections:

```python
import devliverepl

@devliverepl.expose
class Database:
    """Database connection pool."""

    def query(self, sql):
        return self._execute(sql)

@devliverepl.expose
def get_stats():
    """Get application statistics."""
    return stats

devliverepl.detach()
```

### Configuration

```python
import devliverepl

devliverepl.configure(
    port=8022,
    host="127.0.0.1",
    banner="rich",  # or "minimal" or "custom"
    log_connections=True,
)

devliverepl.detach()
```

### Custom Banner

```python
import devliverepl
import os

devliverepl.set_banner(lambda: f"""
╭──────────────────────────────────╮
│  MyApp Debugger — PID {os.getpid()}   │
╰──────────────────────────────────╯
""")

devliverepl.detach()
```

### REPL Commands

When connected, use `%` commands:

```
%ls          # List exposed objects and captured variables
%import os   # Import a module
%where db    # Show where an object was defined
%env         # Show captured environment summary
%help        # Show all commands
```

### Debugger Integration

```python
# In the REPL, use the debug helper:
debug.attach()      # Auto-detect best debugger
debug.pudb()        # Use PuDB
debug.ipdb()        # Use IPython debugger
debug.pdbpp()       # Use pdb++
debug.patdb()       # Use PatDB (pattern debugger)
debug.web()         # Use Web-PDB (browser UI)

debug.list_available()  # Show installed debuggers
```

### Shutdown

```python
import devliverepl

# Graceful shutdown (waits for connections to close)
devliverepl.shutdown()

# Immediate shutdown
devliverepl.shutdown(force=True)
```

## Examples

See the [examples/](examples/) directory for more:

- [`basic_usage.py`](examples/basic_usage.py) — Simple long-running script
- [`flask_app.py`](examples/flask_app.py) — Flask web server integration
- [`data_pipeline.py`](examples/data_pipeline.py) — Data processing pipeline

## How It Works

1. Call `devliverepl.detach()` in your code
2. The function captures the calling frame's `locals()` and `globals()`
3. A ptpython REPL server starts in a daemon thread
4. Connect via telnet to inspect the captured state
5. Disconnect anytime without stopping your application

## Architecture

```
devliverepl/
├── __init__.py         # Public API: detach(), shutdown(), @expose
├── core.py             # REPLServer, event loop management
├── capture.py          # Frame capture, context extraction
├── registry.py         # Exposed object registry
├── banner.py           # Banner generation
├── commands.py         # % commands implementation
├── shutdown.py         # Graceful shutdown handling
└── integrations/       # Debugger integrations
    ├── pdb.py
    ├── pudb.py
    ├── ipdb.py
    └── ...
```

## Requirements

- Python 3.10+
- ptpython >= 3.0.0
- prompt-toolkit >= 3.0.0

Optional (for debugger integrations):
- pudb >= 2022.1
- ipdb >= 0.13.0
- pdbpp >= 0.10.0
- web-pdb >= 0.5.0

## Roadmap

### v0.2.0 (Current)
- ✅ Multiple named REPLs (foundational support)
- ✅ Enhanced configuration system
- ✅ Full debugger integration suite

### v0.3.0 (Planned)
- ⏳ Thread-aware stack inspection
- ⏳ Context manager pattern
- ⏳ SSH support
- ⏳ Authentication
- ⏳ TLS/SSL
- ⏳ Multi-client collaboration

## Contributing

Contributions welcome! Please read our contributing guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

```bash
# Clone the repository
git clone https://github.com/devliverepl/devliverepl.git
cd devliverepl

# Install in development mode
uv sync --extra dev

# Run tests
pytest

# Run type checking
mypy devliverepl/

# Run linting
ruff check devliverepl/
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with:
- [ptpython](https://github.com/prompt-toolkit/ptpython) — Python REPL
- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) — Terminal UI
- [uv](https://github.com/astral-sh/uv) — Python package manager

---

**Happy debugging! 🐛**

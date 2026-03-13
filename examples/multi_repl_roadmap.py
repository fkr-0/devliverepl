"""Example showing how multiple REPLs would be used (future feature).

This is a roadmap document showing the planned API for multiple REPLs.
"""

# ROADMAP: v0.2.0 Multiple Named REPLs
#
# When working with microservices or multi-process applications,
# you might want separate REPLs for different components:
#
# # In API server process:
# devliverepl.detach("api", port=8022)
#
# # In worker process:
# devliverepl.detach("worker", port=8023)
#
# # In database layer:
# devliverepl.detach("db", port=8024)
#
# # List all active REPLs:
# devliverepl.list_repls()
# # => ["api", "worker", "db"]
#
# # Attach to specific REPL's context from main REPL:
# devliverepl.attach_context("worker")
#
# # Or use context manager (v0.2.0):
# with devliverepl.session("api") as repl:
#     # REPL runs here
#     pass
# # Automatically shut down on exit

print("Multi-REPL support is planned for v0.2.0")
print("\nPlanned API:")
print("  devliverepl.detach(name, port)  # Named REPL")
print("  devliverepl.list()              # List active REPLs")
print("  devliverepl.shutdown(name)      # Shutdown specific REPL")
print("  with devliverepl.session() ...  # Context manager")

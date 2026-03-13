"""Basic usage example for devliverepl."""

import devliverepl
import time


def main():
    # Application state
    users = []
    config = {"debug": True, "port": 8000}

    # Start the REPL - captures users and config
    devliverepl.detach(port=8022)
    print("REPL started on port 8022")
    print("Connect with: telnet localhost 8022")

    # Simulate a long-running process
    for i in range(10):
        users.append(f"user_{i}")
        print(f"Processing user {i}")
        time.sleep(0.5)

        # In the REPL, you can now inspect:
        # - users (the list being built)
        # - config (the config dict)
        # - i (the current iteration)

    print("Done! Users:", users)


if __name__ == "__main__":
    main()

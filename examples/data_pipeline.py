"""Data pipeline example with devliverepl."""

import devliverepl
import time


class DataProcessor:
    """Example data processor."""

    def __init__(self, name):
        self.name = name
        self.batch = []
        self.stats = {"processed": 0, "errors": 0}

    def process(self, item):
        """Process an item."""
        try:
            # Simulate processing
            result = f"{self.name}_processed_{item}"
            self.batch.append(result)
            self.stats["processed"] += 1
            return result
        except Exception as e:
            self.stats["errors"] += 1
            return None

    def flush(self):
        """Flush the batch."""
        result = list(self.batch)
        self.batch.clear()
        return result


# Expose the processor class
@devliverepl.expose
class Processor:
    """Public processor interface."""
    pass


def main():
    # Create processor
    processor = DataProcessor("main")

    # Start REPL - captures processor
    devliverepl.detach(port=8022)
    print("Data pipeline running. REPL on port 8022")
    print("In REPL, try:")
    print("  processor.stats     # See processing stats")
    print("  processor.batch     # See current batch")

    # Process data stream
    for i in range(100):
        processor.process(f"item_{i}")

        if i % 20 == 0:
            flushed = processor.flush()
            print(f"Flushed {len(flushed)} items")

        time.sleep(0.1)


if __name__ == "__main__":
    main()

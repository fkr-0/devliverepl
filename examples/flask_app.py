"""Flask web server example with devliverepl."""

import devliverepl


class Database:
    """Mock database for example."""

    def __init__(self):
        self.connections = 0
        self.queries = []

    def query(self, sql):
        self.connections += 1
        self.queries.append(sql)
        return f"Result of: {sql}"


# Expose the database class
@devliverepl.expose
def get_db():
    """Get the database instance."""
    return db


# Create Flask app
try:
    from flask import Flask

    app = Flask(__name__)
    db = Database()

    @app.route("/")
    def home():
        return f"Hello! DB connections: {db.connections}"

    @app.route("/query/<sql>")
    def query(sql):
        return db.query(sql)

    # Start REPL after app setup - captures app, db
    devliverepl.detach(port=8022)

    if __name__ == "__main__":
        print("REPL available on telnet localhost 8022")
        print("Try these in the REPL:")
        print("  get_db()          # Get the database instance")
        print("  get_db().queries  # See all queries")
        app.run(debug=True)

except ImportError:
    print("Flask not installed. Install with: pip install flask")


"""School transport management system with secure database operations."""

import sqlite3
from pathlib import Path


def create_connection():
    """Create and initialize the in-memory rider database."""
    connection = sqlite3.connect(":memory:")

    connection.execute(
        """
        CREATE TABLE riders (
            id INTEGER PRIMARY KEY,
            student TEXT,
            route TEXT,
            stop TEXT,
            fee INTEGER
        )
        """
    )

    return connection


def enroll_rider(connection, student, route, stop, fee):
    """Enroll a rider using a parameterized SQL query."""
    connection.execute(
        """
        INSERT INTO riders (student, route, stop, fee)
        VALUES (?, ?, ?, ?)
        """,
        (student, route, stop, fee),
    )

    connection.commit()


def route_roster(connection, route):
    """Return the student names registered on a route."""
    cursor = connection.execute(
        "SELECT student FROM riders WHERE route = ?",
        (route,),
    )

    return [row[0] for row in cursor.fetchall()]


def export_roster(connection, path, route):
    """Export a route roster to a UTF-8 text file."""
    with Path(path).open("w", encoding="utf-8") as output_file:
        for name in route_roster(connection, route):
            output_file.write(name + "\n")


def dispatch_alert(route):
    """Display a bus dispatch alert."""
    print(f"dispatching bus {route}")


def fee_collected(connection, route):
    """Return the total fee collected for a route."""
    result = connection.execute(
        "SELECT SUM(fee) FROM riders WHERE route = ?",
        (route,),
    ).fetchone()

    return result[0] or 0


def main():
    """Run the school transport demonstration."""
    connection = create_connection()

    try:
        enroll_rider(connection, "Tara", "R1", "Lake Road", 1800)
        enroll_rider(connection, "Kabir", "R1", "Mill Street", 1800)
        enroll_rider(connection, "Zoya", "R2", "Fort Gate", 2100)

        if fee_collected(connection, "R1") != 3600:
            raise ValueError("Incorrect fee total for route R1")

        export_roster(connection, "route_r1.txt", "R1")
        dispatch_alert("R1")
        print(route_roster(connection, "R2"))

    finally:
        connection.close()


if __name__ == "__main__":
    main()

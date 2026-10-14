"""School Bus Transport Register module.

Manages student enrollment, route rosters, roster export,
dispatch notifications, and fee collection totals.
"""

import sqlite3

# Initialize in-memory SQLite database
conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE riders ("
    "id INTEGER PRIMARY KEY, "
    "student TEXT, "
    "route TEXT, "
    "stop TEXT, "
    "fee INTEGER"
    ")"
)


def enroll_rider(student, route, stop, fee):
    """Enroll a student on a specific bus route with their stop and fee."""
    conn.execute(
        "INSERT INTO riders (student, route, stop, fee) VALUES (?, ?, ?, ?)",
        (student, route, stop, fee),
    )
    conn.commit()


def route_roster(route, _driver=None):
    """Retrieve the list of student names enrolled on a given route."""
    cursor = conn.execute(
        "SELECT student FROM riders WHERE route = ?", (route,)
    )
    return [r[0] for r in cursor]


def export_roster(path, route):
    """Export the list of enrolled students for a route to a text file."""
    with open(path, "w", encoding="utf-8") as out:
        for name in route_roster(route, None):
            out.write(name + "\n")


def dispatch_alert(route):
    """Display dispatch alert message for a given bus route."""
    print("dispatching bus " + route)


def fee_collected(route):
    """Calculate the total fee collected for a given route."""
    try:
        cursor = conn.execute(
            "SELECT SUM(fee) FROM riders WHERE route = ?", (route,)
        )
        total = cursor.fetchone()[0]
        return total if total is not None else 0
    except sqlite3.Error:
        return 0


def main():
    """Run demonstration workflow for school bus transport register."""
    enroll_rider("Tara", "R1", "Lake Road", 1800)
    enroll_rider("Kabir", "R1", "Mill Street", 1800)
    enroll_rider("Zoya", "R2", "Fort Gate", 2100)
    total_r1 = fee_collected("R1")
    if total_r1 != 3600:
        raise ValueError(f"Expected fee 3600, got {total_r1}")
    export_roster("route_r1.txt", "R1")
    dispatch_alert("R1")
    print(route_roster("R2", "Mr. Das"))


if __name__ == "__main__":
    main()

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = "registrations.db"

events = [
    {
        "id": 1,
        "name": "Tech Fest 2026",
        "date": "October 15, 2026",
        "venue": "College Auditorium",
        "description": "Technical competitions, coding contests and workshops."
    },
    {
        "id": 2,
        "name": "Cultural Fest 2026",
        "date": "October 20, 2026",
        "venue": "Main Ground",
        "description": "Music, dance, cultural programs and entertainment."
    },
    {
        "id": 3,
        "name": "Sports Meet 2026",
        "date": "October 25, 2026",
        "venue": "College Sports Ground",
        "description": "Inter-college sports competitions and activities."
    }
]


# ---------------- DATABASE ----------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            event TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Initialize database when application starts
init_db()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html", events=events)


# ---------------- EVENTS ----------------

@app.route("/events")
def event_list():
    return render_template("events.html", events=events)


# ---------------- REGISTRATION ----------------

@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):

    event = next((e for e in events if e["id"] == event_id), None)

    if event is None:
        return "Event not found", 404

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO registrations
            (name, email, department, event)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            department,
            event["name"]
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("success"))

    return render_template("register.html", event=event)


# ---------------- SUCCESS ----------------

@app.route("/success")
def success():
    return render_template("success.html")


# ---------------- ADMIN ----------------

@app.route("/admin")
def admin():

    connection = get_db_connection()

    registrations = connection.execute("""
        SELECT id, name, email, department, event
        FROM registrations
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        registrations=registrations
    )


# ---------------- STATUS ----------------

@app.route("/status")
def status():
    return {
        "status": "healthy",
        "application": "College Event Management System",
        "version": "1.0.0"
    }


# ---------------- API INFO ----------------

@app.route("/api/info")
def api_info():

    connection = get_db_connection()

    registration_count = connection.execute(
        "SELECT COUNT(*) FROM registrations"
    ).fetchone()[0]

    connection.close()

    return {
        "application": "College Event Management System",
        "events": len(events),
        "registrations": registration_count
    }


# ---------------- HEALTH CHECK ----------------

@app.route("/health")
def health():
    return {"status": "healthy"}, 200


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
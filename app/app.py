from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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

registrations = []


@app.route("/")
def home():
    return render_template("index.html", events=events)


@app.route("/events")
def event_list():
    return render_template("events.html", events=events)


@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):

    event = next((e for e in events if e["id"] == event_id), None)

    if event is None:
        return "Event not found", 404

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]

        registrations.append({
            "name": name,
            "email": email,
            "department": department,
            "event": event["name"]
        })

        return redirect(url_for("success"))

    return render_template("register.html", event=event)


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/admin")
def admin():
    return render_template("admin.html", registrations=registrations)


@app.route("/status")
def status():
    return {
        "status": "healthy",
        "application": "College Event Management System",
        "version": "1.0.0"
    }


@app.route("/api/info")
def api_info():
    return {
        "application": "College Event Management System",
        "events": len(events),
        "registrations": len(registrations)
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
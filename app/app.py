"""Flask web application used by the CI/CD pipeline."""
import os
import platform
import time
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, Response

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
START_TIME = time.time()
REQUEST_COUNT = {"total": 0}


@app.before_request
def count_requests():
    REQUEST_COUNT["total"] += 1


def uptime_seconds() -> int:
    return int(time.time() - START_TIME)


@app.route("/")
def home():
    return render_template(
        "index.html",
        message="Welcome to the Automated CI/CD Pipeline demo",
        version=APP_VERSION,
    )


@app.route("/status")
def status():
    return render_template(
        "status.html",
        version=APP_VERSION,
        uptime=uptime_seconds(),
        host=platform.node(),
        python_version=platform.python_version(),
        now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )


@app.route("/api/info")
def api_info():
    return jsonify(
        name="flask-cicd-app",
        message="Welcome to the Automated CI/CD Pipeline demo",
        version=APP_VERSION,
        uptime_seconds=uptime_seconds(),
    )


@app.route("/health")
def health():
    """Used by Docker HEALTHCHECK and Jenkins deployment verification."""
    return jsonify(status="ok", version=APP_VERSION), 200


@app.route("/metrics")
def metrics():
    """Prometheus-format metrics (optional monitoring module)."""
    body = (
        "# HELP app_requests_total Total HTTP requests handled.\n"
        "# TYPE app_requests_total counter\n"
        f"app_requests_total {REQUEST_COUNT['total']}\n"
        "# HELP app_uptime_seconds Seconds since the app started.\n"
        "# TYPE app_uptime_seconds gauge\n"
        f"app_uptime_seconds {uptime_seconds()}\n"
        "# HELP app_up Whether the application is up.\n"
        "# TYPE app_up gauge\n"
        "app_up 1\n"
    )
    return Response(body, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))

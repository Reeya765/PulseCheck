
from flask import Flask, jsonify, render_template
import os
import itertools
import threading
import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

SERVICES = {
    "service-a": os.getenv(
        "SERVICE_A_URL", "http://service_a:5000"
    ),
    "service-b": os.getenv(
        "SERVICE_B_URL", "http://service_b:5000"
    ),
}

_service_cycle = itertools.cycle(SERVICES.items())
_cycle_lock = threading.Lock()


def check_service(name, url):
    try:
        response = requests.get(f"{url}/health", timeout=2)

        if response.ok:
            data = response.json()
            return {
                "service": name,
                "status": "healthy",
                "hostname": data.get("hostname"),
                "uptime_seconds": data.get("uptime_seconds"),
            }

        return {
            "service": name,
            "status": "unhealthy",
        }

    except (requests.RequestException, ValueError):
        return {
            "service": name,
            "status": "unavailable",
        }


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/status")
def status():
    with ThreadPoolExecutor(
        max_workers=len(SERVICES)
    ) as executor:
        results = list(
            executor.map(
                lambda item: check_service(item[0], item[1]),
                SERVICES.items(),
            )
        )

    healthy_count = sum(
        result["status"] == "healthy"
        for result in results
    )

    if healthy_count == len(results):
        system_status = "healthy"
    elif healthy_count > 0:
        system_status = "degraded"
    else:
        system_status = "unavailable"

    return jsonify({
        "total_services": len(results),
        "healthy_services": healthy_count,
        "system_status": system_status,
        "services": results,
    })


@app.get("/route")
def route():
    # Try the next backend first, then fall back to the other.
    with _cycle_lock:
        first = next(_service_cycle)
        candidates = [first] + [
            item
            for item in SERVICES.items()
            if item[0] != first[0]
        ]

    for name, url in candidates:
        try:
            response = requests.get(url, timeout=2)

            return jsonify({
                "routed_to": name,
                "backend_response": response.json(),
            }), response.status_code

        except (requests.RequestException, ValueError):
            continue

    return jsonify({
        "error": "No backend service is currently available"
    }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

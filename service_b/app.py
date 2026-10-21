from flask import Flask, jsonify
import os
import socket
import time

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "service-a")
START_TIME = time.time()


@app.get("/health")
def health():
    return jsonify({
        "service": SERVICE_NAME,
        "status": "healthy",
        "hostname": socket.gethostname(),
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }), 200


@app.get("/")
def home():
    return jsonify({
        "message": "PulseCheck backend is running",
        "service": SERVICE_NAME,
        "hostname": socket.gethostname()
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

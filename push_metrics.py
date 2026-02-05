import os
import requests
from prometheus_client import generate_latest, REGISTRY
from requests.auth import HTTPBasicAuth

REMOTE_WRITE_URL = os.environ["GRAFANA_REMOTE_WRITE_URL"]
USERNAME = os.environ["GRAFANA_USERNAME"]
PASSWORD = os.environ["GRAFANA_PASSWORD"]

def push_metrics():
    data = generate_latest(REGISTRY)

    requests.post(
        REMOTE_WRITE_URL,
        data=data,
        headers={"Content-Type": "text/plain"},
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=5
    )
    print("PUSH METRICS ->", REMOTE_WRITE_URL)
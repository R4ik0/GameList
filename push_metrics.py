import os
import requests
from prometheus_client import generate_latest, REGISTRY
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import time

load_dotenv()

REMOTE_WRITE_URL = os.environ["GRAFANA_REMOTE_WRITE_URL"]
USERNAME = os.environ["GRAFANA_USERNAME"]
PASSWORD = os.environ["GRAFANA_PASSWORD"]

def push_metrics():
    # Convertir métriques Prometheus → format InfluxDB line protocol
    lines = []
    
    for metric in REGISTRY.collect():
        for sample in metric.samples:
            # Construire les labels (tags en InfluxDB)
            if sample.labels:
                labels = "," + ",".join([f"{k}={v}" for k, v in sample.labels.items()])
            else:
                labels = ""
            
            # Format: metric_name,label1=value1,label2=value2 value=123 timestamp
            timestamp_ns = int(time.time() * 1e9)  # Nanoseconds
            lines.append(f"{sample.name}{labels} value={sample.value} {timestamp_ns}")

    # Remplacer /api/prom/push par /api/v1/push/influx/write
    influx_url = REMOTE_WRITE_URL.replace("/api/prom/push", "/api/v1/push/influx/write")
    
    response = requests.post(  
        influx_url,
        data="\n".join(lines),
        headers={"Content-Type": "text/plain"},
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=5
    )
    
    if response.status_code not in [200, 204]:
        print(f"[PROM] Push failed: {response.status_code} - {response.text}")
    else:
        print(f"[PROM] Push OK: {len(lines)} metrics")
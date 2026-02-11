#!/usr/bin/env python
import socket
import time
import os
import sys

host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', 5432))
max_attempts = 30
timeout_seconds = 1
sleep_interval = 1

print(f"Waiting for database at {host}:{port} to be ready...", file=sys.stderr)

for attempt in range(max_attempts):
    try:
        s = socket.create_connection((host, port), timeout=timeout_seconds)
        s.close()
        print(f"Database {host}:{port} is ready after {attempt + 1} attempts.", file=sys.stderr)
        sys.exit(0)
    except (socket.error, ConnectionRefusedError):
        print(f"Attempt {attempt + 1}/{max_attempts}: {host}:{port} not yet ready. Waiting...", file=sys.stderr)
        time.sleep(sleep_interval)
    
print(f"Error: Database {host}:{port} did not become ready after {max_attempts} attempts.", file=sys.stderr)
sys.exit(1)
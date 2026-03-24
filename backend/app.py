from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import time
import os
from prometheus_client import Counter, generate_latest

app = Flask(__name__)
CORS(app)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests')

# database connection
while True:
    try:
        conn = psycopg2.connect(
             host=os.getenv("DB_HOST", "localhost"),
             database=os.getenv("DB_NAME", "tasksdb"),
             user=os.getenv("DB_USER", "postgres"),
             password=os.getenv("DB_PASSWORD", "postgres")
        )
        print("Connected to database")
        break
    except psycopg2.OperationalError:
        print("Database is not ready, retrying..")
        time.sleep(3)

@app.route("/")
def home():
    REQUEST_COUNT.inc()
    return "DevOps 3-Tier Application Running"

@app.route("/tasks", methods=["GET"])
def get_tasks():
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    cur.close()

    tasks = []
    for row in rows:
        tasks.append({"id": row[0], "task": row[1]})

    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    task = data["task"]

    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (task) VALUES (%s)", (task,))
    conn.commit()
    cur.close()

    return {"message": "Task added"}

@app.route("/metrics")
def metrics():
    return generate_latest()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# app.py — Flask API backed by PostgreSQL
from flask import Flask, request, jsonify
import os
import psycopg2               # PostgreSQL driver for Python
from psycopg2.extras import RealDictCursor   # returns rows as dicts (JSON-friendly)

app = Flask(__name__)

# --- DATABASE CONNECTION CONFIG ---
# These come from environment variables, which we'll inject via the deployment.
# Host/user/database are plain env vars; the PASSWORD comes from a Secret
# (via secretKeyRef) so it never appears in our code or git.
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "flaskapi")
DB_USER = os.environ.get("DB_USER", "flaskapi")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")   # injected from the K8s Secret


def get_connection():
    # Opens a new connection to postgres using the config above
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor,   # rows come back as dicts
    )


def init_db():
    # Runs once at startup — creates the tasks table if it doesn't exist.
    # "IF NOT EXISTS" makes this safe to run every time the app starts.
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/version")
def version():
    return jsonify({"version": "4.0.0"})   # bumped — now database-backed


# List all tasks — reads from the database
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
    tasks = cur.fetchall()      # list of dict rows
    cur.close()
    conn.close()
    return jsonify({"tasks": tasks})


# Create a task — inserts into the database
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    conn = get_connection()
    cur = conn.cursor()
    # Parameterized query (%s) — prevents SQL injection
    cur.execute(
        "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done",
        (data["title"],),
    )
    new_task = cur.fetchone()   # the row we just inserted
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(new_task), 201


# Get one task by id
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


if __name__ == "__main__":
    init_db()    # create the table on startup
    app.run(host="0.0.0.0", port=8080)

from flask import Flask, request, jsonify

app = Flask(__name__)

tasks = {}
next_id = 1


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/version")
def version():
    return jsonify({"version": "3.0.0"})


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": list(tasks.values())})


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    task = {"id": next_id, "title": data["title"], "done": False}
    tasks[next_id] = task
    next_id += 1
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

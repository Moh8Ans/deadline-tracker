from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from db import supabase
from datetime import date

app = Flask(__name__)
CORS(app)

# ── Tool 1: Add a deadline ──────────────────────────────
@app.route('/add', methods=['POST'])
def add_deadline():
    data = request.get_json()

    required = ['subject', 'task_name', 'due_date']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    row = {
        "subject":     data['subject'],
        "task_name":   data['task_name'],
        "type":        data.get('type', 'Assignment'),
        "due_date":    data['due_date'],
        "status":      "Pending",
        "source_note": data.get('source_note', ''),
    }

    result = supabase.table("deadlines").insert(row).execute()
    return jsonify({"message": "✅ Deadline saved!", "data": result.data}), 201


# ── Tool 2: List upcoming deadlines ────────────────────
@app.route('/list', methods=['GET'])
def list_deadlines():
    today = date.today().isoformat()

    result = (
        supabase.table("deadlines")
        .select("*")
        .eq("status", "Pending")
        .gte("due_date", today)
        .order("due_date", desc=False)
        .execute()
    )
    return jsonify(result.data), 200


# ── Tool 3: Mark a deadline as submitted ───────────────
@app.route('/complete/<int:deadline_id>', methods=['PATCH'])
def complete_deadline(deadline_id):
    result = (
        supabase.table("deadlines")
        .update({"status": "Submitted"})
        .eq("id", deadline_id)
        .execute()
    )
    return jsonify({"message": "✅ Marked as submitted!", "data": result.data}), 200


# ── Health check ────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "DeadlineBot API is running 🚀"}), 200
# ── Dashboard ───────────────────────────────────────────
@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')
# ── Send Digest ─────────────────────────────────────────
@app.route('/send-digest', methods=['GET'])
def send_digest_route():
    from digest import send_digest
    send_digest()
    return jsonify({"message": "✅ Digest sent!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
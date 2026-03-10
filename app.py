from pathlib import Path
from datetime import date
import os
import sqlite3

import json
from flask import Flask, render_template, redirect, url_for, session, request, flash, send_from_directory

from utils.db import init_db, execute, query_one, query_many
from utils.auth import init_app as init_auth, create_user, authenticate_user
from utils.inference import run_inference


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

# Initialise database and auth once at startup (Flask 3+ removed before_first_request)
init_db()
init_auth(app)


@app.route("/")
def home():
    # Default to login page
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = authenticate_user(email, password)
        if not user:
            flash("Invalid email or password.", "error")
            return render_template("login.html")
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        if user["role"] == "clinician":
            return redirect(url_for("clinician_dashboard"))
        return redirect(url_for("patient_portal"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role", "patient")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        try:
            create_user(email, password, role)
        except sqlite3.IntegrityError:
            flash("That email is already registered. Try logging in instead.", "error")
            return render_template("register.html")
        except Exception:
            flash("Could not create account. Please try again.", "error")
            return render_template("register.html")

        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/clinician")
def clinician_dashboard():
    if session.get("role") != "clinician":
        return redirect(url_for("login"))
    latest = query_one(
        "SELECT * FROM scans WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        [session.get("user_id")],
    )
    last_result = None
    if latest:
        row = dict(latest)
        probs = {}
        if row.get("probabilities"):
            try:
                probs = json.loads(row["probabilities"])
            except (json.JSONDecodeError, TypeError):
                pass
        fp = row.get("file_path") or ""
        file_name = Path(fp).name if fp else ""
        # Sort probabilities by value descending (top prediction first)
        probs_sorted = sorted(probs.items(), key=lambda x: -x[1]) if probs else []
        last_result = {
            "file_path": fp,
            "file_name": file_name,
            "prediction": row.get("prediction"),
            "confidence": row.get("confidence"),
            "probabilities": probs,
            "probabilities_sorted": probs_sorted,
        }
    return render_template("clinician_dashboard.html", last_result=last_result)


@app.route("/patient")
def patient_portal():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = query_one("SELECT patient_id FROM users WHERE id = ?", [session["user_id"]])
    patient_id = (dict(user) or {}).get("patient_id") or f"P-{session['user_id']}"
    scans = query_many(
        "SELECT * FROM scans WHERE patient_id = ? ORDER BY uploaded_at DESC",
        [patient_id],
    )
    reports = []
    for row in scans:
        r = dict(row)
        fp = r.get("file_path") or ""
        reports.append({
            "file_name": Path(fp).name if fp else "",
            "prediction": r.get("prediction"),
            "confidence": r.get("confidence"),
            "patient_summary": r.get("patient_summary"),
            "doctor_note": r.get("doctor_note"),
            "uploaded_at": r.get("uploaded_at"),
        })
    return render_template(
        "patient_portal.html",
        patient_id=patient_id,
        reports=reports,
        today=date.today().isoformat(),
    )


@app.route("/patient/follow-up", methods=["POST"])
def patient_follow_up():
    if "user_id" not in session:
        return redirect(url_for("login"))
    preferred_date = request.form.get("preferred_date", "").strip() or None
    preferred_time = request.form.get("preferred_time", "").strip() or None
    message = request.form.get("message", "").strip() or None
    execute(
        """
        INSERT INTO follow_up_requests (patient_user_id, preferred_date, preferred_time, message)
        VALUES (?, ?, ?, ?)
        """,
        [session["user_id"], preferred_date, preferred_time, message],
    )
    flash("Follow-up chat request submitted. Your clinician will contact you soon.", "success")
    return redirect(url_for("patient_portal"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory("uploads", filename)


@app.route("/clinician/send-results", methods=["POST"])
def clinician_send_results():
    if session.get("role") != "clinician":
        return redirect(url_for("login"))
    patient_id = request.form.get("patient_id", "").strip() or None
    patient_summary = request.form.get("patient_summary", "") or None
    doctor_note = request.form.get("doctors_note", "").strip() or None
    latest = query_one(
        "SELECT id FROM scans WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        [session.get("user_id")],
    )
    if latest:
        execute(
            "UPDATE scans SET patient_id = ?, patient_summary = ?, doctor_note = ? WHERE id = ?",
            [patient_id, patient_summary, doctor_note, latest["id"]],
        )
    flash("Results sent to patient.", "success")
    return redirect(url_for("clinician_dashboard"))


@app.route("/clinician/upload", methods=["POST"])
def clinician_upload():
    if session.get("role") != "clinician":
        return redirect(url_for("login"))
    file = request.files.get("mri_file")
    if not file:
        flash("Please upload an MRI file.", "error")
        return redirect(url_for("clinician_dashboard"))

    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    save_path = uploads_dir / file.filename
    file.save(save_path)

    label, confidence, probs_dict = run_inference(save_path)
    probs_json = json.dumps(probs_dict)

    execute(
        """
        INSERT INTO scans (user_id, file_path, prediction, confidence, probabilities)
        VALUES (?, ?, ?, ?, ?)
        """,
        [session.get("user_id"), str(save_path), label, confidence, probs_json],
    )

    flash("Analysis complete. Results are displayed below.", "success")
    return redirect(url_for("clinician_dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=8000)
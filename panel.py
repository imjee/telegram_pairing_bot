from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(_name_)
app.secret_key = "supersecret"
ADMIN_USER = "hoxibet"
ADMIN_PASS = "hoxibet11"

# Dummy data
users = {}
reports = []
rematch_queue = {}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/")
    return render_template("dashboard.html", users=users, reports=reports)

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=8080)

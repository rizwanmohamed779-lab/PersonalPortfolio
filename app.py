from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "portfolio-secret-key"


def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            technologies TEXT NOT NULL,
            github_link TEXT
        )
    """)

    project_count = connection.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    if project_count == 0:
        projects = [
            (
                "Intelligent Resume Analyzer",
                "A Python-based application that analyzes resumes and evaluates skills and candidate scores.",
                "Python, Data Analysis",
                "https://github.com/rizwanmohamed779-lab/Intelligent-Resume-Analyzer"
            ),
            (
                "Smart Agriculture AI",
                "An AI-based application for plant disease detection and intelligent agriculture predictions.",
                "Python, Machine Learning, Flask",
                ""
            ),
            (
                "Secure Banking Management System",
                "A secure banking management application using Java and MySQL.",
                "Java, MySQL, JavaFX",
                ""
            ),
            (
                "AI Prediction System",
                "A machine learning application that predicts outcomes from input data.",
                "Python, Machine Learning",
                ""
            )
        ]

        connection.executemany("""
            INSERT INTO projects
            (title, description, technologies, github_link)
            VALUES (?, ?, ?, ?)
        """, projects)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    connection = get_db_connection()

    projects = connection.execute(
        "SELECT * FROM projects"
    ).fetchall()

    connection.close()

    return render_template("index.html", projects=projects)


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    connection = get_db_connection()

    connection.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )

    connection.commit()
    connection.close()

    flash("Your message has been sent successfully!")

    return redirect(url_for("home"))

@app.route("/resume")
def resume():
    resume_folder = os.path.join(app.root_path, "resume")
    return send_from_directory(resume_folder, "resume.pdf")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
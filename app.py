from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import psycopg
import os
from psycopg.rows import dict_row

app = Flask(__name__)
app.secret_key = "portfolio-secret-key"


def get_db_connection():
    return psycopg.connect(
        os.environ["DATABASE_URL"],
        row_factory=dict_row
    )


def ensure_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            technologies TEXT NOT NULL,
            github_link TEXT
        )
    """)

    project_count = connection.execute(
        "SELECT COUNT(*) AS count FROM projects"
    ).fetchone()["count"]

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

        for project in projects:
            connection.execute("""
                INSERT INTO projects
                (title, description, technologies, github_link)
                VALUES (%s, %s, %s, %s)
            """, project)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    ensure_database()

    connection = get_db_connection()

    projects = connection.execute(
        "SELECT * FROM projects ORDER BY id"
    ).fetchall()

    connection.close()

    return render_template("index.html", projects=projects)


@app.route("/contact", methods=["POST"])
def contact():
    ensure_database()

    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    connection = get_db_connection()

    connection.execute(
        "INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)",
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
    ensure_database()
    app.run(debug=True)
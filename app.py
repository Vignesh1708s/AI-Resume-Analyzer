from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import re
import mysql.connector
import psycopg2
import os
from flask import send_from_directory

def get_db_connection():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))
app = Flask(__name__)
CORS(app)

with open("skills.txt", "r") as file:
    SKILLS = [line.strip() for line in file]

JOB_ROLES = {
    "Java Developer": ["Java", "Spring Boot", "MySQL"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript"],
    "Python Developer": ["Python", "Flask"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "Java", "MySQL"],
    "C Programmer":["c"],
    "Software Developer":["C","C++","Java"]
}



@app.route("/")
def home():
    return send_from_directory("../frontend", "front.html")
@app.route("/style.css")
def style():
    return send_from_directory("../frontend", "style.css")

@app.route("/script.js")
def script():
    return send_from_directory("../frontend", "script.js")

@app.route("/analyze", methods=["POST"])
def analyze_resume():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    reader = PdfReader(file)

    text = ""
    
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    #name extraction
    lines=text.split("\n");
    name="Not Found"
    for line in lines:
        line = line.strip()
        if len(line)>2 and len(line)<30:
            name=line
            break
    #email extraction
    # Email Extraction
    email = "Not Found"

    email_match = re.search(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    text
    )

    if email_match:
        email = email_match.group()
    #phone extraction
    phone="Not Found"

    phone_match=re.search(r"\b\d{10}\b",text)
    if phone_match:
        phone = phone_match.group()


    detected_skills = []

    resume_text = text.lower().replace(" ", "")

    for skill in SKILLS:
        if skill.lower().replace(" ", "") in resume_text:
            detected_skills.append(skill)

    score = len(detected_skills) * 10

    if score > 100:
        score = 100

    missing_skills = list(set(SKILLS) - set(detected_skills))

    recommended_jobs = []

    for role, required_skills in JOB_ROLES.items():

        match_count = 0

        for skill in required_skills:
            if skill in detected_skills:
                match_count += 1

        if match_count >= 2:
            recommended_jobs.append(role)

    feedback = []

    if score >= 80:
        strength = "Excellent 🟢"
        feedback.append("Excellent Resume")
    elif score >= 50:
        strength = "Good 🟡"
        feedback.append("Good Resume")
    elif score >=40:
        strength = "Average 🟠"
        feedback.append("Add more technical skills")
    else:
        strength = "Needs Improvement 🔴"
    if len(missing_skills) > 0:
        feedback.append("Learn more in-demand skills")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
                """
        INSERT INTO resumes
        (name, email, phone, score, strength, skills)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            email,
            phone,
            score,
            strength,
            ",".join(detected_skills)
            )
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "name":name,
        "email":email,
        "phone":phone,
        "strength": strength,
        "score": score,
        "skills": detected_skills,
        "missing_skills": missing_skills[:5],
        "jobs": recommended_jobs,
        "feedback": feedback
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
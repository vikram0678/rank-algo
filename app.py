# import mysql.connector
# import json
# from flask import Flask, request, jsonify, send_from_directory
# import pdfplumber#to extract data from pdf files
# import requests
# from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

# app = Flask(__name__)

# # MySQL database configuration
# db_config = {
#     "host": "localhost",
#     "user": "hire3x_user",
#     "password": "Hire3xSecurePass2025!",
#     "database": "hire3x"
# }

# def get_db_connection():
#     return mysql.connector.connect(**db_config)

# # Initialize the database and create tables
# conn = get_db_connection()
# cursor = conn.cursor()

# # Create the user_activity table
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS user_activity (
#         user_id INT,
#         activity_type VARCHAR(255),
#         activity_data TEXT,
#         timestamp VARCHAR(255)
#     )
# """)

# # Create the job_postings table
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS job_postings (
#         job_id INTEGER PRIMARY KEY AUTO_INCREMENT,
#         title VARCHAR(255),
#         required_skills TEXT,
#         timestamp VARCHAR(255)
#     )
# """)
# conn.commit()
# conn.close()

# # DeepSeek API configuration
# # DEEPSEEK_API_KEY = "sk-f9d4ff4dd7204a45a5ce2723502f1b5a"
# # DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"/
# # Headers for DeepSeek API
# headers = {
#     "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
#     "Content-Type": "application/json"
# }

# # Extract text from PDF
# def extract_text_from_pdf(pdf_file):
#     with pdfplumber.open(pdf_file) as pdf:
#         return "".join(page.extract_text() or "" for page in pdf.pages)

# # Analyze resume with DeepSeek
# def analyze_resume_with_deepseek(resume_text):
#     try:
#         payload = {
#             "model": "deepseek/deepseek-r1:free",
#             "messages": [
#                 {"role": "system", "content": "You are a resume parser. Extract all technical skills and total years of experience from the resume text. Return the result in this format: 'Skills: skill1, skill2, skill3; Experience: X years'. If no skills or experience are found, return 'Skills: None; Experience: 0 years'."},
#                 {"role": "user", "content": resume_text}
#             ],
#             "max_tokens": 200
#         }
#         response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
#         response.raise_for_status()
#         result = response.json()["choices"][0]["message"]["content"]
#         skills_part = result.split("Skills:")[1].split(";")[0].strip()
#         experience_part = result.split("Experience:")[1].strip()
#         skills = [s.strip() for s in skills_part.split(",")] if skills_part != "None" else []
#         experience_years = int(experience_part.split()[0]) if experience_part != "0 years" else 0
#         return {"skills": skills, "experience_years": experience_years}
#     except Exception as e:
#         print(f"Error analyzing resume with DeepSeek: {e}")
#         return {"skills": [], "experience_years": 0}

# # Endpoint for resume upload
# @app.route("/upload_resume", methods=["POST"])
# def upload_resume():
#     user_id = request.form["user_id"]
#     # Validate user_id as an integer
#     try:
#         user_id = int(user_id)
#     except ValueError:
#         return jsonify({"status": "error", "message": "User ID must be an integer (e.g., 1)"}), 400

#     if "resume" not in request.files:
#         return jsonify({"status": "error", "message": "No file uploaded"}), 400
#     resume_file = request.files["resume"]
#     if not resume_file.filename.endswith(".pdf"):
#         return jsonify({"status": "error", "message": "Must be PDF"}), 400
#     resume_text = extract_text_from_pdf(resume_file)
#     resume_data = analyze_resume_with_deepseek(resume_text)
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     for skill in resume_data["skills"]:
#         cursor.execute("INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
#             (user_id, "skill_added", json.dumps({"skill": skill}), "2025-03-07"))
#     cursor.execute("INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
#             (user_id, "experience_added", json.dumps({"years": resume_data["experience_years"]}), "2025-03-07"))
#     conn.commit()
#     conn.close()
#     return jsonify({"status": "success", "skills": resume_data["skills"], "experience": resume_data["experience_years"]})

# # Endpoint for manual entry (candidates)
# @app.route("/add_manual", methods=["POST"])
# def add_manual():
#     user_id = request.form["user_id"]
#     # Validate user_id as an integer
#     try:
#         user_id = int(user_id)
#     except ValueError:
#         return jsonify({"status": "error", "message": "User ID must be an integer (e.g., 1)"}), 400

#     skills = request.form["skills"].split(",")
#     try:
#         experience_years = int(request.form["experience"])
#     except ValueError:
#         return jsonify({"status": "error", "message": "Experience must be an integer (e.g., 3)"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     for skill in [s.strip() for s in skills if s.strip()]:
#         cursor.execute("INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
#             (user_id, "skill_added", json.dumps({"skill": skill}), "2025-03-07"))
#     cursor.execute("INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
#             (user_id, "experience_added", json.dumps({"years": experience_years}), "2025-03-07"))
#     conn.commit()
#     conn.close()
#     return jsonify({"status": "success", "skills": skills, "experience": experience_years})

# # Endpoint to add a job posting
# @app.route("/add_job", methods=["POST"])
# def add_job():
#     title = request.form["title"]
#     required_skills = request.form["required_skills"]
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO job_postings (title, required_skills, timestamp) VALUES (%s, %s, %s)",
#                 (title, required_skills, "2025-03-07"))
#     conn.commit()
#     conn.close()
#     return jsonify({"status": "success", "title": title, "required_skills": required_skills})

# # Check skill similarity using DeepSeek
# def get_skill_similarity(skill1, skill2):
#     try:
#         payload = {
#             "model": "deepseek-r1",
#             "messages": [
#                 {"role": "system", "content": "You are a skill comparison tool. Compare two skills and return a similarity score between 0 and 1, where 1 means identical and 0 means unrelated. Return only the number (e.g., 0.85)."},
#                 {"role": "user", "content": f"Compare '{skill1}' and '{skill2}'"}
#             ],
#             "max_tokens": 10
#         }
#         response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
#         response.raise_for_status()
#         return float(response.json()["choices"][0]["message"]["content"])
#     except Exception as e:
#         print(f"Error in skill similarity: {e}")
#         return 0

# # Calculate user score with relevance filter
# def calculate_score(user_id, searched_skills):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'skill_added'", (user_id,))
#     user_skills = [json.loads(row[0])["skill"] for row in cursor.fetchall()]
#     cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'experience_added'", (user_id,))
#     experience = sum([json.loads(row[0])["years"] for row in cursor.fetchall()])
#     conn.close()
    
#     score = 0
#     has_relevant_skill = False
#     for search_skill in searched_skills:
#         for user_skill in user_skills:
#             similarity = get_skill_similarity(search_skill, user_skill)
#             if similarity > 0.7:
#                 has_relevant_skill = True
#                 score += 10 * similarity
#             elif search_skill.lower() == user_skill.lower():
#                 has_relevant_skill = True
#                 score += 10
    
#     if not has_relevant_skill:
#         return 0
    
#     score += experience * 2
#     return round(score, 2)

# # Summarize candidate data using DeepSeek
# def summarize_candidate(user_id, searched_skills):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'skill_added'", (user_id,))
#     skills = [json.loads(row[0])["skill"] for row in cursor.fetchall()]
#     cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'experience_added'", (user_id,))
#     experience = sum([json.loads(row[0])["years"] for row in cursor.fetchall()])
#     conn.close()
#     skill_text = ", ".join(skills) if skills else "None"
#     try:
#         payload = {
#             "model": "deepseek-r1",
#             "messages": [
#                 {"role": "system", "content": "You are a hiring assistant. Summarize a candidate’s profile based on their skills, experience, and relevance to the searched skills. Highlight if they have team management skills."},
#                 {"role": "user", "content": f"Candidate has skills: {skill_text}, experience: {experience} years. Searched skills: {', '.join(searched_skills)}."}
#             ],
#             "max_tokens": 200
#         }
#         response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]
#     except Exception as e:
#         print(f"Error summarizing candidate: {e}")
#         return f"User {user_id} has {experience} years of experience with skills: {skill_text}."

# # Endpoint to rank users (only relevant candidates)
# @app.route("/rank_users", methods=["GET"])
# def rank_users():
#     job_id = request.args.get("job_id", None)
#     query = request.args.get("skills", "")
    
#     if job_id:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT required_skills FROM job_postings WHERE job_id = %s", (job_id,))
#         job = cursor.fetchone()
#         conn.close()
#         if not job:
#             return jsonify({"message": "Job not found"}), 404
#         searched_skills = job[0].split(",")
#     else:
#         if not query:
#             return jsonify({"message": "Please enter a search query or job ID"}), 400
#         searched_skills = query.split(",")

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT DISTINCT user_id FROM user_activity")
#     users = cursor.fetchall()
#     conn.close()
#     if not users:
#         return jsonify({"message": "No candidates found"}), 404

#     ranked = []
#     for user in users:
#         user_id = user[0]
#         score = calculate_score(user_id, searched_skills)
#         if score > 0:
#             conn = get_db_connection()
#             cursor = conn.cursor()
#             cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'skill_added'", (user_id,))
#             user_skills = [json.loads(row[0])["skill"] for row in cursor.fetchall()]
#             conn.close()
#             summary = summarize_candidate(user_id, searched_skills)
#             ranked.append({
#                 "user_id": user_id,
#                 "score": score,
#                 "skills": user_skills,
#                 "summary": summary
#             })
    
#     if not ranked:
#         return jsonify({"message": "No candidates found with relevant skills"}), 404
    
#     ranked.sort(key=lambda x: x["score"], reverse=True)
#     return jsonify(ranked)

# # Serve the frontend
# @app.route("/")
# def serve_index():
#     return send_from_directory(".", "index.html")

# @app.route("/static/<path:path>")
# def serve_static(path):
#     return send_from_directory("static", path)

# if __name__ == "__main__":
#     app.run(debug=True)



# .....................................................................................................................

# app.py
from flask import Flask, request, jsonify, send_from_directory
import json
from database import initialize_database, get_db_connection
from resume_parser import extract_text_from_pdf, analyze_resume_with_deepseek
from skill_processor import calculate_score, summarize_candidate, get_skill_similarity

app = Flask(__name__)

# Initialize the database when the app starts
initialize_database()

# Endpoint for resume upload
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    user_id = request.form["user_id"]
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"status": "error", "message": "User ID must be an integer (e.g., 1)"}), 400

    if "resume" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    resume_file = request.files["resume"]
    if not resume_file.filename.endswith(".pdf"):
        return jsonify({"status": "error", "message": "Must be PDF"}), 400
    resume_text = extract_text_from_pdf(resume_file)
    resume_data = analyze_resume_with_deepseek(resume_text)
    conn = get_db_connection()
    cursor = conn.cursor()
    for skill in resume_data["skills"]:
        cursor.execute("INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
                        (user_id, "skill_added", json.dumps({"skill": skill}), "2025-03-07"))
    cursor.execute("INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
                    (user_id, "experience_added", json.dumps({"years": resume_data["experience_years"]}), "2025-03-07"))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "skills": resume_data["skills"], "experience": resume_data["experience_years"]})

# Endpoint for manual entry (candidates)
@app.route("/add_manual", methods=["POST"])
def add_manual():
    user_id = request.form["user_id"]
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"status": "error", "message": "User ID must be an integer (e.g., 1)"}), 400
    
    skills = request.form["skills"].split(",")
    try:
        experience_years = int(request.form["experience"])
    except ValueError:
        return jsonify({"status": "error", "message": "Experience must be an integer (e.g., 3)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    for skill in [s.strip() for s in skills if s.strip()]:
        cursor.execute("INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
                        (user_id, "skill_added", json.dumps({"skill": skill}), "2025-03-07"))
    cursor.execute("INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
                    (user_id, "experience_added", json.dumps({"years": experience_years}), "2025-03-07"))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "skills": skills, "experience": experience_years})

# Endpoint to add a job posting
@app.route("/add_job", methods=["POST"])
def add_job():
    title = request.form["title"]
    required_skills = request.form["required_skills"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO job_postings (title, required_skills, timestamp) VALUES (%s, %s, %s)",
                    (title, required_skills, "2025-03-07"))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "title": title, "required_skills": required_skills})

# Endpoint to rank users (only relevant candidates)
@app.route("/rank_users", methods=["GET"])
def rank_users():
    job_id = request.args.get("job_id", None)
    query = request.args.get("skills", "")
    
    if job_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT required_skills FROM job_postings WHERE job_id = %s", (job_id,))
        job = cursor.fetchone()
        conn.close()
        if not job:
            return jsonify({"message": "Job not found"}), 404
        searched_skills = job[0].split(",")
    else:
        if not query:
            return jsonify({"message": "Please enter a search query or job ID"}), 400
        searched_skills = query.split(",")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM user_activity")
    users = cursor.fetchall()
    conn.close()
    if not users:
        return jsonify({"message": "No candidates found"}), 404

    ranked = []
    for user in users:
        user_id = user[0]
        score = calculate_score(user_id, searched_skills)
        if score > 0:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'skill_added'", (user_id,))
            user_skills = [json.loads(row[0])["skill"] for row in cursor.fetchall()]
            conn.close()
            summary = summarize_candidate(user_id, searched_skills)
            ranked.append({
                "user_id": user_id,
                "score": score,
                "skills": user_skills,
                "summary": summary
            })
    
    if not ranked:
        return jsonify({"message": "No candidates found with relevant skills"}), 404
    
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(ranked)

# Serve the frontend
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(debug=True)
# skill_processor.py
import json
import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL
from database import get_db_connection



headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}


def get_skill_similarity(skill1, skill2):
    try:
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {"role": "system", "content": "You are a skill comparison tool. Compare two skills and return a similarity score between 0 and 1, where 1 means identical and 0 means unrelated. Return only the number (e.g., 0.85)."},
                {"role": "user", "content": f"Compare '{skill1}' and '{skill2}'"}
            ],
            "max_tokens": 10
        }
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        # return float(response.json()["choices"][0]["message"]["content"])
        content = response.json()["choices"][0]["message"]["content"].strip()
        if not content or not content.replace('.', '').isdigit():
            return 0  # Return 0 if content is empty or not a number
        return float(content)
    except Exception as e:
        print(f"Error in skill similarity: {e}")
        return 0

def calculate_score(user_id, searched_skills):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'skill_added'", (user_id,))
    user_skills = [json.loads(row[0])["skill"] for row in cursor.fetchall()]
    cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'experience_added'", (user_id,))
    experience = sum([json.loads(row[0])["years"] for row in cursor.fetchall()])
    conn.close()
    
    score = 0
    has_relevant_skill = False
    for search_skill in searched_skills:
        for user_skill in user_skills:
            similarity = get_skill_similarity(search_skill, user_skill)
            if similarity > 0.7:
                has_relevant_skill = True
                score += 10 * similarity
            elif search_skill.lower() == user_skill.lower():
                has_relevant_skill = True
                score += 10
    
    if not has_relevant_skill:
        return 0
    
    score += experience * 2
    return round(score, 2)

def summarize_candidate(user_id, searched_skills):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'skill_added'", (user_id,))
    skills = [json.loads(row[0])["skill"] for row in cursor.fetchall()]
    cursor.execute("SELECT activity_data FROM user_activity WHERE user_id = %s AND activity_type = 'experience_added'", (user_id,))
    experience = sum([json.loads(row[0])["years"] for row in cursor.fetchall()])
    conn.close()
    skill_text = ", ".join(skills) if skills else "None"
    try:
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {"role": "system", "content": "You are a hiring assistant. Summarize a candidate’s profile based on their skills, experience, and relevance to the searched skills. Highlight if they have team management skills."},
                {"role": "user", "content": f"Candidate has skills: {skill_text}, experience: {experience} years. Searched skills: {', '.join(searched_skills)}."}
            ],
            "max_tokens": 200
        }
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        summary= response.json()["choices"][0]["message"]["content"].replace("*","")
        print(f"Debug - Summary from AI: {summary}")
        return summary
    except Exception as e:
        print(f"Error summarizing candidate: {e}")
        return f"User {user_id} has {experience} years of experience with skills: {skill_text}."
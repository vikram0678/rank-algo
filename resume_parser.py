# resume_parser.py
import pdfplumber
import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "".join(page.extract_text() or "" for page in pdf.pages)

def analyze_resume_with_deepseek(resume_text):
    try:
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {"role": "system", "content": "You are a resume parser. Extract all technical skills and total years of experience from the resume text. Return the result in this format: 'Skills: skill1, skill2, skill3; Experience: X years'. If no skills or experience are found, return 'Skills: None; Experience: 0 years'."},
                {"role": "user", "content": resume_text}
            ],
            "max_tokens": 200
        }
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        skills_part = result.split("Skills:")[1].split(";")[0].strip()
        experience_part = result.split("Experience:")[1].strip()
        skills = [s.strip() for s in skills_part.split(",")] if skills_part != "None" else []
        experience_years = int(experience_part.split()[0]) if experience_part != "0 years" else 0
        return {"skills": skills, "experience_years": experience_years}
    except Exception as e:
        print(f"Error analyzing resume with DeepSeek: {e}")
        return {"skills": [], "experience_years": 0}
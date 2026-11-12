import re
from pypdf import PdfReader

# 1. Read PDF function (NEW!)
def read_pdf_resume(file_name):
    try:
        reader = PdfReader(file_name)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# 2. Clean text
def clean_text(raw_text):
    text = raw_text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

# 3. Match skills
def match_skills(resume_text, required_skills):
    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill in resume_text:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    score = (len(matched_skills) / len(required_skills)) * 100
    return score, matched_skills, missing_skills

# 4. Generate recommendation
def generate_recommendation(score, missing_skills):
    if score >= 80:
        return "Strong Match: Highly recommended for interview!"
    elif score >= 50:
        missing_str = ", ".join(missing_skills)
        return f"Moderate Match: Consider interviewing, but candidate needs to learn: {missing_str}"
    else:
        return "Low Match: Candidate does not meet the core requirements."


# ==========================================
# TESTING OUR REAL PDF RESUME
# ==========================================

# Read from the real PDF!
raw_resume = read_pdf_resume("resume.pdf")
cleaned_resume = clean_text(raw_resume)

# Pick any 3 skills you know are (or aren't) in your PDF:
required_skills = ["python", "sql", "communication"]

score, matched, missing = match_skills(cleaned_resume, required_skills)
recommendation = generate_recommendation(score, missing)

print("\n====================================")
print("     REAL PDF SCREENING REPORT      ")
print("====================================")
print(f"Match Score   : {round(score, 1)}%")
print(f"Matched Skills: {matched}")
print(f"Missing Skills: {missing}")
print(f"Recommendation: {recommendation}")
print("====================================\n")
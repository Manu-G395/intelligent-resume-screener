import streamlit as st
import re
from pypdf import PdfReader

# Page Setup
st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="centered")

st.title("Intelligent Resume Screening & Job-Fit Platform")
st.write("Upload a candidate's resume and specify required skills to check job-fit.")

# ----------------- OUR HELPER FUNCTIONS -----------------

def extract_text_from_file(uploaded_file):
    """Extracts text whether the user uploads a PDF or a TXT file."""
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
    return text

def clean_text(raw_text):
    text = raw_text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def match_skills(resume_text, required_skills):
    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill.strip().lower() in resume_text:
            matched_skills.append(skill.strip())
        else:
            missing_skills.append(skill.strip())

    if len(required_skills) > 0:
        score = (len(matched_skills) / len(required_skills)) * 100
    else:
        score = 0.0

    return score, matched_skills, missing_skills

def generate_recommendation(score, missing_skills):
    if score >= 80:
        return "Strong Match: Highly recommended for interview!"
    elif score >= 50:
        missing_str = ", ".join(missing_skills)
        return f"Moderate Match: Consider interviewing, but candidate needs to learn: {missing_str}"
    else:
        return "Low Match: Candidate does not meet the core requirements."

# ----------------- WEB USER INTERFACE -----------------

# 1. File Upload Box
uploaded_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])

# 2. Input Box for Skills
skills_input = st.text_input(
    "Enter required job skills (separated by commas):",
    "Python, SQL, Git, Docker"
)

# 3. Action Button
if st.button("🔍 Screen Resume"):
    if uploaded_file is None:
        st.warning("Please upload a resume file first!")
    else:
        with st.spinner("Analyzing resume..."):
            raw_text = extract_text_from_file(uploaded_file)
            cleaned_text = clean_text(raw_text)

            skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]

            score, matched, missing = match_skills(cleaned_text, skills_list)
            recommendation = generate_recommendation(score, missing)

            st.divider()
            st.subheader("Candidate Evaluation")

            # Match Score
            st.metric(label="Job-Fit Match Score", value=f"{round(score, 1)}%")

            # Matched & Missing Columns with clean bullets
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"**Matched Skills ({len(matched)}):**")
                if matched:
                    for skill in matched:
                        st.write(f"{skill}")
                else:
                    st.write("None")

            with col2:
                st.error(f"**Missing Skills ({len(missing)}):**")
                if missing:
                    for skill in missing:
                        st.write(f"{skill}")
                else:
                    st.write("None")

            # Final Recommendation Card
            st.info(f"**Recommendation:**\n\n{recommendation}")
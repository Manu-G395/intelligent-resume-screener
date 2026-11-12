import streamlit as st
import re
from pypdf import PdfReader
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Page Setup
st.set_page_config(page_title="AI Resume Screener Enterprise", page_icon="📄", layout="wide")

st.title("Intelligent Resume Screening & Job-Fit Platform (Enterprise)")
st.write("Enterprise ATS: Featuring **PDF/DOCX Parsing**, **Skill Synonyms**, **Section-Wise Scoring**, and **TF-IDF Semantic Analysis**.")

# ----------------- 1. SKILL TAXONOMY & SYNONYMS -----------------
SYNONYM_MAP = {
    "ml": ["machine learning", "ml"],
    "machine learning": ["ml", "machine learning"],
    "ai": ["artificial intelligence", "ai"],
    "artificial intelligence": ["ai", "artificial intelligence"],
    "js": ["javascript", "js"],
    "javascript": ["js", "javascript"],
    "ts": ["typescript", "ts"],
    "typescript": ["ts", "typescript"],
    "py": ["python", "py"],
    "python": ["py", "python"],
    "react": ["reactjs", "react.js", "react"],
    "node": ["nodejs", "node.js", "node"],
    "k8s": ["kubernetes", "k8s"],
    "kubernetes": ["k8s", "kubernetes"],
    "aws": ["amazon web services", "aws"],
    "nlp": ["natural language processing", "nlp"],
    "db": ["database", "sql", "db"]
}

# ----------------- 2. FILE EXTRACTION (PDF, DOCX, TXT) -----------------

def extract_text_from_file(uploaded_file):
    """Extracts text from PDF, DOCX, or TXT."""
    text = ""
    filename = uploaded_file.name.lower()
    
    if filename.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif filename.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        text = "\n".join([p.text for p in doc.paragraphs if p.text])
    elif filename.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
        
    return text

def clean_text(raw_text):
    """Standardizes text to lowercase and removes punctuation."""
    text = raw_text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text

# ----------------- 3. SKILL & SEMANTIC MATCHING -----------------

def is_skill_present(skill, text):
    """Checks for the skill AND any of its known synonyms/abbreviations."""
    skill_clean = skill.strip().lower()
    aliases = SYNONYM_MAP.get(skill_clean, [skill_clean])
    for alias in aliases:
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text):
            return True
    return False

def evaluate_skill_group(required_skills, resume_text):
    """Evaluates skills against the resume using synonyms."""
    matched = []
    missing = []
    for skill in required_skills:
        clean_s = skill.strip()
        if not clean_s:
            continue
        if is_skill_present(clean_s, resume_text):
            matched.append(clean_s)
        else:
            missing.append(clean_s)
    
    score = (len(matched) / len(required_skills) * 100) if required_skills else 100.0
    return round(score, 1), matched, missing

def calculate_tfidf_similarity(resume_text, job_desc_text):
    """Calculates semantic match using TF-IDF and Cosine Similarity."""
    text_list = [resume_text, job_desc_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(text_list)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 1)

# ----------------- 4. SECTION-WISE ANALYSIS -----------------

def analyze_sections(resume_text, skill_score, semantic_score):
    """Evaluates the 4 core pillars: Skills, Experience, Education, Projects."""
    
    # 1. Experience Keywords
    exp_keywords = ["experience", "worked", "developer", "engineer", "developed", "managed", "led", "responsibilities", "built"]
    found_exp = [k for k in exp_keywords if k in resume_text]
    exp_score = min(100.0, round((len(found_exp) / 5) * 100 * 0.6 + (semantic_score * 0.4), 1))
    
    # 2. Education Keywords
    edu_keywords = ["education", "bachelor", "btech", "degree", "university", "college", "master", "gpa", "academic", "institute"]
    found_edu = [k for k in edu_keywords if k in resume_text]
    edu_score = 100.0 if len(found_edu) >= 2 else (50.0 if len(found_edu) == 1 else 0.0)
    
    # 3. Projects Keywords
    proj_keywords = ["project", "projects", "implemented", "github", "application", "created", "designed"]
    found_proj = [k for k in proj_keywords if k in resume_text]
    proj_score = min(100.0, round((len(found_proj) / 3) * 100, 1))

    # Overall Section-Weighted Score (Skills 40%, Experience 30%, Education 15%, Projects 15%)
    section_score = round(
        (skill_score * 0.40) +
        (exp_score * 0.30) +
        (edu_score * 0.15) +
        (proj_score * 0.15),
        1
    )
    
    return {
        "overall": section_score,
        "skills": skill_score,
        "experience": exp_score,
        "education": edu_score,
        "projects": proj_score
    }

# ----------------- 5. USER INTERFACE -----------------

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. Candidate Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

with col_right:
    st.subheader("2. Job Requirements")
    job_desc_input = st.text_area(
        "Job Description (for TF-IDF Context Match):",
        "Looking for a Backend Python Developer to build APIs and machine learning pipelines with SQL and Git. Must have Bachelor's degree and hands-on projects.",
        height=100
    )

st.divider()
st.subheader("3. Skill Weighting (Must-Have vs. Nice-to-Have)")

s1, s2 = st.columns(2)
with s1:
    must_have_input = st.text_input("Must-Have Skills (70% Weight - Mandatory):", "Python, SQL, ML")
with s2:
    nice_to_have_input = st.text_input("Nice-to-Have Skills (30% Weight - Bonus):", "Docker, AWS, Git")

if st.button("🚀 Run Comprehensive Enterprise Screening"):
    if not uploaded_file:
        st.warning("Please upload a resume first!")
    else:
        with st.spinner("Analyzing candidate across all sections..."):
            raw_resume = extract_text_from_file(uploaded_file)
            cleaned_resume = clean_text(raw_resume)
            cleaned_jd = clean_text(job_desc_input)

            # Skill matching
            must_have_list = [s.strip() for s in must_have_input.split(",") if s.strip()]
            nice_to_have_list = [s.strip() for s in nice_to_have_input.split(",") if s.strip()]

            must_score, must_matched, must_missing = evaluate_skill_group(must_have_list, cleaned_resume)
            nice_score, nice_matched, nice_missing = evaluate_skill_group(nice_to_have_list, cleaned_resume)

            # Weighted Skill Score
            weighted_skill_score = round((must_score * 0.70) + (nice_score * 0.30), 1)

            # TF-IDF Semantic Match
            semantic_score = calculate_tfidf_similarity(cleaned_resume, cleaned_jd)

            # Section-Wise Scoring
            sections = analyze_sections(cleaned_resume, weighted_skill_score, semantic_score)
            final_score = sections["overall"]

            # ----------------- DISPLAY RESULTS -----------------
            st.divider()
            st.header("Candidate Evaluation Dashboard")

            # Big Metric Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Overall Fit Score", f"{final_score}%")
            m2.metric("Weighted Skills", f"{weighted_skill_score}%")
            m3.metric("Experience Alignment", f"{sections['experience']}%")
            m4.metric("TF-IDF Semantic", f"{semantic_score}%")

            # Section-Wise Scoring Cards
            st.subheader("Section-Wise Score Breakdown")
            sec1, sec2, sec3, sec4 = st.columns(4)
            sec1.info(f"**Skills Section (40% wt)**\n\n### {sections['skills']}%")
            sec2.info(f"**Experience (30% wt)**\n\n### {sections['experience']}%")
            sec3.info(f"**Education (15% wt)**\n\n### {sections['education']}%")
            sec4.info(f"**Projects (15% wt)**\n\n### {sections['projects']}%")

            # Explainable Formula
            with st.expander("**Explainable Score Breakdown (Mathematical Formula)**", expanded=True):
                st.markdown(f"""
                - **Skills Section (40% wt):** `{sections['skills']}%` × 0.40 = **`{round(sections['skills'] * 0.40, 1)} pts`**
                - **Experience Section (30% wt):** `{sections['experience']}%` × 0.30 = **`{round(sections['experience'] * 0.30, 1)} pts`**
                - **Education Section (15% wt):** `{sections['education']}%` × 0.15 = **`{round(sections['education'] * 0.15, 1)} pts`**
                - **Projects Section (15% wt):** `{sections['projects']}%` × 0.15 = **`{round(sections['projects'] * 0.15, 1)} pts`**
                - **Final Composite Formula:** `({round(sections['skills'] * 0.40, 1)}) + ({round(sections['experience'] * 0.30, 1)}) + ({round(sections['education'] * 0.15, 1)}) + ({round(sections['projects'] * 0.15, 1)}) = {final_score}%`
                """)

            # Skill Highlights
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Must-Have Skills")
                for s in must_matched:
                    st.success(f"**{s}** (Matched via exact name or synonym)")
                for s in must_missing:
                    st.error(f"**{s}** (Missing)")

            with c2:
                st.subheader("Nice-to-Have Skills")
                for s in nice_matched:
                    st.success(f"**{s}** (Bonus Matched)")
                for s in nice_missing:
                    st.warning(f"**{s}** (Optional - Not Found)")

            # Final Advice
            st.subheader("Strategic Hiring Advice")
            if final_score >= 70:
                st.success("**Strong Candidate:** Strong section alignment and high skill match. Recommended for technical interview.")
            elif final_score >= 45:
                st.info("**Moderate Candidate:** Meets basic requirements, but has gaps in some sections or bonus competencies.")
            else:
                st.error("**Low Match:** Candidate does not meet core requirements for this position.")
import streamlit as st
import re
import pandas as pd
from collections import Counter
from pypdf import PdfReader
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Page Setup
st.set_page_config(page_title="AI Enterprise ATS & Career Platform", page_icon="📄", layout="wide")

st.title("AI-Powered Intelligent Resume & Career Platform")
st.write("Enterprise Solution: Featuring **Bulk Screening**, **Leaderboard Rankings**, **ATS Auditing**, and **Career Roadmaps**.")

# ----------------- 1. TAXONOMY & SYNONYMS -----------------
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

LEARNING_RESOURCES = {
    "docker": {
        "level": "Foundational DevOps",
        "resource": "Docker for Beginners (FreeCodeCamp / Official Docs)",
        "duration": "1-2 Weeks",
        "action": "Containerize a simple Python script and push the image to Docker Hub."
    },
    "aws": {
        "level": "Cloud Infrastructure",
        "resource": "AWS Cloud Practitioner Essentials (Free on AWS Skill Builder)",
        "duration": "2-3 Weeks",
        "action": "Deploy a simple app on EC2 and store a file in S3."
    },
    "kubernetes": {
        "level": "Advanced Container Orchestration",
        "resource": "Kubernetes Crash Course (TechWorld with Nana - YouTube)",
        "duration": "2-3 Weeks",
        "action": "Deploy a multi-pod cluster locally using Minikube."
    },
    "sql": {
        "level": "Core Data Management",
        "resource": "SQL Tutorial for Beginners (Mode Analytics / SQLBolt)",
        "duration": "1 Week",
        "action": "Write complex queries using JOINs, GROUP BY, and aggregate functions."
    },
    "git": {
        "level": "Essential Version Control",
        "resource": "Git & GitHub Crash Course (FreeCodeCamp)",
        "duration": "3-5 Days",
        "action": "Create branches, resolve merge conflicts, and submit a pull request."
    },
    "ml": {
        "level": "Data Science & AI",
        "resource": "Machine Learning Specialization (Andrew Ng / Coursera Free Audit)",
        "duration": "4-6 Weeks",
        "action": "Build and train a regression and classification model using scikit-learn."
    }
}

# ----------------- 2. EXTRACTION & CLEANING -----------------

def extract_text_from_file(uploaded_file):
    text = ""
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif filename.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs if p.text])
        elif filename.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
    except Exception as e:
        text = f"Error reading file: {e}"
    return text

def clean_text(raw_text):
    text = raw_text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text

def is_skill_present(skill, text):
    skill_clean = skill.strip().lower()
    aliases = SYNONYM_MAP.get(skill_clean, [skill_clean])
    for alias in aliases:
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text):
            return True
    return False

def evaluate_skill_group(required_skills, resume_text):
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
    text_list = [resume_text, job_desc_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(text_list)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 1)

def analyze_sections(resume_text, skill_score, semantic_score):
    exp_keywords = ["experience", "worked", "developer", "engineer", "developed", "managed", "led", "responsibilities", "built"]
    found_exp = [k for k in exp_keywords if k in resume_text]
    exp_score = min(100.0, round((len(found_exp) / 5) * 100 * 0.6 + (semantic_score * 0.4), 1))
    
    edu_keywords = ["education", "bachelor", "btech", "degree", "university", "college", "master", "gpa", "academic", "institute"]
    found_edu = [k for k in edu_keywords if k in resume_text]
    edu_score = 100.0 if len(found_edu) >= 2 else (50.0 if len(found_edu) == 1 else 0.0)
    
    proj_keywords = ["project", "projects", "implemented", "github", "application", "created", "designed"]
    found_proj = [k for k in proj_keywords if k in resume_text]
    proj_score = min(100.0, round((len(found_proj) / 3) * 100, 1))

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

def check_ats_friendliness(raw_text):
    text_lower = raw_text.lower()
    words = raw_text.split()
    word_count = len(words)
    
    if word_count < 200:
        length_status = "Too brief (< 200 words). Add more details."
        length_score = 50
    elif word_count > 1200:
        length_status = "Very long (> 1,200 words). Condense to 1-2 pages."
        length_score = 70
    else:
        length_status = f"Optimal resume length ({word_count} words)."
        length_score = 100

    sections = {
        "Skills": ["skill", "technologies", "competencies"],
        "Experience": ["experience", "work", "employment", "history"],
        "Education": ["education", "academic", "degree", "university", "college"],
        "Projects": ["project", "projects", "portfolio"]
    }
    found_sections = [s for s, kws in sections.items() if any(k in text_lower for k in kws)]
    missing_sections = [s for s in sections.keys() if s not in found_sections]
    section_score = (len(found_sections) / len(sections)) * 100

    weak_phrases = ["responsible for", "helped with", "worked on", "assisted in", "tasked with", "handled"]
    strong_verbs = ["developed", "engineered", "automated", "spearheaded", "optimized", "designed", "implemented", "built", "orchestrated"]
    
    detected_weak = [p for p in weak_phrases if p in text_lower]
    detected_strong = [v for v in strong_verbs if v in text_lower]

    ats_score = round((length_score * 0.25) + (section_score * 0.50) + (min(len(detected_strong) * 10, 100) * 0.25), 1)

    return {
        "ats_score": ats_score,
        "word_count": word_count,
        "length_status": length_status,
        "found_sections": found_sections,
        "missing_sections": missing_sections,
        "detected_weak": detected_weak,
        "detected_strong": detected_strong
    }

def get_missing_keywords(resume_text, job_desc_text):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=25)
    vectorizer.fit([job_desc_text])
    top_jd_words = vectorizer.get_feature_names_out()
    missing_keywords = [w for w in top_jd_words if w not in resume_text and len(w) > 2]
    return missing_keywords[:8]

def rewrite_bullet_point(bullet_text):
    cleaned = bullet_text.strip()
    return [
        f"**Formula-Driven:** Engineered and deployed an end-to-end solution for {cleaned}, boosting execution efficiency by 30% and reducing manual effort.",
        f"**Metric-Focused:** Automated core processes related to {cleaned}, improving system reliability and achieving a 25% decrease in operational errors."
    ]

# ----------------- 3. NAVIGATION TABS -----------------

tab_bulk, tab_single, tab_candidate = st.tabs([
    "Bulk Screening & Leaderboard", 
    "Single Resume Deep-Dive", 
    "Candidate Career Coach & ATS Optimizer"
])

# ==========================================
# TAB 1: BULK SCREENING & LEADERBOARD
# ==========================================
with tab_bulk:
    st.header("Bulk Candidate Screening & Ranked Leaderboard")
    st.write("Upload **multiple resumes (PDF, DOCX, TXT)** at once to generate a ranked leaderboard, apply filters, view charts, and export results.")

    b_col1, b_col2 = st.columns([1, 1])
    with b_col1:
        bulk_files = st.file_uploader(
            "Upload Batch of Resumes (Select multiple files):", 
            type=["pdf", "docx", "txt"], 
            accept_multiple_files=True,
            key="bulk_uploader"
        )
    with b_col2:
        bulk_jd = st.text_area(
            "Target Job Description:",
            "Looking for a Backend Python Developer to build APIs and machine learning pipelines with SQL and Git. Must have Bachelor's degree and hands-on projects.",
            height=100,
            key="bulk_jd"
        )

    b_s1, b_s2 = st.columns(2)
    with b_s1:
        bulk_must = st.text_input("Must-Have Skills (70% Wt):", "Python, SQL, ML", key="bulk_must")
    with b_s2:
        bulk_nice = st.text_input("Nice-to-Have Skills (30% Wt):", "Docker, AWS, Git", key="bulk_nice")

    if st.button("Screen Batch & Generate Leaderboard", key="btn_bulk"):
        if not bulk_files:
            st.warning("Please upload at least one resume file!")
        else:
            with st.spinner(f"Screening {len(bulk_files)} resumes against the Job Description..."):
                cleaned_jd = clean_text(bulk_jd)
                must_list = [s.strip() for s in bulk_must.split(",") if s.strip()]
                nice_list = [s.strip() for s in bulk_nice.split(",") if s.strip()]

                all_candidates = []
                all_missing_skills = []

                progress_bar = st.progress(0)
                for idx, file in enumerate(bulk_files):
                    raw_text = extract_text_from_file(file)
                    clean_res = clean_text(raw_text)

                    m_score, m_matched, m_missing = evaluate_skill_group(must_list, clean_res)
                    n_score, n_matched, n_missing = evaluate_skill_group(nice_list, clean_res)
                    weighted_skill = round((m_score * 0.70) + (n_score * 0.30), 1)
                    sem_score = calculate_tfidf_similarity(clean_res, cleaned_jd)

                    sections = analyze_sections(clean_res, weighted_skill, sem_score)
                    final_fit = sections["overall"]

                    all_missing_skills.extend(m_missing + n_missing)

                    # Recommendation label
                    if final_fit >= 70:
                        rec = "Strong Match"
                    elif final_fit >= 45:
                        rec = "Moderate Match"
                    else:
                        rec = "Low Match"

                    all_candidates.append({
                        "Rank": 0,
                        "Candidate File": file.name,
                        "Overall Fit Score (%)": final_fit,
                        "Skills Score (%)": weighted_skill,
                        "Experience (%)": sections["experience"],
                        "Education (%)": sections["education"],
                        "Projects (%)": sections["projects"],
                        "Matched Skills": ", ".join(m_matched + n_matched) if (m_matched + n_matched) else "None",
                        "Missing Skills": ", ".join(m_missing + n_missing) if (m_missing + n_missing) else "None",
                        "Recommendation": rec
                    })
                    progress_bar.progress((idx + 1) / len(bulk_files))

                # Save in session state so filters work interactively
                df_results = pd.DataFrame(all_candidates).sort_values(by="Overall Fit Score (%)", ascending=False).reset_index(drop=True)
                df_results["Rank"] = [f"#{i+1}" for i in range(len(df_results))]
                st.session_state["bulk_df"] = df_results
                st.session_state["all_missing_skills"] = all_missing_skills

    # Display Leaderboard if data exists
    if "bulk_df" in st.session_state:
        df = st.session_state["bulk_df"]

        st.divider()
        st.subheader("Ranked Candidate Leaderboard")

        # Filters
        f1, f2 = st.columns([1, 1])
        with f1:
            min_score = st.slider("Filter by Minimum Overall Fit Score (%):", 0, 100, 40)
        with f2:
            export_name = st.text_input("CSV Export Filename:", "shortlisted_candidates.csv")

        filtered_df = df[df["Overall Fit Score (%)"] >= min_score]

        st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** candidates meeting criteria:")
        st.dataframe(filtered_df, use_container_width=True)

        # Export CSV Button
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Shortlist as CSV",
            data=csv_bytes,
            file_name=export_name,
            mime="text/csv",
            key="download_csv"
        )

        # Dashboard Analytics Charts
        st.divider()
        st.subheader("Recruiter Analytics & Charts")

        chart_c1, chart_c2 = st.columns(2)
        with chart_c1:
            st.write("**Candidate Score Distribution:**")
            score_chart_data = filtered_df[["Candidate File", "Overall Fit Score (%)"]].set_index("Candidate File")
            st.bar_chart(score_chart_data)

        with chart_c2:
            st.write("**Most Common Missing Skills Across Candidates:**")
            if st.session_state.get("all_missing_skills"):
                missing_counts = Counter(st.session_state["all_missing_skills"])
                missing_df = pd.DataFrame(missing_counts.most_common(6), columns=["Skill", "Count"]).set_index("Skill")
                st.bar_chart(missing_df)
            else:
                st.write("No missing skills recorded!")


# ==========================================
# TAB 2: SINGLE RESUME DEEP-DIVE
# ==========================================
with tab_single:
    st.header("Single Candidate Deep-Dive Screener")
    col_left, col_right = st.columns([1, 1])
    with col_left:
        uploaded_file = st.file_uploader("Upload Resume:", type=["pdf", "docx", "txt"], key="single_file")
    with col_right:
        job_desc_input = st.text_area("Job Description:", "Backend Python Developer with SQL, Git, and ML.", height=100, key="single_jd")

    s1, s2 = st.columns(2)
    with s1:
        must_have_input = st.text_input("Must-Have Skills (70% Wt):", "Python, SQL, ML", key="single_must")
    with s2:
        nice_to_have_input = st.text_input("Nice-to-Have Skills (30% Wt):", "Docker, AWS, Git", key="single_nice")

    if st.button("Run Deep-Dive Screening", key="btn_single"):
        if not uploaded_file:
            st.warning("Please upload a resume!")
        else:
            raw_resume = extract_text_from_file(uploaded_file)
            cleaned_resume = clean_text(raw_resume)
            cleaned_jd = clean_text(job_desc_input)

            must_have_list = [s.strip() for s in must_have_input.split(",") if s.strip()]
            nice_to_have_list = [s.strip() for s in nice_to_have_input.split(",") if s.strip()]

            must_score, must_matched, must_missing = evaluate_skill_group(must_have_list, cleaned_resume)
            nice_score, nice_matched, nice_missing = evaluate_skill_group(nice_to_have_list, cleaned_resume)

            weighted_skill_score = round((must_score * 0.70) + (nice_score * 0.30), 1)
            semantic_score = calculate_tfidf_similarity(cleaned_resume, cleaned_jd)

            sections = analyze_sections(cleaned_resume, weighted_skill_score, semantic_score)
            final_score = sections["overall"]

            st.divider()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Overall Fit Score", f"{final_score}%")
            m2.metric("Weighted Skills", f"{weighted_skill_score}%")
            m3.metric("Experience", f"{sections['experience']}%")
            m4.metric("TF-IDF Semantic", f"{semantic_score}%")

            st.subheader("Section-Wise Score Breakdown")
            sec1, sec2, sec3, sec4 = st.columns(4)
            sec1.info(f"**Skills Section (40%)**\n\n### {sections['skills']}%")
            sec2.info(f"**Experience (30%)**\n\n### {sections['experience']}%")
            sec3.info(f"**Education (15%)**\n\n### {sections['education']}%")
            sec4.info(f"**Projects (15%)**\n\n### {sections['projects']}%")


# ==========================================
# TAB 3: CANDIDATE CAREER COACH
# ==========================================
with tab_candidate:
    st.header("Candidate Career Coach & ATS Diagnostic")
    cand_file = st.file_uploader("Upload Your Resume to Audit:", type=["pdf", "docx", "txt"], key="cand_file")
    cand_target_jd = st.text_area("Target Job Description:", "Python Developer with SQL, Docker, and AWS.", height=80, key="cand_jd")

    if st.button("Run Candidate Diagnostics", key="btn_cand"):
        if not cand_file:
            st.warning("Please upload your resume!")
        else:
            raw_cand_text = extract_text_from_file(cand_file)
            cleaned_cand_text = clean_text(raw_cand_text)
            ats_audit = check_ats_friendliness(raw_cand_text)

            st.divider()
            col_score, col_status = st.columns([1, 2])
            with col_score:
                st.metric("ATS Health Score", f"{ats_audit['ats_score']} / 100")
            with col_status:
                st.write(f"**Word Count:** {ats_audit['length_status']}")

            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.write("**Detected Standard Sections:**")
                for s in ats_audit["found_sections"]:
                    st.success(f"{s}")
            with s_col2:
                st.write("**Missing Recommended Sections:**")
                for s in ats_audit["missing_sections"]:
                    st.error(f"{s}")

            st.divider()
            st.subheader("High-Impact Keywords Missing in Your Resume")
            if cand_target_jd.strip():
                missing_kws = get_missing_keywords(cleaned_cand_text, clean_text(cand_target_jd))
                if missing_kws:
                    st.info(" • " + "   •   ".join([f"**{kw.upper()}**" for kw in missing_kws]))

            st.divider()
            st.subheader("Personalized Skill Gap Learning Roadmap")
            skills_to_audit = ["docker", "aws", "kubernetes", "sql", "git", "ml"]
            missing_learning_skills = [s for s in skills_to_audit if not is_skill_present(s, cleaned_cand_text)]
            for s in missing_learning_skills:
                info = LEARNING_RESOURCES.get(s)
                if info:
                    with st.expander(f"Learn {s.upper()} — {info['level']} ({info['duration']})", expanded=True):
                        st.markdown(f"* **Resource:** {info['resource']}\n* **Hands-on Milestone:** {info['action']}")

    st.divider()
    st.subheader("AI Resume Bullet Point Rewriter (Google X-Y-Z Formula)")
    sample_bullet = st.text_input("Paste a weak bullet point to rewrite:", "worked on building python backend apis and fixed bugs")
    if st.button("Optimize Bullet Point", key="btn_rewrite"):
        if sample_bullet.strip():
            options = rewrite_bullet_point(sample_bullet)
            st.success("Here are two optimized versions with metrics:")
            for opt in options:
                st.markdown(opt)
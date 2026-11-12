# 📄 AI-Powered Intelligent Resume & Career Platform (Enterprise ATS)

An end-to-end, two-sided intelligent platform designed for **Recruiters** (bulk screening, ranked leaderboards, semantic matching) and **Candidates** (ATS health audit, keyword gap analysis, career roadmap).

---

## 🚀 Key Features

### 👔 1. Recruiter Suite
- **Bulk Screening & Leaderboard:** Upload 50+ resumes simultaneously (PDF, DOCX, TXT) and view a real-time ranked candidate leaderboard.
- **Section-Wise Scoring:** Multi-factor weighted evaluation across Skills (40%), Experience (30%), Education (15%), and Projects (15%).
- **Weighted Skill Heuristics:** Distinguishes between Must-Have (70% weight) and Nice-to-Have (30% weight) competencies.
- **Skill Taxonomy & Synonyms:** Normalizes industry abbreviations (e.g., `ML` ↔ `Machine Learning`, `JS` ↔ `JavaScript`, `K8s` ↔ `Kubernetes`).
- **TF-IDF Semantic Matching:** Statistical NLP measuring overall document context using `scikit-learn` and Cosine Similarity.
- **Interactive Filters & CSV Export:** Filter candidates by minimum score thresholds and export shortlists to CSV with one click.
- **Visual Analytics:** Real-time charts showing score distribution and the most common skill gaps across applicants.

### 👤 2. Candidate Career Coach
- **ATS-Friendliness Audit:** Checks word count health, verifies standard section headings, and flags weak passive phrases in favor of strong power verbs.
- **Missing Keyword Suggestions:** Identifies high-priority terms from the Job Description omitted in the resume.
- **30-Day Skill Gap Learning Roadmap:** Recommends curated free resources (Coursera, FreeCodeCamp, AWS Skill Builder) with structured milestones for missing skills.
- **AI Bullet Point Rewriter:** Optimizes duty statements into high-impact, metrics-driven bullets using the Google X-Y-Z formula.

---

## 🛠️ Tech Stack
- **Language:** Python
- **Natural Language Processing & ML:** `scikit-learn` (TF-IDF Vectorizer, Cosine Similarity), `re` (Regex)
- **Document Parsing:** `pypdf` (PDF), `python-docx` (DOCX), UTF-8 text
- **Data & Visual Analytics:** `pandas`, Streamlit Native Charts
- **Web Framework:** `streamlit`

---

## 💻 How to Run Locally

1. Clone repository:
   ```bash
   git clone https://github.com/Manu-G395/intelligent-resume-screener.git
   cd intelligent-resume-screener
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch application:
   ```bash
   streamlit run app.py
   ```
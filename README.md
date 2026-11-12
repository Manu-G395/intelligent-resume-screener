# 📄 Intelligent Resume Screening & Job-Fit Recommendation Platform

An intelligent Python-based Applicant Tracking System (ATS) that evaluates candidate resumes against required job skills and provides hiring recommendations.

## 🚀 Features
- **Multi-Format Support:** Extracts text from both PDF and TXT resumes.
- **Text Preprocessing:** Cleans raw text by standardizing to lowercase and removing punctuation/symbols using Regex.
- **Skill Gap Analysis:** Accurately identifies matched and missing candidate skills.
- **Job-Fit Recommendation Engine:** Categorizes candidates (Strong, Moderate, Low Match) and highlights missing skills to improve hiring decisions.
- **Interactive Web Dashboard:** Clean, user-friendly UI built with Streamlit.

## 🛠️ Tech Stack
- **Language:** Python
- **Text & PDF Processing:** `pypdf`, `re` (Regular Expressions)
- **Web Interface:** `streamlit`

## 💻 How to Run Locally

1. Clone this repository:
   ```bash
   git clone <YOUR_REPOSITORY_LINK>
   cd resume_screening_platform
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the web application:
   ```bash
   streamlit run app.py
   ```
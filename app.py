import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Streamlit Page Config
st.set_page_config(page_title="AI Resume Screener", layout="wide")

# Custom CSS for UI Styling
st.markdown("""
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #e0f7fa, #c2e9fb);
        }
        .css-1aumxhk {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .stButton>button {
            background: linear-gradient(to right, #4fc3f7, #29b6f6);
            border: none;
            color: white;
            padding: 12px 25px;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.2s ease-in-out;
        }
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
    </style>
""", unsafe_allow_html=True)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text
    return text

# Function to rank resumes
def rank_resumes(job_description, resumes):
    documents = [job_description] + resumes
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()

    # Calculate cosine similarity
    job_description_vector = vectors[0]
    resume_vectors = vectors[1:]
    cosine_similarities = cosine_similarity([job_description_vector], resume_vectors).flatten()

    return cosine_similarities

# UI Layout
st.title("🤖 AI Resume Screening & Ranking")
st.markdown("Upload resumes and provide a job description to rank the resumes based on relevance.")

# Job Description Input
job_description = st.text_area("📌 Paste Job Description Here", height=200)

# File Upload
uploaded_files = st.file_uploader("📂 Upload Resumes (PDFs Only)", type=['pdf'], accept_multiple_files=True)

# Process Button
if st.button("🚀 Process Resumes"):
    if not job_description:
        st.error("⚠️ Please enter a job description!")
    elif not uploaded_files:
        st.error("⚠️ Please upload at least one resume!")
    else:
        resumes = []
        resume_names = []

        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            resumes.append(text)
            resume_names.append(file.name)

        # Rank resumes
        scores = rank_resumes(job_description, resumes)

        # Prepare results
        results = [{"Resume": name, "Score": round(float(score) * 100, 2)} for name, score in zip(resume_names, scores)]
        results = sorted(results, key=lambda x: x["Score"], reverse=True)

        # Show Results
        st.subheader("📊 Resume Ranking Results")
        df = pd.DataFrame(results)
        st.table(df)
import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

#page configuration
st.set_page_config(
    page_title="AI Resume Critiquer",
    page_icon="📃",
    layout="centered"
)

# csssssss
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, rgba(186,85,255,0.25), rgba(255,105,180,0.25));
            background-size: cover;
        }
        

        h1, h2, h3 {
            font-weight: 800;
            background: linear-gradient(to right, #C56FFF, #FF73B9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stButton>button {
            background: linear-gradient(135deg, #C56FFF, #FF73B9);
            color: white;
            padding: 0.8rem 1.2rem;
            border-radius: 12px;
            border: none;
            font-size: 1rem;
            font-weight: 600;
            transition: 0.2s ease-in-out;
        }

        .stButton>button:hover {
            transform: scale(1.03);
            background: linear-gradient(135deg, #b34aff, #ff4fad);
        }

        .stTextInput>div>div>input {
            background: rgba(255,255,255,0.35);
            border-radius: 10px;
        }

        .stFileUploader {
            background: rgba(255,255,255,0.35);
            padding: 10px;
            border-radius: 12px;
        }

        .stSelectbox>div>div {
            background: rgba(255,255,255,0.35);
            border-radius: 12px;
        }

        .result-box {
            background: rgba(255,255,255,0.40);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            border: 1px solid rgba(255,255,255,0.4);
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.header("📃 AI Resume Critiquer")
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt"])
    job_role = st.text_input("Enter job role (optional)")

    tone = st.selectbox(
        "Choose the tone of the review",
        ["Professional & Polite", "Funny Roast 🤪"]
    )

    analyze = st.button("✨ Analyze Resume ✨")

st.markdown('</div>', unsafe_allow_html=True)

#pdf extraction
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")


#analyzeeee
if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File has no readable content.")
            st.stop()

        # Tone instructions
        if tone == "Professional & Polite":
            tone_instruction = "Give a polite, professional, structured HR-style review."
        else:
            tone_instruction = "Give a FUNNY, light-hearted roast of the resume. Use humor and playful sarcasm but stay respectful, helpful and constructive."

        # Prompt for full review + ATS score
        prompt = f"""
        You are an expert resume evaluator and an ATS system.

        Tone: {tone_instruction}

        TASKS:
        1. Provide a detailed resume critique.
        2. Evaluate skills, experience clarity, formatting, and relevance to {job_role if job_role else "general roles"}.
        3. Provide concrete suggestions.
        4. Generate an ATS Score from 0 to 100 based on keyword match, formatting, clarity, skills alignment, and relevance.

        Resume:
        {file_content}

        Return your response in this structure:

        ### 🔥 Main Review
        (Your review in the selected tone)

        ### 📌 Key Improvements
        - bullet points...

        ### 🎯 ATS Score
        A number from 0–100 with one sentence explanation.
        """

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        with st.spinner("Analyzing your resume... ✨"):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional ATS and resume expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )

        # Display result
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown("### 🔍 Analysis Results")
        st.markdown(response.choices[0].message.content)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

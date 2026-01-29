import streamlit as st
import cv2
import numpy as np
import easyocr
from sentence_transformers import SentenceTransformer, util
from PIL import Image


# ---------------------------------------------------
# MODEL LOADING

# ---------------------------------------------------
@st.cache_resource
def load_models():
    reader = easyocr.Reader(['en'], gpu=False)
    grader = SentenceTransformer('all-MiniLM-L6-v2')
    return reader, grader

reader, grader_model = load_models()


# ---------------------------------------------------
# HANDWRITING PREPROCESSING
# ---------------------------------------------------
def preprocess_for_handwriting(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Noise reduction
    gray = cv2.fastNlMeansDenoising(gray, None, 20, 7, 21)

    # Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # Stroke strengthening
    kernel = np.ones((2,2), np.uint8)
    thick = cv2.dilate(enhanced, kernel, iterations=1)

    return thick


# ---------------------------------------------------
# HANDWRITING OCR PIPELINE
# ---------------------------------------------------
def extract_handwritten_text(image):
    processed = preprocess_for_handwriting(image)

    # Try processed
    result1 = reader.readtext(processed, detail=0, paragraph=True)
    # Try raw
    result2 = reader.readtext(np.array(image), detail=0, paragraph=True)

    t1 = " ".join(result1) if result1 else ""
    t2 = " ".join(result2) if result2 else ""

    # pick the longer text
    return t1 if len(t1) > len(t2) else t2


# ---------------------------------------------------
# GRADING SYSTEM (KEY POINT SIMILARITY)
# ---------------------------------------------------
def grade_key_points(student_text, key_points):
    student_sentences = student_text.split('.')
    student_emb = grader_model.encode(student_sentences, convert_to_tensor=True)

    found = []
    missing = []
    score = 0

    for point in key_points:
        if not point.strip():
            continue

        point_emb = grader_model.encode(point, convert_to_tensor=True)
        sims = util.pytorch_cos_sim(point_emb, student_emb)[0]
        best_match = float(max(sims)) * 100

        if best_match > 55:  # similarity threshold
            found.append(f"✅ {point} ({best_match:.1f}%)")
            score += 1
        else:
            missing.append(f"❌ {point}")

    final_score = (score / len(key_points)) * 100 if key_points else 0
    return final_score, found, missing


# ---------------------------------------------------
# MAIN GRADER FUNCTION (USED BY LOGIN)
# ---------------------------------------------------
def main_grader_app():
    st.title("📚 AI Handwritten Answer Grader")

    # ---- Sidebar (teacher rubric + logout) ----
    with st.sidebar:
        st.header("Teacher Rubric")
        rubric = st.text_area("Enter expected key points (one per line):", height=250)
        key_points = [line.strip() for line in rubric.split("\n") if line.strip()]

        if st.button("Logout"):
            st.session_state.password_correct = False
            st.session_state.view = "login"
            st.rerun()

    # ---- Student submission ----
    uploaded = st.file_uploader("Upload handwritten pages", type=["png","jpg","jpeg"], accept_multiple_files=True)

    if uploaded and key_points:
        collected = ""

        with st.spinner("Reading handwriting..."):
            for file in uploaded:
                img = Image.open(file)
                collected += extract_handwritten_text(img) + " "

        # ---- Display extracted text ----
        st.subheader("📖 Extracted Text")
        st.info(collected)

        # ---- Grade using key points ----
        final_score, found, missing = grade_key_points(collected, key_points)

        st.subheader("📊 Evaluation Result")
        st.metric("Final Score", f"{final_score:.1f}%")

        col1, col2 = st.columns(2)
        with col1:
            st.write("### 🟩 Points Covered")
            for p in found:
                st.success(p)

        with col2:
            st.write("### 🟥 Points Missing")
            for p in missing:
                st.error(p)


# ---------------------------------------------------
# DIRECT EXECUTION SUPPORT
# ---------------------------------------------------
if __name__ == "__main__":
    main_grader_app()

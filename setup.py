print("--- STARTING DOWNLOAD ---")

print("1. Downloading EasyOCR Model...")
import easyocr
# This forces the download now
reader = easyocr.Reader(['en'], gpu=False)
print("✅ EasyOCR Ready!")

print("2. Downloading Grading Model...")
from sentence_transformers import SentenceTransformer
# This forces the download now
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Grading Model Ready!")

print("--- ALL DONE! NOW RUN STREAMLIT ---")
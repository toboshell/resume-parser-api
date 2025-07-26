import re
import spacy
from spacy.matcher import Matcher
from pdfminer.high_level import extract_text as extract_pdf
from docx import Document

def extract_text_from_file(path):
    if path.endswith(".pdf"):
        return extract_pdf(path)
    elif path.endswith(".docx"):
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return ""

def extract_name(text):
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    patterns = [[{'POS': 'PROPN'}, {'POS': 'PROPN'}]]
    for pattern in patterns:
        matcher.add('NAME', patterns=[pattern])
    doc = nlp(text)
    matches = matcher(doc)
    for match_id, start, end in matches:
        return doc[start:end].text
    return None

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group() if match else None

def extract_phone(text):
    match = re.search(r"(\+91)?[\s\-]?[6-9]\d{9}", text)
    return match.group() if match else None

def extract_linkedin(text):
    match = re.search(r"linkedin\.com/in/[\w\-]+", text)
    return match.group() if match else None

def extract_location(text):
    match = re.search(r"Bengaluru|Karnataka|Delhi|Mumbai", text, re.IGNORECASE)
    return match.group() if match else None

def extract_section(text, start, end):
    match = re.search(fr"{start}(.*?){end}", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return []

    lines = match.group(1).split('\n')
    cleaned = []

    for line in lines:
        # Remove leading/trailing bullets and symbols
        line = line.strip().lstrip("•·*-•").strip()
        # Ignore empty lines or lines that are just bullets
        if line and not re.fullmatch(r'[•·*-]+', line):
            cleaned.append(line)

    return cleaned

def parse_resume(path):
    text = extract_text_from_file(path)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "location": extract_location(text),
        "skills": extract_section(text, "SKILLS", "EDUCATION"),
        "education": extract_section(text, "EDUCATION", "PROJECTS"),
        "experience": extract_section(text, "PROFESSIONAL EXPERIENCE", "INTERNSHIP"),
        "internships": extract_section(text, "INTERNSHIP", "SKILLS"),
        "projects_and_certifications": extract_section(text, "PROJECTS & CERTIFICATIONS", "$")
    }

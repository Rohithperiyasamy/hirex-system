"""
Hirex - AI Utilities
Supports Google Gemini API
Configured via AI_PROVIDER in settings / .env
"""

import os
import fitz          # PyMuPDF
import requests
import re

from django.conf import settings


def ai_response(prompt: str) -> str:
    from google import genai
    from google.genai import types

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return "I'm sorry, the AI service is currently unavailable."

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # ← disables thinking, saves 5-15s
                max_output_tokens=300,   # ← interview questions don't need more
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        print(f"[Hirex AI] Failed: {e}")
        return "I'm sorry, the AI service is currently unavailable."
    
    
# ── INTERVIEW QUESTION GENERATION ────────────────────────────────
def generate(name, job_description, participant_info, level, role, transcript_chat, transcript):
    """Generate the next interview question using AI."""
    prompt = (
        f"You are a professional technical interviewer at a top tech company.\n"
        f"Candidate name: {name}\n"
        f"Applying for: {role} (Experience level: {level})\n"
        f"Job Description: {job_description}\n"
        f"Resume Summary: {participant_info}\n"
        f"Previous conversation: {transcript_chat}\n"
        f"Candidate just said: \"{transcript}\"\n\n"
        f"Ask exactly ONE follow-up technical interview question based on their last answer and resume. "
        f"Do not repeat previously asked questions. "
        f"Do not introduce yourself or explain what you are doing. "
        f"If the candidate is being rude or unprofessional, politely ask them to maintain professional conduct. "
        f"Output only the question — nothing else."
    )
    return ai_response(prompt)


# ── PDF / RESUME PARSING ──────────────────────────────────────────
def convert_to_direct_download_link(google_drive_link: str) -> str:
    """Convert a Google Drive shared link to a direct download link."""
    match = re.search(r"\/d\/(.*?)(?:\/|$)", google_drive_link)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    raise ValueError("Invalid Google Drive link format.")


def pdf_ocr(url: str) -> str:
    """Download PDF from URL (supports Google Drive links) and extract text."""
    try:
        if "drive.google.com" in url:
            url = convert_to_direct_download_link(url)

        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"[Hirex PDF] Failed to fetch PDF — HTTP {response.status_code}")
            return "Resume not available."

        pdf_document = fitz.open("pdf", response.content)
        text = ""
        for page in pdf_document:
            text += page.get_text()
        pdf_document.close()
        print(f"[Hirex PDF] Extracted {len(text)} characters from resume.")
        return text if text.strip() else "Resume content could not be extracted."

    except Exception as e:
        print(f"[Hirex PDF] Error: {e}")
        return "Resume parsing failed."


# ── EVALUATION ────────────────────────────────────────────────────
REQUIRED_SKILLS = [
    "python", "java", "c++", "javascript", "typescript", "react", "vue", "angular",
    "node.js", "django", "flask", "sql", "mysql", "postgresql", "mongodb",
    "html", "css", "git", "docker", "kubernetes", "aws", "azure", "gcp",
    "machine learning", "deep learning", "api", "rest", "graphql", "linux"
]
NICE_TO_HAVE = [
    "next.js", "nuxt", "jest", "cypress", "redis", "kafka", "spark",
    "tensorflow", "pytorch", "nlp", "opencv", "fastapi", "celery"
]


def evaluation(transcript_data: dict) -> dict:
    """
    Evaluate a candidate based on their interview transcripts.
    Returns a dict with accuracy, communication, technical_depth, good_fit,
    strengths, and weaknesses.
    """
    transcripts = transcript_data.get("transcripts", [])

    # ── AI-generated strengths / weaknesses ─────────────────────
    eval_prompt = (
        f"Evaluate this technical interview transcript and give exactly:\n"
        f"- 3 bullet points under 'Strengths:'\n"
        f"- 3 bullet points under 'Weaknesses:'\n\n"
        f"Transcript (each item: 'transcript' = candidate answer, 'response' = interviewer question):\n"
        f"{transcripts}\n\n"
        f"Format strictly as:\nStrengths:\n- point1\n- point2\n- point3\n"
        f"Weaknesses:\n- point1\n- point2\n- point3\n"
        f"Output only these 8 lines — nothing else."
    )

    raw = ai_response(eval_prompt)
    print(f"[Hirex Eval] Raw AI output:\n{raw}")

    strengths, weaknesses = [], []
    current_section = None
    for line in raw.split('\n'):
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if 'strengths' in lower:
            current_section = 'strengths'
            continue
        elif 'weaknesses' in lower or 'weakness' in lower:
            current_section = 'weaknesses'
            continue
        if current_section and (
            line.startswith('-') or line.startswith('*') or
            (line[0].isdigit() and len(line) > 1 and line[1] in '.)')
        ):
            clean = re.sub(r'^[-*\d.)\s]+', '', line).strip()
            clean = re.sub(r'\*\*(.*?)\*\*', r'\1', clean)
            if clean:
                if current_section == 'strengths':
                    strengths.append(clean)
                else:
                    weaknesses.append(clean)

    # ── Scoring metrics ──────────────────────────────────────────
    accuracy_scores        = []
    communication_scores   = []
    technical_depth_scores = []
    good_fit_keywords      = set()
    all_skills             = REQUIRED_SKILLS + NICE_TO_HAVE

    for qa in transcripts:
        candidate_ans = qa.get("transcript", "").lower()
        interviewer_q = qa.get("response", "").lower()

        q_words = set(interviewer_q.split())
        a_words = set(candidate_ans.split())
        overlap = len(q_words & a_words)
        relevance_score = min(100, int((overlap / max(len(q_words), 1)) * 200))
        if len(candidate_ans.split()) > 15:
            relevance_score = max(relevance_score, 60)
        accuracy_scores.append(relevance_score)

        word_count = len(candidate_ans.split())
        if word_count <= 3:
            communication_scores.append("Low")
        elif word_count <= 12:
            communication_scores.append("Medium")
        else:
            communication_scores.append("High")

        matched = sum(1 for s in all_skills if s in candidate_ans)
        if matched >= 3:
            technical_depth_scores.append("High")
        elif matched >= 1:
            technical_depth_scores.append("Medium")
        else:
            technical_depth_scores.append("Low")

        for skill in all_skills:
            if skill in candidate_ans:
                good_fit_keywords.add(skill)

    avg_accuracy      = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
    avg_communication = max(set(communication_scores), key=communication_scores.count) if communication_scores else "Low"
    avg_tech_depth    = max(set(technical_depth_scores), key=technical_depth_scores.count) if technical_depth_scores else "Low"
    is_good_fit       = len(good_fit_keywords) >= 3

    return {
        "accuracy":        f"{avg_accuracy:.0f}%",
        "communication":   avg_communication,
        "technical_depth": avg_tech_depth,
        "good_fit":        "Yes" if is_good_fit else "No",
        "strengths":       "\n".join(strengths[:3]),
        "weaknesses":      "\n".join(weaknesses[:3]),
    }
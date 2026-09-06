import json
import requests
from decouple import config


def get_gemini_api_key():
    return config('GEMINI_API_KEY', default=config('VITE_GEMINI_API_KEY', default=''))


def call_gemini_api(prompt: str, system_instruction: str = None) -> str:
    """
    Executes a server-side call to Google Gemini REST API.
    Uses gemini-2.5-flash or gemini-1.5-flash.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return json.dumps({
            "error": "Gemini API key is not configured in .env",
            "mock": True
        })

    # Try gemini-2.5-flash, fallback to gemini-1.5-flash
    models = ["gemini-2.5-flash", "gemini-1.5-flash"]
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048,
        }
    }
    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    return json.dumps(data)
            elif response.status_code in [400, 403, 404]:
                continue
        except Exception as e:
            continue

    return json.dumps({
        "status": "completed",
        "message": "AI service offline or rate-limited. Fallback response generated.",
        "fallback": True
    })


def generate_curriculum_service(course_name: str, category: str, target_audience: str = "General", duration: str = "3 Months"):
    prompt = f"""
    Act as the Chief Academic Architect of ILA Global (International Learning Alliance).
    Generate a comprehensive, accredited enterprise syllabus and training curriculum in valid JSON format.
    Course Name: {course_name}
    Category: {category}
    Target Audience: {target_audience}
    Duration: {duration}

    Return ONLY a valid JSON object matching this schema:
    {{
      "course_name": "{course_name}",
      "headline": "...",
      "overview": "...",
      "modules": [
        {{
          "module_number": 1,
          "title": "...",
          "hours": 20,
          "topics": ["topic 1", "topic 2"],
          "exercises": ["drill 1", "drill 2"]
        }}
      ],
      "teaching_methodology": "...",
      "certification_standard": "..."
    }}
    """
    return call_gemini_api(prompt, "You are an expert curriculum designer. Output raw JSON only.")


def check_eligibility_service(profile: dict):
    prompt = f"""
    Act as a senior European Immigration & German Academic Compliance Evaluator for ILA Global.
    Evaluate the following candidate profile for German Opportunities (Chancenkarte / University Admission / Ausbildung / Job Placement):
    {json.dumps(profile, indent=2)}

    Calculate their exact score out of 100, determine their eligibility status, points breakdown, and a step-by-step action plan.
    Return ONLY a valid JSON object:
    {{
      "eligibility_score": 85,
      "status": "Highly Eligible / Eligible / Needs Improvement",
      "recommended_path": "Chancenkarte / APS Direct Admission / Dual-Vocational Ausbildung",
      "points_breakdown": {{
        "education": "...",
        "language": "...",
        "work_experience": "...",
        "age": "..."
      }},
      "action_plan": [
        "Step 1: ...",
        "Step 2: ..."
      ]
    }}
    """
    return call_gemini_api(prompt, "You are a German immigration compliance auditor. Output raw JSON only.")


def classroom_tutor_service(question: str, course_context: str = "", history: list = None):
    history_str = json.dumps(history) if history else "None"
    prompt = f"""
    You are Intelli-Coach, the premier AI Academic Mentor and Classroom Assistant for ILA Global.
    Course Context: {course_context}
    Student Conversation History: {history_str}
    Student's Current Query: {question}

    Provide a warm, highly clear, pedagoically structured answer with practical examples and pronunciation/grammar/code tips where relevant.
    """
    return call_gemini_api(prompt, "You are Intelli-Coach, an expert international tutor.")


def parse_resume_service(resume_text: str):
    prompt = f"""
    Extract structured candidate data and provide a professional character and suitability analysis for this resume:
    {resume_text[:4000]}

    Return ONLY a valid JSON object:
    {{
      "name": "...",
      "email": "...",
      "phone": "...",
      "skills": ["..."],
      "experience_years": 0,
      "suitability_score": 85,
      "recommended_position": "...",
      "character_analysis": "..."
    }}
    """
    return call_gemini_api(prompt, "You are an expert HR recruitment evaluator. Output raw JSON only.")

import os
import re
import json
import logging
from django.db import models
from django.db.models import Q, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    Country,
    College,
    StudyAbroadCourse,
    StudentApplication,
    DocumentChecklist,
    ConsultantATSTask,
    HybridAILog,
    CountryTieUpCategory,
)
from .serializers import (
    CountrySerializer,
    CollegeSerializer,
    StudyAbroadCourseSerializer,
    StudentPrivacyCourseViewSerializer,
    StudentApplicationSerializer,
    DocumentChecklistSerializer,
    ConsultantATSTaskSerializer,
    HybridAILogSerializer,
    CountryTieUpCategorySerializer,
    ResumeParsedDataSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Standard CRUD ViewSets
# ---------------------------------------------------------------------------

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.annotate(colleges_count=Count("colleges")).all().order_by("-created_at")
    serializer_class = CountrySerializer


class CollegeViewSet(viewsets.ModelViewSet):
    queryset = College.objects.select_related("country").annotate(courses_count=Count("courses")).all().order_by("-created_at")
    serializer_class = CollegeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        country_id = self.request.query_params.get("country_id")
        if country_id:
            qs = qs.filter(country_id=country_id)
        return qs


class StudyAbroadCourseViewSet(viewsets.ModelViewSet):
    queryset = StudyAbroadCourse.objects.select_related("college", "country").all().order_by("-created_at")
    serializer_class = StudyAbroadCourseSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        country_id = self.request.query_params.get("country_id")
        degree = self.request.query_params.get("degree")
        if country_id:
            qs = qs.filter(country_id=country_id)
        if degree:
            qs = qs.filter(degree=degree)
        return qs

    @action(detail=False, methods=["get"], url_path="public-browse")
    def public_browse(self, request):
        courses = self.get_queryset()
        serializer = StudentPrivacyCourseViewSerializer(courses, many=True)
        return Response(serializer.data)


class StudentApplicationViewSet(viewsets.ModelViewSet):
    queryset = StudentApplication.objects.select_related("target_country", "assigned_college", "matched_course").all().order_by("-created_at")
    serializer_class = StudentApplicationSerializer

    @action(detail=True, methods=["post"], url_path="toggle-college-reveal")
    def toggle_college_reveal(self, request, pk=None):
        application = self.get_object()
        reveal = request.data.get("reveal", not application.is_college_revealed)
        application.is_college_revealed = reveal
        if reveal and application.status in ["Submitted", "Matched", "Under Review"]:
            application.status = "College Approved"
        application.save()
        return Response(
            {
                "success": True,
                "is_college_revealed": application.is_college_revealed,
                "status": application.status,
                "assigned_college_name": application.assigned_college.name if application.assigned_college else None,
            }
        )


class DocumentChecklistViewSet(viewsets.ModelViewSet):
    queryset = DocumentChecklist.objects.all().order_by("country", "course_track")
    serializer_class = DocumentChecklistSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        country = self.request.query_params.get("country")
        course_track = self.request.query_params.get("course_track")
        if country and country != "All":
            qs = qs.filter(country__iexact=country)
        if course_track and course_track != "All":
            qs = qs.filter(course_track__iexact=course_track)
        return qs


class ConsultantATSTaskViewSet(viewsets.ModelViewSet):
    queryset = ConsultantATSTask.objects.prefetch_related("hybrid_logs").all().order_by("-updated_at")
    serializer_class = ConsultantATSTaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        stage = self.request.query_params.get("stage")
        search = self.request.query_params.get("search")
        if stage and stage != "All":
            qs = qs.filter(stage=stage)
        if search:
            qs = qs.filter(
                Q(student_name__icontains=search)
                | Q(student_email__icontains=search)
                | Q(target_course__icontains=search)
            )
        return qs

    @action(detail=True, methods=["post"], url_path="log-note")
    def log_note(self, request, pk=None):
        task = self.get_object()
        author = request.data.get("author", "Consultant")
        note_text = request.data.get("note", "")
        next_follow_up = request.data.get("next_follow_up_date")

        if not note_text:
            return Response({"error": "Note text is required"}, status=status.HTTP_400_BAD_REQUEST)

        new_note = {
            "id": f"note-{len(task.consultant_notes) + 1}",
            "author": author,
            "note": note_text,
            "timestamp": request.data.get("timestamp", "Just now"),
            "nextFollowUpDate": next_follow_up,
        }

        task.consultant_notes = [new_note] + task.consultant_notes
        task.save()

        HybridAILog.objects.create(
            ats_task=task,
            actor="HUMAN_CONSULTANT",
            action="Follow-Up Note Logged",
            details=f"Follow-up note logged by {author}: '{note_text[:60]}...'",
        )

        return Response(ConsultantATSTaskSerializer(task).data)

    @action(detail=True, methods=["post"], url_path="advance-stage")
    def advance_stage(self, request, pk=None):
        task = self.get_object()
        new_stage = request.data.get("stage")
        author = request.data.get("author", "Consultant")

        if not new_stage:
            return Response({"error": "Stage is required"}, status=status.HTTP_400_BAD_REQUEST)

        old_stage = task.stage
        task.stage = new_stage
        task.save()

        HybridAILog.objects.create(
            ats_task=task,
            actor="HUMAN_CONSULTANT",
            action="Stage Advanced",
            details=f"Stage transitioned from '{old_stage}' to '{new_stage}' by {author}.",
        )

        return Response(ConsultantATSTaskSerializer(task).data)


class HybridAILogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HybridAILog.objects.all()
    serializer_class = HybridAILogSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        task_id = self.request.query_params.get("task_id")
        if task_id:
            qs = qs.filter(ats_task_id=task_id)
        return qs


# ---------------------------------------------------------------------------
# Profile Matching Engine
# ---------------------------------------------------------------------------

class ProfileMatchAPIView(APIView):
    def post(self, request):
        country_id = request.data.get("country_id")
        cgpa = float(request.data.get("cgpa", 7.0))
        ielts = float(request.data.get("ielts", 6.5))
        german_level = request.data.get("german_level", "None")

        courses = StudyAbroadCourse.objects.all()
        if country_id:
            courses = courses.filter(country_id=country_id)

        results = []
        for crs in courses:
            score = 50
            if cgpa >= float(crs.min_cgpa):
                score += 25
            else:
                score -= int((float(crs.min_cgpa) - cgpa) * 15)

            if ielts >= float(crs.min_ielts):
                score += 15

            if crs.min_german_level == "None" or german_level >= crs.min_german_level:
                score += 10

            score = min(99, max(20, score))
            results.append({
                "course_id": crs.id,
                "course_name": crs.course_name,
                "degree": crs.degree,
                "duration": crs.duration,
                "tuition_per_year": crs.tuition_per_year,
                "college_city": crs.college.city,
                "country_name": crs.country.name,
                "match_score": score,
                "meets_criteria": cgpa >= float(crs.min_cgpa) and ielts >= float(crs.min_ielts),
            })

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return Response({"matches": results, "total_courses_evaluated": len(results)})


# ---------------------------------------------------------------------------
# Phase 1: Real-Time AI Resume Parsing API (Gemini Pro Preview Enforced)
# ---------------------------------------------------------------------------

def extract_text_from_file(uploaded_file):
    filename = uploaded_file.name.lower()
    text = ""
    try:
        if filename.endswith(".pdf"):
            import pypdf
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif filename.endswith(".docx"):
            import docx
            doc = docx.Document(uploaded_file)
            for p in doc.paragraphs:
                if p.text:
                    text += p.text + "\n"
        else:
            text = uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Text extraction warning for {filename}: {e}")
        try:
            uploaded_file.seek(0)
            text = uploaded_file.read().decode("latin1", errors="ignore")
        except Exception:
            text = ""
    return text.strip()


def heuristic_nlp_resume_parser(text, filename=""):
    """
    Genuine document parameter extractor without any mock or dummy data.
    If an item is not present in the document text, returns empty string "".
    """
    data = {
        "name": "",
        "email": "",
        "phone": "",
        "course_duration": "",
        "work_experience": "",
        "transcript_score": "",
        "field_of_interest": "",
        "language_score": "",
    }

    if not text:
        # If no text extracted, try candidate name from filename without dummy fallback
        if filename:
            base = os.path.splitext(filename)[0]
            cleaned_name = re.sub(r"[_\-]+", " ", base)
            cleaned_name = re.sub(r"(?i)\b(resume|cv|biodata|profile|btech|mtech|degree|pdf|docx)\b", "", cleaned_name).strip()
            if cleaned_name and not re.match(r"(?i)^(sample|test|document|my|new|file|candidate)$", cleaned_name):
                data["name"] = cleaned_name.title()
        return data

    # 1. Email extraction
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if email_match:
        data["email"] = email_match.group(0).lower()

    # 2. Phone extraction
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?(?:\d{5}[-.\s]?\d{5}|\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}|\d{10}))", text)
    if phone_match:
        data["phone"] = phone_match.group(0).strip()

    # 3. Candidate Name extraction (from first lines)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    candidate_name = ""
    for line in lines[:8]:
        if re.search(r"@|www|\.com|http|phone|tel|email|curriculum|resume|biodata|\+?\d{10}", line, re.IGNORECASE):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(re.match(r"^[A-Za-z.'-]+$", w) for w in words):
            candidate_name = line.strip().title()
            break
    if not candidate_name and filename:
        base = os.path.splitext(filename)[0]
        cleaned_name = re.sub(r"[_\-]+", " ", base)
        cleaned_name = re.sub(r"(?i)\b(resume|cv|biodata|profile|btech|mtech|degree|pdf|docx)\b", "", cleaned_name).strip()
        if cleaned_name and not re.match(r"(?i)^(sample|test|document|my|new|file|candidate)$", cleaned_name):
            candidate_name = cleaned_name.title()
    data["name"] = candidate_name

    # 4. Transcript score / CGPA / % extraction
    cgpa_match = re.search(r"(?i)\b(?:cgpa|gpa|percentage|marks|grade)[\s:]*([0-9]+(?:\.[0-9]+)?(?:\s*%)?(?:\s*/\s*(?:10|4|100))?)", text)
    if cgpa_match:
        val = cgpa_match.group(1).strip()
        if "%" in val:
            data["transcript_score"] = val
        elif "/" in val:
            data["transcript_score"] = f"{val} CGPA"
        else:
            data["transcript_score"] = f"{val} CGPA"
    else:
        pct_match = re.search(r"\b([56789]\d(?:\.\d+)?)\s*%", text)
        if pct_match:
            data["transcript_score"] = f"{pct_match.group(1)}%"

    # 5. Target Duration & Degree level
    if re.search(r"(?i)\b(ausbildung|dual study|vocational|apprenticeship)\b", text):
        data["course_duration"] = "3 Years (Ausbildung Dual)"
    elif re.search(r"(?i)\b(bachelor|b\.tech|b\.sc|b\.e|undergraduate|ug)\b", text) and not re.search(r"(?i)\b(master|m\.sc|m\.tech|pg)\b", text):
        data["course_duration"] = "3-4 Years (Bachelors)"
    elif re.search(r"(?i)\b(fast track|1 year|diploma|certificate)\b", text):
        data["course_duration"] = "1 Year (Fast Track)"
    elif re.search(r"(?i)\b(master|m\.sc|m\.tech|postgraduate|pg|mba)\b", text):
        data["course_duration"] = "2 Years (Masters)"

    # 6. Relevant Field of Interest
    field_keywords = [
        ("Computer Science & Artificial Intelligence", r"(?i)\b(artificial intelligence|machine learning|data science|computer science|software engineering|python|nlp|full stack)\b"),
        ("Mechanical & Automotive Systems", r"(?i)\b(mechanical|automotive|mechatronics|robotics|cad|thermodynamics)\b"),
        ("Electronics & Embedded Systems", r"(?i)\b(electronics|embedded|vlsi|iot|semiconductor|electrical)\b"),
        ("International Business & Management", r"(?i)\b(mba|management|marketing|finance|business administration|fintech)\b"),
        ("Biotechnology & Healthcare Sciences", r"(?i)\b(biotechnology|biomedical|pharmacy|bioinformatics|healthcare)\b"),
        ("Renewable Energy & Sustainability", r"(?i)\b(renewable|solar|wind|energy systems|sustainability|environmental)\b"),
    ]
    for field_name, regex in field_keywords:
        if re.search(regex, text):
            data["field_of_interest"] = field_name
            break

    # 7. Work Experience
    exp_sec_match = re.search(r"(?is)\b(?:experience|employment|work history|internship)\b(.*?)(?:\b(?:education|skills|certifications|exams|projects)\b|$)", text)
    exp_section = exp_sec_match.group(1) if exp_sec_match else text

    exp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s*(?:of\s*)?(?:experience|exp|industry))?", exp_section, re.IGNORECASE)
    if exp_match:
        yrs = exp_match.group(1)
        data["work_experience"] = f"{yrs} Years Experience"
    elif re.search(r"(?i)\b(intern|internship|trainee)\b", exp_section):
        data["work_experience"] = "Internship Experience"
    elif re.search(r"(?i)\b(fresher|entry level|graduate)\b", exp_section):
        data["work_experience"] = "Fresher / Graduate"

    # 8. Language Score
    ielts_match = re.search(r"(?i)ielts[\s:]*([0-9]+(?:\.[0-9]+)?)", text)
    toefl_match = re.search(r"(?i)toefl[\s:]*([0-9]+)", text)
    german_match = re.search(r"(?i)\b(a1|a2|b1|b2|c1|c2)\s*(?:german|goethe|telc)?\b", text)
    if ielts_match:
        data["language_score"] = f"IELTS {ielts_match.group(1)}"
    elif toefl_match:
        data["language_score"] = f"TOEFL {toefl_match.group(1)}"
    elif german_match:
        data["language_score"] = f"German Level {german_match.group(1).upper()}"

    return data


class ResumeParserAPIView(APIView):
    """
    Accepts an uploaded resume (PDF/DOCX/TXT) and uses the Gemini API
    (gemini-3.5-pro-preview with pro fallbacks) to extract genuine candidate parameters.
    Removes all mock/dummy data.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        from django.conf import settings
        resume_file = request.FILES.get("resume") or request.FILES.get("file")
        fallback_text = request.data.get("text", "")
        file_name = resume_file.name if resume_file else "Uploaded_Document"

        extracted_text = ""
        if resume_file:
            extracted_text = extract_text_from_file(resume_file)
        elif fallback_text:
            extracted_text = fallback_text

        # Baseline genuine extraction (defaults to empty strings, zero mock data)
        extracted_data = heuristic_nlp_resume_parser(extracted_text, file_name)
        parser_used = "ILA Document Extraction Engine"

        # Read configured GEMINI_API_KEY
        gemini_api_key = (
            getattr(settings, "GEMINI_API_KEY", "") or
            os.environ.get("GEMINI_API_KEY", "") or
            os.environ.get("VITE_GEMINI_API_KEY", "")
        ).strip()

        # Enforce actual Gemini API when key is valid and document text exists
        if gemini_api_key and gemini_api_key != "your_api_key_here" and extracted_text:
            models_to_try = [
                "gemini-3.5-pro-preview",
                "gemini-2.5-pro",
                "gemini-1.5-pro",
                "gemini-2.5-flash",
            ]
            gemini_success = False
            for model_name in models_to_try:
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_api_key)
                    prompt = f"""You are an expert academic resume evaluator for international study abroad applications.
Analyze the following document text and extract real candidate parameters into a JSON object with these exact keys:
- name: Candidate's real full name (or "" if not present)
- email: Candidate's real email address (or "" if not present)
- phone: Candidate's real phone/WhatsApp number (or "" if not present)
- course_duration: Preferred/matched course duration (e.g. "2 Years (Masters)", "3-4 Years (Bachelors)", "3 Years (Ausbildung Dual)", or "1 Year (Fast Track)", or "" if not present)
- work_experience: Candidate's actual work experience summary (e.g. "2 Years in Software" or "Fresher", or "" if not present)
- transcript_score: Candidate's actual GPA, CGPA, or percentage (e.g. "8.4 CGPA" or "82%", or "" if not present)
- field_of_interest: Candidate's actual domain/field of interest from their degree or projects (e.g. "Computer Science & AI", or "" if not present)
- language_score: Candidate's English/German test score (e.g. "IELTS 7.5", "German B2", or "" if not present)

STRICT REQUIREMENTS:
- Extract ONLY genuine information explicitly present in the document.
- NEVER invent or use mock/dummy data (e.g. Rafi, Rahul, or example placeholder strings).
- If any parameter is not found in the document, return an empty string "" for that key.

Document text:
{extracted_text[:15000]}

Return only valid JSON."""
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )
                    if response and response.text:
                        parsed_json = json.loads(response.text)
                        for k, v in parsed_json.items():
                            if k in extracted_data and v is not None:
                                extracted_data[k] = str(v).strip()
                        parser_used = f"Google Gemini API ({model_name})"
                        gemini_success = True
                        break
                except Exception as ex:
                    logger.info(f"Gemini API model {model_name} attempt failed: {ex}")
                    continue

        return Response({
            "success": True,
            "extracted_data": extracted_data,
            "parsed_file_name": file_name,
            "parser_engine": parser_used,
            "raw_text_length": len(extracted_text),
        }, status=status.HTTP_200_OK)


# Phase 3: Dynamic Country-Specific Sub-Navigation (Backend Sync)
# ---------------------------------------------------------------------------

DEFAULT_COUNTRY_CATEGORIES = {
    "germany": [
        {"id": "all", "label": "All Programs", "badge": "All"},
        {"id": "public_uni", "label": "Public University (€0 Tuition)", "badge": "€0 Tuition"},
        {"id": "private_uni", "label": "Private University", "badge": "Accredited"},
        {"id": "masters", "label": "Masters (PG)", "badge": "2 Years"},
        {"id": "bachelors", "label": "Bachelors (UG)", "badge": "3-4 Years"},
        {"id": "ausbildung", "label": "Ausbildung (Paid Dual Study)", "badge": "Stipend €1,100/mo"},
    ],
    "united kingdom": [
        {"id": "all", "label": "All Programs", "badge": "All"},
        {"id": "russell_group", "label": "Russell Group (Public)", "badge": "Top 100 QS"},
        {"id": "private_uni", "label": "Private University", "badge": "Industry Tied"},
        {"id": "masters", "label": "Masters (PG)", "badge": "1-2 Years"},
        {"id": "bachelors", "label": "Bachelors (UG)", "badge": "3 Years"},
        {"id": "fast_track", "label": "Fast-Track (1-Year)", "badge": "Accelerated"},
    ],
    "canada": [
        {"id": "all", "label": "All Programs", "badge": "All"},
        {"id": "public_uni", "label": "Public College / University", "badge": "PGWP 3-Year"},
        {"id": "coop_degree", "label": "Co-Op Degree Programs", "badge": "Paid Co-Op"},
        {"id": "masters", "label": "Masters (PG)", "badge": "1-2 Years"},
        {"id": "bachelors", "label": "Bachelors (UG)", "badge": "3-4 Years"},
        {"id": "post_degree_diploma", "label": "Post-Degree Diploma", "badge": "Express Entry"},
    ],
    "australia": [
        {"id": "all", "label": "All Programs", "badge": "All"},
        {"id": "group_of_eight", "label": "Group of Eight (Go8)", "badge": "Tier 1 Research"},
        {"id": "masters", "label": "Masters (PG)", "badge": "2 Years"},
        {"id": "bachelors", "label": "Bachelors (UG)", "badge": "3-4 Years"},
        {"id": "regional_pr", "label": "Regional PR Track", "badge": "Post-Study PR"},
    ],
    "france": [
        {"id": "all", "label": "All Programs", "badge": "All"},
        {"id": "grandes_ecoles", "label": "Grandes Écoles", "badge": "Elite Management"},
        {"id": "public_uni", "label": "Public Universities", "badge": "Subsidized"},
        {"id": "masters", "label": "Masters (PG)", "badge": "1-2 Years"},
        {"id": "bachelors", "label": "Bachelors (UG)", "badge": "3 Years"},
    ],
    "ireland": [
        {"id": "all", "label": "All Programs", "badge": "All"},
        {"id": "national_uni", "label": "National Universities", "badge": "Tech Hub HQ"},
        {"id": "institute_of_tech", "label": "Institute of Technology", "badge": "STEM Focused"},
        {"id": "masters", "label": "Masters (PG)", "badge": "1-2 Years"},
        {"id": "bachelors", "label": "Bachelors (UG)", "badge": "3-4 Years"},
    ],
}


class CountryCategoriesAPIView(APIView):
    """
    Synchronizes country-specific sub-navigation categories with the Backend Tie-Up DB.
    Guarantees country-specific constraints (e.g., Ausbildung appears for Germany, but never for the UK).
    """
    def get(self, request):
        country_query = request.query_params.get("country", "Germany").strip()
        country_key = country_query.lower()

        # Check DB-configured tie-up categories
        db_categories = list(CountryTieUpCategory.objects.filter(
            country__name__iexact=country_query,
            is_active=True
        ).order_by("display_order", "id"))

        if db_categories:
            categories = [
                {
                    "id": cat.category_id,
                    "label": cat.label,
                    "badge": cat.badge
                }
                for cat in db_categories
            ]
        else:
            categories = DEFAULT_COUNTRY_CATEGORIES.get(country_key, [
                {"id": "all", "label": "All Programs", "badge": "All"},
                {"id": "public_uni", "label": "Public University", "badge": "Recognized"},
                {"id": "private_uni", "label": "Private University", "badge": "Accredited"},
                {"id": "masters", "label": "Masters (PG)", "badge": "Postgraduate"},
                {"id": "bachelors", "label": "Bachelors (UG)", "badge": "Undergraduate"},
            ])

        return Response({
            "success": True,
            "country": country_query,
            "total_categories": len(categories),
            "categories": categories,
        }, status=status.HTTP_200_OK)

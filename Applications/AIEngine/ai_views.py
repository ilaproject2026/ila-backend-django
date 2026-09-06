import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .gemini_service import (
    generate_curriculum_service,
    check_eligibility_service,
    classroom_tutor_service,
    parse_resume_service,
)


def safe_json_parse(raw_text: str):
    """Parses JSON text, stripping potential markdown ```json wrappers"""
    clean_text = raw_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    try:
        return json.loads(clean_text)
    except Exception:
        return {"raw_response": raw_text}


class CourseCreatorAIGenerateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        course_name = request.data.get('course_name') or request.data.get('name')
        category = request.data.get('category', 'Education')
        target_audience = request.data.get('target_audience', 'Professional & Academic')
        duration = request.data.get('duration', '3 Months')

        if not course_name:
            return Response({'error': 'course_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        raw_result = generate_curriculum_service(course_name, category, target_audience, duration)
        data = safe_json_parse(raw_result)
        return Response(data, status=status.HTTP_200_OK)


class EligibilityCheckAIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        profile = request.data
        if not profile:
            return Response({'error': 'Profile data is required'}, status=status.HTTP_400_BAD_REQUEST)

        raw_result = check_eligibility_service(profile)
        data = safe_json_parse(raw_result)
        return Response(data, status=status.HTTP_200_OK)


class ClassroomChatAIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        question = request.data.get('question') or request.data.get('message')
        course_context = request.data.get('course_context', '')
        history = request.data.get('history', [])

        if not question:
            return Response({'error': 'question is required'}, status=status.HTTP_400_BAD_REQUEST)

        response_text = classroom_tutor_service(question, course_context, history)
        return Response({'reply': response_text}, status=status.HTTP_200_OK)


class CandidateParseResumeAIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        resume_text = request.data.get('resume_text', '')
        if not resume_text:
            return Response({'error': 'resume_text is required'}, status=status.HTTP_400_BAD_REQUEST)

        raw_result = parse_resume_service(resume_text)
        data = safe_json_parse(raw_result)
        return Response(data, status=status.HTTP_200_OK)

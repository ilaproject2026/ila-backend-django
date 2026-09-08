from django.urls import path
from .ai_views import (
    CourseCreatorAIGenerateView,
    EligibilityCheckAIView,
    ClassroomChatAIView,
    CandidateParseResumeAIView,
)

urlpatterns = [
    path('course-creator/generate/', CourseCreatorAIGenerateView.as_view(), name='ai-course-generate'),
    path('course-creator/', CourseCreatorAIGenerateView.as_view(), name='ai-course-generate-alias'),
    path('eligibility-check/', EligibilityCheckAIView.as_view(), name='ai-eligibility-check'),
    path('eligibility/', EligibilityCheckAIView.as_view(), name='ai-eligibility-alias'),
    path('classroom/chat/', ClassroomChatAIView.as_view(), name='ai-classroom-chat'),
    path('classroom-chat/', ClassroomChatAIView.as_view(), name='ai-classroom-chat-alias'),
    path('candidate/parse-resume/', CandidateParseResumeAIView.as_view(), name='ai-candidate-parse-resume'),
    path('parse-resume/', CandidateParseResumeAIView.as_view(), name='ai-candidate-parse-resume-alias'),
]

from django.urls import path
from .ai_views import (
    CourseCreatorAIGenerateView,
    EligibilityCheckAIView,
    ClassroomChatAIView,
    CandidateParseResumeAIView,
)

urlpatterns = [
    path('course-creator/generate/', CourseCreatorAIGenerateView.as_view(), name='ai-course-generate'),
    path('eligibility-check/', EligibilityCheckAIView.as_view(), name='ai-eligibility-check'),
    path('classroom/chat/', ClassroomChatAIView.as_view(), name='ai-classroom-chat'),
    path('candidate/parse-resume/', CandidateParseResumeAIView.as_view(), name='ai-candidate-parse-resume'),
]

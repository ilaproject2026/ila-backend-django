import os
from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser

from google import genai

from .studiocore_models import Application, PackageTier, ChatMessageLog
from .studiocore_serializers import (
    ApplicationSerializer,
    PackageTierSerializer,
    AssistantChatSerializer,
)

SYSTEM_INSTRUCTION = """
You are the "ILA Global Strategy Advisor", an expert executive consultant assisting Indian enterprises and remote investors with European expansion, German GmbH setup, capital protection, and independent corporate ownership.
Be professional, concise, authoritative, and strategic. Answer in 2 to 3 sentences.
"""


class ApplicationViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    POST /api/v1/studio/applications/ -> Public: Submit eligibility assessment
    GET  /api/v1/studio/applications/ -> Admin only: Review incoming leads
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        response_data = serializer.data
        response_data['message'] = (
            "Application received successfully. "
            "An ILA Global advisor will contact you within 24 hours."
        )
        return Response(response_data, status=status.HTTP_201_CREATED)


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/studio/packages/ -> Public: Fetch active package tiers
    """
    queryset = PackageTier.objects.filter(is_active=True)
    serializer_class = PackageTierSerializer
    permission_classes = [AllowAny]


class AssistantChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AssistantChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prompt = serializer.validated_data["prompt"]
        session_id = serializer.validated_data.get("session_id") or "anonymous"
        history = serializer.validated_data.get("history", [])

        api_key = settings.GEMINI_API_KEY

        if not api_key:
            return Response(
                {
                    "error": "GEMINI_API_KEY is not configured on the server."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # 1. Configure Gemini client
            client = genai.Client(api_key=api_key)

            # 2. Convert previous messages into Gemini contents
            contents = []

            for msg in history:
                role = msg.get("role")
                content = msg.get("content", "")

                if not content:
                    continue

                if role == "user":
                    contents.append({
                        "role": "user",
                        "parts": [
                            {
                                "text": content
                            }
                        ],
                    })

                elif role == "assistant" or role == "model":
                    contents.append({
                        "role": "model",
                        "parts": [
                            {
                                "text": content
                            }
                        ],
                    })

            # Add current prompt
            contents.append({
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ],
            })

            # 3. Generate response
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config={
                    "system_instruction": SYSTEM_INSTRUCTION,
                    "temperature": 0.7,
                    "max_output_tokens": 500,
                },
            )

            reply_text = response.text or "Strategic briefing generated."

            # 4. Get client IP
            client_ip = request.META.get(
                "HTTP_X_FORWARDED_FOR",
                request.META.get("REMOTE_ADDR", "")
            ).split(",")[0].strip()

            # 5. Save conversation
            ChatMessageLog.objects.create(
                session_id=session_id,
                prompt=prompt,
                response=reply_text,
                model_used="gemini-3.6-flash",
                ip_address=client_ip or None,
            )

            # 6. Return response
            return Response(
                {
                    "text": reply_text,
                    "session_id": session_id,
                    "model_used": "gemini-3.6-flash",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "error": f"AI generation error: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

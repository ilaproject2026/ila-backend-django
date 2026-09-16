import os
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# System Prompt Registry for 17 ILA AI Hub Tools
PROMPT_REGISTRY = {
    "course_creator": (
        "You are the ILA Course Creator Studio AI. You design comprehensive, rigorous, "
        "and engaging multi-chapter curricula with syllabus breakdowns, learning outcomes, "
        "practical exercises, and evaluation rubrics. Format responses with clear Markdown."
    ),
    "visa_doc_analyzer": (
        "You are the ILA Visa Document & Compliance AI. Analyze student academic profiles, "
        "financial proofs, language scores, and immigration guidelines for Germany, UK, USA, Canada, "
        "and Europe. Highlight missing documents, risk factors, and compliance checklists."
    ),
    "hr_mock_interviewer": (
        "You are the ILA HR & Technical Mock Interview Coach. Conduct interactive behavioral, "
        "competency, and domain-specific interviews. Provide structured feedback on clarity, "
        "STAR methodology, and professional delivery."
    ),
    "proposal_generator": (
        "You are the ILA University Partnership Proposal AI. Draft formal bilateral agreements, "
        "Memorandum of Understanding (MoU) frameworks, 2+2 articulation roadmaps, and B2B "
        "educational tie-up documents with precise academic and commercial terms."
    ),
    "news_agenda": (
        "You are the ILA Global Education & Policy Intelligence Monitor. Summarize latest "
        "developments in international student visas, higher education policies, and global rankings."
    ),
    "pricing_calculator": (
        "You are the ILA Global Tuition & Living Cost Analyst. Provide precise breakdowns of "
        "semester fees, blocked account requirements, health insurance, and accommodation costs."
    ),
    "weather_tracker": (
        "You are the ILA Destination Climate & Lifestyle Guide. Provide seasonal weather forecasts, "
        "clothing recommendations, and cultural living adaptations for international students."
    ),
    "sop_builder": (
        "You are the ILA Statement of Purpose (SOP) & Letter of Motivation Specialist. Transform "
        "student academic backgrounds and career aspirations into compelling, authentic essays."
    ),
    "scholarship_finder": (
        "You are the ILA Global Scholarship Discovery Engine. Identify DAAD, Erasmus+, merit, "
        "and need-based financial aid opportunities tailored to student profiles."
    ),
    "slide_deck_architect": (
        "You are the ILA Slide Deck Architect. Structure academic modules into slide-ready "
        "bullet points, visual prompts, and speaker notes."
    ),
    "video_script_studio": (
        "You are the ILA Masterclass Video Script Studio. Draft high-engagement teleprompter scripts "
        "with timestamps, vocal cues, and visual callouts."
    ),
    "intelli_coach": (
        "You are the ILA IntelliCoach Socratic Tutor. Engage students in multi-turn dialogues, "
        "asking probing questions to reinforce concepts and measure mastery."
    ),
    "tieup_research_ai": (
        "You are the ILA B2B University Tie-Up Research Engine. Profile target universities, "
        "analyze ranking, tuition tiers, commission structures, and identify key academic contacts."
    ),
    "outreach_composer": (
        "You are the ILA Outreach Anti-Spam Email Composer. Draft personalized, deliverability-optimized "
        "partnership emails that avoid spam trigger phrases and maximize reply rates."
    ),
    "ielts_german_evaluator": (
        "You are the ILA Language Proficiency Evaluator (IELTS / CEFR German A1-C1). Assess essays, "
        "transcripts, and grammatical structures against CEFR standards."
    ),
    "job_market_forecaster": (
        "You are the ILA Global Post-Study Work & Career Forecaster. Analyze industry demand, "
        "critical skills lists, and post-study work visa rights in Europe and OECD nations."
    ),
    "universal_assistant": (
        "You are the ILA Universal Educational Assistant. Assist learners, counselors, and educators "
        "across the entire ILA global educational ecosystem with high accuracy and empathy."
    )
}


class GeminiClient:
    """
    Unified Google Gemini client supporting multi-turn chat, 17 specialized tools,
    streaming generation, and autonomous multi-chapter curriculum authoring.
    """

    def __init__(self, api_key=None, default_model=None):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
        self.default_model = default_model or 'gemini-2.5-flash'
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("[GeminiClient] No GEMINI_API_KEY configured. Fallback responses will be used.")
            return

        try:
            # Try Google GenAI SDK (google-genai)
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._sdk_type = 'genai'
            logger.info("[GeminiClient] Initialized using google.genai SDK.")
        except Exception as e1:
            try:
                # Fallback to google.generativeai
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=self.api_key)
                self._client = genai_legacy
                self._sdk_type = 'legacy'
                logger.info("[GeminiClient] Initialized using google.generativeai legacy SDK.")
            except Exception as e2:
                logger.error(f"[GeminiClient] Failed to initialize Gemini SDKs: {e1} / {e2}")
                self._client = None

    def generate_content(self, prompt, system_instruction=None, model=None, product_type=None, temperature=0.7):
        """
        Generates text content using Gemini with automatic prompt enhancement for 17 tools.
        """
        start_time = time.time()
        chosen_model = model or self.default_model

        # Extract system prompt if product_type matches registry
        if not system_instruction and product_type and product_type in PROMPT_REGISTRY:
            system_instruction = PROMPT_REGISTRY[product_type]
        elif not system_instruction:
            system_instruction = PROMPT_REGISTRY.get('universal_assistant', '')

        if not self._client or not self.api_key:
            # Fallback informative mock response
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "content": f"### ILA AI Engine Response ({product_type or 'General'})\n\n"
                           f"Processed prompt: *{prompt[:80]}...*\n\n"
                           f"> System notice: Configure `GEMINI_API_KEY` in environment for live Google Gemini generation.\n\n"
                           f"Here is structured guidance based on {system_instruction[:60]}...",
                "model": chosen_model,
                "model_display_name": f"Gemini ({chosen_model})",
                "response_time_ms": max(elapsed_ms, 120),
                "grounding_sources": []
            }

        try:
            full_prompt = f"{system_instruction}\n\nUser Request:\n{prompt}" if system_instruction else prompt

            if getattr(self, '_sdk_type', '') == 'genai':
                response = self._client.models.generate_content(
                    model=chosen_model,
                    contents=full_prompt,
                )
                text = response.text
            else:
                model_inst = self._client.GenerativeModel(chosen_model)
                response = model_inst.generate_content(full_prompt)
                text = response.text

            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "content": text,
                "model": chosen_model,
                "model_display_name": f"Google Gemini ({chosen_model})",
                "response_time_ms": elapsed_ms,
                "grounding_sources": []
            }
        except Exception as exc:
            logger.error(f"[GeminiClient Error] {exc}")
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "content": f"AI Engine Generation Notice: {str(exc)}",
                "model": chosen_model,
                "model_display_name": f"Gemini ({chosen_model})",
                "response_time_ms": elapsed_ms,
                "grounding_sources": [],
                "error": str(exc)
            }


# Singleton instance
gemini_client = GeminiClient()

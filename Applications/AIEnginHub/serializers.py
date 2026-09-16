import uuid
from rest_framework import serializers
from .models import (
    CourseCategory, LibraryCourse, CourseChapter, CourseVersionSnapshot,
    ChatSession, ChatMessage, LegacyChatHistory,
    TieupLead, TieupPolicy, OutreachStatusLog, SmtpConfiguration,
    AIProductPreset, GenerationJob, SystemActivityLog, MetricSnapshot
)


# ---------------------------------------------------------------------------
# 1. Course & Library Serializers
# ---------------------------------------------------------------------------

class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'department', 'description', 'color', 'created_at', 'updated_at']


class CourseChapterSerializer(serializers.ModelSerializer):
    subTopics = serializers.JSONField(source='sub_topics', required=False, default=list)
    chapterNumber = serializers.IntegerField(source='chapter_number')
    isCompleted = serializers.BooleanField(source='is_completed', required=False, default=False)

    class Meta:
        model = CourseChapter
        fields = ['id', 'chapterNumber', 'title', 'summary', 'content', 'isCompleted', 'subTopics']


class CourseVersionSnapshotSerializer(serializers.ModelSerializer):
    versionNumber = serializers.CharField(source='version_number')
    chaptersSnapshot = serializers.JSONField(source='chapters_snapshot', required=False, default=list)
    autoSaved = serializers.BooleanField(source='auto_saved', required=False, default=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = CourseVersionSnapshot
        fields = ['id', 'versionNumber', 'label', 'chaptersSnapshot', 'autoSaved', 'createdAt']


class LibraryCourseSerializer(serializers.ModelSerializer):
    chapters = CourseChapterSerializer(many=True, required=False)
    versions = CourseVersionSnapshotSerializer(source='version_snapshots', many=True, read_only=True)

    # CamelCase Aliases for React Frontend Interoperability
    subCategory = serializers.CharField(source='sub_category', required=False, allow_blank=True, default="")
    deliveryPath = serializers.CharField(source='delivery_path', required=False, allow_blank=True, default="home")
    batchSlot = serializers.CharField(source='batch_slot', required=False, allow_blank=True, default="")
    totalChapters = serializers.IntegerField(source='total_chapters', required=False, default=0)
    sourceSessionId = serializers.CharField(source='source_session_id', required=False, allow_null=True, allow_blank=True)
    isFavorite = serializers.BooleanField(source='is_favorite', required=False, default=False)
    isPermanent = serializers.BooleanField(source='is_permanent', required=False, default=False)
    downloadCount = serializers.IntegerField(source='download_count', required=False, default=0)
    lastDownloadedAt = serializers.DateTimeField(source='last_downloaded_at', required=False, allow_null=True)
    adminCourseData = serializers.JSONField(source='admin_course_data', required=False, default=dict)
    slideAiCourseData = serializers.JSONField(source='slide_ai_course_data', required=False, default=dict)
    intelliCoachCourseData = serializers.JSONField(source='intelli_coach_course_data', required=False, default=dict)
    authorizedStructure = serializers.JSONField(source='authorized_structure', required=False, default=dict)
    studiedBy = serializers.CharField(source='studied_by', required=False, allow_blank=True, default="")
    targetAudience = serializers.CharField(source='target_audience', required=False, allow_blank=True, default="")
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = LibraryCourse
        fields = [
            'id', 'title', 'subtitle', 'category', 'subCategory', 'deliveryPath',
            'batchSlot', 'overview', 'totalChapters', 'sourceSessionId', 'tags',
            'isFavorite', 'isPermanent', 'locked', 'downloadCount', 'lastDownloadedAt',
            'studiedBy', 'targetAudience', 'adminCourseData', 'slideAiCourseData',
            'intelliCoachCourseData', 'authorizedStructure', 'metadata',
            'chapters', 'versions', 'createdAt', 'updatedAt'
        ]

    def create(self, validated_data):
        chapters_data = validated_data.pop('chapters', [])
        # Auto-generate ID if missing
        if not validated_data.get('id'):
            validated_data['id'] = f"course_{uuid.uuid4().hex[:12]}"
        
        course = LibraryCourse.objects.create(**validated_data)
        for chap in chapters_data:
            if not chap.get('id'):
                chap['id'] = f"chap_{course.id}_{chap.get('chapter_number', 1)}"
            CourseChapter.objects.create(course=course, **chap)
        return course

    def update(self, instance, validated_data):
        chapters_data = validated_data.pop('chapters', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if chapters_data is not None:
            instance.chapters.all().delete()
            for chap in chapters_data:
                if not chap.get('id'):
                    chap['id'] = f"chap_{instance.id}_{chap.get('chapter_number', 1)}"
                CourseChapter.objects.create(course=instance, **chap)
        return instance


# ---------------------------------------------------------------------------
# 2. Universal AI Chat & Sessions Serializers
# ---------------------------------------------------------------------------

class ChatMessageSerializer(serializers.ModelSerializer):
    modelDisplayName = serializers.CharField(source='model_display_name', required=False, allow_blank=True, default="")
    responseTimeMs = serializers.IntegerField(source='response_time_ms', required=False, allow_null=True)
    groundingSources = serializers.JSONField(source='grounding_sources', required=False, default=list)
    nextModuleInfo = serializers.JSONField(source='next_module_info', required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'session', 'role', 'content', 'model', 'modelDisplayName',
            'responseTimeMs', 'documents', 'groundingSources', 'nextModuleInfo', 'createdAt'
        ]

    def create(self, validated_data):
        if not validated_data.get('id'):
            validated_data['id'] = f"msg_{uuid.uuid4().hex[:12]}"
        return super().create(validated_data)


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, required=False, read_only=True)
    isPinned = serializers.BooleanField(source='is_pinned', required=False, default=False)
    productType = serializers.CharField(source='product_type', required=False, default='ila_chat')
    productParams = serializers.JSONField(source='product_params', required=False, default=dict)
    coursePlan = serializers.JSONField(source='course_plan', required=False, allow_null=True)
    autonomousPlan = serializers.JSONField(source='autonomous_plan', required=False, allow_null=True)
    studiedBy = serializers.CharField(source='studied_by', required=False, allow_blank=True, default="")
    targetAudience = serializers.CharField(source='target_audience', required=False, allow_blank=True, default="")
    isPermanent = serializers.BooleanField(source='is_permanent', required=False, default=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'title', 'isPinned', 'productType', 'productParams',
            'coursePlan', 'autonomousPlan', 'studiedBy', 'targetAudience',
            'isPermanent', 'locked', 'messages', 'createdAt', 'updatedAt'
        ]

    def create(self, validated_data):
        if not validated_data.get('id'):
            validated_data['id'] = f"session_{uuid.uuid4().hex[:12]}"
        return super().create(validated_data)


class LegacyChatHistorySerializer(serializers.ModelSerializer):
    modelDisplayName = serializers.CharField(source='model_display_name', required=False, allow_blank=True)
    responseTimeMs = serializers.IntegerField(source='response_time_ms', required=False, allow_null=True)
    isFavorite = serializers.BooleanField(source='is_favorite', required=False, default=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = LegacyChatHistory
        fields = ['id', 'query', 'response', 'model', 'modelDisplayName', 'responseTimeMs', 'isFavorite', 'createdAt']


# ---------------------------------------------------------------------------
# 3. Tie-Up CRM & Outreach Serializers
# ---------------------------------------------------------------------------

class TieupLeadSerializer(serializers.ModelSerializer):
    sessionId = serializers.CharField(source='session_id', required=False, allow_null=True, allow_blank=True)
    subCategory = serializers.CharField(source='sub_category', required=False, allow_blank=True, default="")
    locationMain = serializers.CharField(source='location_main')
    locationSub = serializers.CharField(source='location_sub', required=False, allow_blank=True, default="")
    contactPerson = serializers.CharField(source='contact_person')
    contactTitle = serializers.CharField(source='contact_title')
    contactEmail = serializers.EmailField(source='contact_email')
    contactPhone = serializers.CharField(source='contact_phone', required=False, allow_blank=True, default="")
    websiteUrl = serializers.URLField(source='website_url', required=False, allow_blank=True, default="")
    isPartner = serializers.BooleanField(source='is_partner', required=False, default=False)
    compatibilityScore = serializers.IntegerField(source='compatibility_score', required=False, default=88)
    commissionPercent = serializers.FloatField(source='commission_percent', required=False, default=15.0)
    matchingCriteria = serializers.JSONField(source='matching_criteria', required=False, default=list)
    directSourcePageUrl = serializers.URLField(source='direct_source_page_url', required=False, allow_blank=True, default="")
    studentRequirements = serializers.CharField(source='student_requirements', required=False, allow_blank=True, default="")
    institutionCriteria = serializers.CharField(source='institution_criteria', required=False, allow_blank=True, default="")
    termsOfPartnership = serializers.CharField(source='terms_of_partnership', required=False, allow_blank=True, default="")
    termsSummary = serializers.CharField(source='terms_summary', required=False, allow_blank=True, default="")
    partnershipTerms = serializers.JSONField(source='partnership_terms', required=False, default=dict)
    minIeltsScore = serializers.FloatField(source='min_ielts_score', required=False, default=6.0)
    germanLevelRequired = serializers.CharField(source='german_level_required', required=False, default="None (English Only)")
    tuitionFeeYearly = serializers.CharField(source='tuition_fee_yearly', required=False, default="€0 (Public)")
    tuitionAmountEur = serializers.FloatField(source='tuition_amount_eur', required=False, default=0.0)
    scholarshipAvailable = serializers.BooleanField(source='scholarship_available', required=False, default=False)
    scholarshipDetails = serializers.CharField(source='scholarship_details', required=False, allow_blank=True, default="")
    courseList = serializers.JSONField(source='course_list', required=False, default=list)
    mouDocumentUrl = serializers.URLField(source='mou_document_url', required=False, allow_blank=True, default="")
    antiSpamStatus = serializers.CharField(source='anti_spam_status', required=False, default='verified')
    antiSpamNotes = serializers.CharField(source='anti_spam_notes', required=False, allow_blank=True, default="")
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = TieupLead
        fields = [
            'id', 'sessionId', 'name', 'category', 'subCategory', 'country', 'region',
            'locationMain', 'locationSub', 'contactPerson', 'contactTitle', 'contactEmail',
            'contactPhone', 'websiteUrl', 'isPartner', 'compatibilityScore', 'commissionPercent',
            'matchingCriteria', 'directSourcePageUrl', 'studentRequirements', 'institutionCriteria',
            'termsOfPartnership', 'termsSummary', 'partnershipTerms', 'minIeltsScore',
            'germanLevelRequired', 'tuitionFeeYearly', 'tuitionAmountEur', 'scholarshipAvailable',
            'scholarshipDetails', 'courseList', 'mouDocumentUrl', 'antiSpamStatus', 'antiSpamNotes',
            'createdAt', 'updatedAt'
        ]

    def create(self, validated_data):
        if not validated_data.get('id'):
            validated_data['id'] = f"lead_{uuid.uuid4().hex[:12]}"
        return super().create(validated_data)


class TieupPolicySerializer(serializers.ModelSerializer):
    minCommissionPercent = serializers.FloatField(source='min_commission_percent')
    targetCommissionPercent = serializers.FloatField(source='target_commission_percent')
    partnershipCriteria = serializers.CharField(source='partnership_criteria', required=False, allow_blank=True, default="")
    studentRequirementsGuidelines = serializers.CharField(source='student_requirements_guidelines', required=False, allow_blank=True, default="")
    termsExpectations = serializers.CharField(source='terms_expectations', required=False, allow_blank=True, default="")
    preferredPaymentTerms = serializers.CharField(source='preferred_payment_terms', required=False, default="Net 30 on student semester enrollment")
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = TieupPolicy
        fields = [
            'id', 'minCommissionPercent', 'targetCommissionPercent', 'partnershipCriteria',
            'studentRequirementsGuidelines', 'termsExpectations', 'preferredPaymentTerms', 'updatedAt'
        ]


class OutreachStatusLogSerializer(serializers.ModelSerializer):
    institutionName = serializers.CharField(source='institution_name')
    recipientEmail = serializers.EmailField(source='recipient_email')
    recipientName = serializers.CharField(source='recipient_name', required=False, allow_blank=True, default="")
    senderEmail = serializers.EmailField(source='sender_email', required=False, allow_blank=True, default="")
    flagReason = serializers.CharField(source='flag_reason', required=False, allow_blank=True, default="")
    spamScore = serializers.IntegerField(source='spam_score', required=False, default=0)
    followupCount = serializers.IntegerField(source='followup_count', required=False, default=0)
    lastFollowupAt = serializers.DateTimeField(source='last_followup_at', required=False, allow_null=True)
    meetingScheduledAt = serializers.DateTimeField(source='meeting_scheduled_at', required=False, allow_null=True)
    meetingLink = serializers.URLField(source='meeting_link', required=False, allow_blank=True, default="")
    meetingAgenda = serializers.CharField(source='meeting_agenda', required=False, allow_blank=True, default="")
    responseExcerpt = serializers.CharField(source='response_excerpt', required=False, allow_blank=True, default="")
    responseSentiment = serializers.CharField(source='response_sentiment', required=False, allow_blank=True, default="")
    aiSuggestedReply = serializers.CharField(source='ai_suggested_reply', required=False, allow_blank=True, default="")
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    lastChecked = serializers.DateTimeField(source='last_checked', read_only=True)

    class Meta:
        model = OutreachStatusLog
        fields = [
            'id', 'lead', 'institutionName', 'recipientEmail', 'recipientName', 'senderEmail',
            'subject', 'status', 'flagReason', 'spamScore', 'phase', 'followupCount',
            'lastFollowupAt', 'meetingScheduledAt', 'meetingLink', 'meetingAgenda',
            'responseExcerpt', 'responseSentiment', 'aiSuggestedReply', 'createdAt', 'lastChecked'
        ]


class SmtpConfigurationSerializer(serializers.ModelSerializer):
    senderEmail = serializers.EmailField(source='sender_email')
    senderName = serializers.CharField(source='sender_name', required=False, allow_blank=True, default="")
    appPassword = serializers.CharField(source='app_password', write_only=True)
    isSecure = serializers.BooleanField(source='is_secure', required=False, default=False)
    isActive = serializers.BooleanField(source='is_active', required=False, default=True)
    dailyLimit = serializers.IntegerField(source='daily_limit', required=False, default=500)
    sentToday = serializers.IntegerField(source='sent_today', read_only=True)

    class Meta:
        model = SmtpConfiguration
        fields = [
            'id', 'name', 'host', 'port', 'senderEmail', 'senderName', 'appPassword',
            'isSecure', 'isActive', 'dailyLimit', 'sentToday', 'last_used_at', 'created_at', 'updated_at'
        ]


# ---------------------------------------------------------------------------
# 4. AI Hub 17-Product Presets & Jobs Serializers
# ---------------------------------------------------------------------------

class AIProductPresetSerializer(serializers.ModelSerializer):
    systemPrompt = serializers.CharField(source='system_prompt', required=False, allow_blank=True)
    defaultModel = serializers.CharField(source='default_model', required=False, default='gemini-2.5-flash')
    inputSchema = serializers.JSONField(source='input_schema', required=False, default=dict)
    isActive = serializers.BooleanField(source='is_active', required=False, default=True)

    class Meta:
        model = AIProductPreset
        fields = [
            'id', 'name', 'icon', 'description', 'systemPrompt', 'defaultModel',
            'temperature', 'tags', 'inputSchema', 'isActive', 'created_at', 'updated_at'
        ]


class GenerationJobSerializer(serializers.ModelSerializer):
    jobType = serializers.CharField(source='job_type')
    errorMessage = serializers.CharField(source='error_message', required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    completedAt = serializers.DateTimeField(source='completed_at', read_only=True)

    class Meta:
        model = GenerationJob
        fields = [
            'id', 'jobType', 'status', 'progress', 'payload', 'result',
            'errorMessage', 'createdAt', 'completedAt'
        ]


# ---------------------------------------------------------------------------
# 5. Activity Logs & Telemetry Serializers
# ---------------------------------------------------------------------------

class SystemActivityLogSerializer(serializers.ModelSerializer):
    actionType = serializers.CharField(source='action_type')
    userIdentifier = serializers.CharField(source='user_identifier', required=False, default='system')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = SystemActivityLog
        fields = ['id', 'actionType', 'module', 'description', 'userIdentifier', 'metadata', 'createdAt']


class MetricSnapshotSerializer(serializers.ModelSerializer):
    metricKey = serializers.CharField(source='metric_key')
    metricValue = serializers.FloatField(source='metric_value')
    recordedAt = serializers.DateTimeField(source='recorded_at', read_only=True)

    class Meta:
        model = MetricSnapshot
        fields = ['id', 'metricKey', 'metricValue', 'dimensions', 'recordedAt']

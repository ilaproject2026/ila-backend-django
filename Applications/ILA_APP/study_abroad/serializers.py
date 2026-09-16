from rest_framework import serializers
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


class CountrySerializer(serializers.ModelSerializer):
    colleges_count = serializers.IntegerField(source="colleges.count", read_only=True)

    class Meta:
        model = Country
        fields = "__all__"


class CollegeSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)
    country_flag = serializers.CharField(source="country.flag", read_only=True)
    courses_count = serializers.IntegerField(source="courses.count", read_only=True)

    class Meta:
        model = College
        fields = "__all__"


class StudyAbroadCourseSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source="college.name", read_only=True)
    country_name = serializers.CharField(source="country.name", read_only=True)
    country_flag = serializers.CharField(source="country.flag", read_only=True)

    class Meta:
        model = StudyAbroadCourse
        fields = "__all__"


# Student-Facing Privacy Masked Serializer
class StudentPrivacyCourseViewSerializer(serializers.ModelSerializer):
    """
    Suppresses specific College names before admin authorization.
    Displays course structure, tuition, degree, and country parameters.
    """
    country_name = serializers.CharField(source="country.name", read_only=True)
    country_flag = serializers.CharField(source="country.flag", read_only=True)
    college_identifier = serializers.SerializerMethodField()

    class Meta:
        model = StudyAbroadCourse
        fields = [
            "id",
            "course_name",
            "degree",
            "duration",
            "language",
            "tuition_per_year",
            "min_cgpa",
            "min_ielts",
            "min_german_level",
            "intake_season",
            "description",
            "country_name",
            "country_flag",
            "college_identifier",
        ]

    def get_college_identifier(self, obj):
        return f"Partner Institution in {obj.college.city}, {obj.country.name}"


class StudentApplicationSerializer(serializers.ModelSerializer):
    target_country_name = serializers.CharField(source="target_country.name", read_only=True)
    assigned_college_name = serializers.SerializerMethodField()
    matched_course_name = serializers.CharField(source="matched_course.course_name", read_only=True)

    class Meta:
        model = StudentApplication
        fields = "__all__"

    def get_assigned_college_name(self, obj):
        if obj.is_college_revealed and obj.assigned_college:
            return obj.assigned_college.name
        elif obj.assigned_college:
            return f"Accredited University ({obj.assigned_college.city}) [Protected / Unlock to Reveal]"
        return "Not Assigned Yet"


class DocumentChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChecklist
        fields = "__all__"


class HybridAILogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HybridAILog
        fields = "__all__"


class ConsultantATSTaskSerializer(serializers.ModelSerializer):
    hybrid_logs = HybridAILogSerializer(many=True, read_only=True)

    class Meta:
        model = ConsultantATSTask
        fields = "__all__"


class CountryTieUpCategorySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = CountryTieUpCategory
        fields = "__all__"


class ResumeParsedDataSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True, default="")
    email = serializers.EmailField(allow_blank=True, default="")
    phone = serializers.CharField(allow_blank=True, default="")
    course_duration = serializers.CharField(allow_blank=True, default="2 Years (Masters)")
    work_experience = serializers.CharField(allow_blank=True, default="")
    transcript_score = serializers.CharField(allow_blank=True, default="")
    field_of_interest = serializers.CharField(allow_blank=True, default="")
    language_score = serializers.CharField(allow_blank=True, default="")

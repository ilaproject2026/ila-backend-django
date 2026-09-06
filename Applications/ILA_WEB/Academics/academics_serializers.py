from rest_framework import serializers
from .academics_models import (
    GlobalCategory,
    GlobalSubCategory,
    TeachingStrategy,
    StudentAnalyzingStrategy,
    GlobalCourse,
    GlobalPath,
    GlobalBatch,
    ClassScheduleSession,
    CourseMaterial,
    StudentEnrollment,
)


class GlobalSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSubCategory
        fields = '__all__'


class GlobalCategorySerializer(serializers.ModelSerializer):
    subcategories = GlobalSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = GlobalCategory
        fields = '__all__'


class TeachingStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeachingStrategy
        fields = '__all__'


class StudentAnalyzingStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnalyzingStrategy
        fields = '__all__'


class GlobalPathSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = GlobalPath
        fields = '__all__'


class GlobalBatchSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    path_name = serializers.CharField(source='path.name', read_only=True)

    class Meta:
        model = GlobalBatch
        fields = '__all__'


class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = '__all__'


class GlobalCourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    paths = GlobalPathSerializer(many=True, read_only=True)
    batches = GlobalBatchSerializer(many=True, read_only=True)
    materials = CourseMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = GlobalCourse
        fields = '__all__'


class ClassScheduleSessionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)

    class Meta:
        model = ClassScheduleSession
        fields = '__all__'


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.fullname', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = StudentEnrollment
        fields = '__all__'

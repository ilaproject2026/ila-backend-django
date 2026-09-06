from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

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
from .academics_serializers import (
    GlobalCategorySerializer,
    GlobalSubCategorySerializer,
    TeachingStrategySerializer,
    StudentAnalyzingStrategySerializer,
    GlobalCourseSerializer,
    GlobalPathSerializer,
    GlobalBatchSerializer,
    ClassScheduleSessionSerializer,
    CourseMaterialSerializer,
    StudentEnrollmentSerializer,
)


class GlobalCategoryViewSet(viewsets.ModelViewSet):
    queryset = GlobalCategory.objects.all().prefetch_related('subcategories')
    serializer_class = GlobalCategorySerializer
    permission_classes = [AllowAny]


class TeachingStrategyViewSet(viewsets.ModelViewSet):
    queryset = TeachingStrategy.objects.all()
    serializer_class = TeachingStrategySerializer
    permission_classes = [AllowAny]


class StudentAnalyzingStrategyViewSet(viewsets.ModelViewSet):
    queryset = StudentAnalyzingStrategy.objects.all()
    serializer_class = StudentAnalyzingStrategySerializer
    permission_classes = [AllowAny]


class GlobalCourseViewSet(viewsets.ModelViewSet):
    queryset = GlobalCourse.objects.all().prefetch_related('paths', 'batches', 'materials')
    serializer_class = GlobalCourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        library_type = self.request.query_params.get('library_type')
        category_id = self.request.query_params.get('category')
        sub_category = self.request.query_params.get('sub_category')

        if library_type:
            queryset = queryset.filter(library_type__iexact=library_type)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if sub_category:
            queryset = queryset.filter(sub_category_name__icontains=sub_category)
        return queryset


class GlobalPathViewSet(viewsets.ModelViewSet):
    queryset = GlobalPath.objects.all()
    serializer_class = GlobalPathSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class GlobalBatchViewSet(viewsets.ModelViewSet):
    queryset = GlobalBatch.objects.all()
    serializer_class = GlobalBatchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course')
        path_id = self.request.query_params.get('path')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if path_id:
            queryset = queryset.filter(path_id=path_id)
        return queryset


class ClassScheduleSessionViewSet(viewsets.ModelViewSet):
    queryset = ClassScheduleSession.objects.all()
    serializer_class = ClassScheduleSessionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.query_params.get('date')
        course_id = self.request.query_params.get('course')
        batch_id = self.request.query_params.get('batch')
        status_val = self.request.query_params.get('status')

        if date:
            queryset = queryset.filter(date=date)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        if status_val:
            queryset = queryset.filter(status__iexact=status_val)
        return queryset


class CourseMaterialViewSet(viewsets.ModelViewSet):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer
    permission_classes = [AllowAny]


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [AllowAny]

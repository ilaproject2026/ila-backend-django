from rest_framework import serializers
from .models import WorkStudyPackage, WorkStudyRoleFeature, WorkStudyStream, WorkStudyCandidate

class WorkStudyRoleFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkStudyRoleFeature
        fields = ['id', 'title', 'order', 'is_milestone']


class WorkStudyStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkStudyStream
        fields = ['id', 'name', 'code']


class WorkStudyPackageSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    streams = serializers.SerializerMethodField()

    class Meta:
        model = WorkStudyPackage
        fields = [
            'id', 'category', 'category_label', 'title', 'badge',
            'stipend', 'training_duration', 'internship_duration', 'certification',
            'roles', 'streams', 'action_text', 'description', 'terms_and_conditions',
            'status', 'promoted_to_marketing', 'marketing_campaign_id', 'last_promoted_at',
            'created_at', 'updated_at'
        ]

    def get_roles(self, obj):
        return [r.title for r in obj.roles.all().order_by('order')]

    def get_streams(self, obj):
        return [s.name for s in obj.streams.all()]


class WorkStudyCandidateSerializer(serializers.ModelSerializer):
    package_title = serializers.CharField(source='package.title', read_only=True)

    class Meta:
        model = WorkStudyCandidate
        fields = '__all__'


class JDPromotionSerializer(serializers.Serializer):
    channels = serializers.ListField(
        child=serializers.CharField(),
        default=['WhatsApp', 'Meta Ads', 'LinkedIn', 'Email Funnel']
    )
    custom_message = serializers.CharField(required=False, allow_blank=True)
    target_region = serializers.CharField(default='All India & DACH Region')

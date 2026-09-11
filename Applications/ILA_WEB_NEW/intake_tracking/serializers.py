from rest_framework import serializers
from .models import DepartmentInquiry, FollowUpAutoTriggerRule, SocialMediaCampaign


class DepartmentInquirySerializer(serializers.ModelSerializer):
    # Allow dynamic_data to accept any JSON structure
    dynamic_data = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = DepartmentInquiry
        fields = "__all__"

    def to_internal_value(self, data):
        # Create a mutable copy of the incoming data dict
        data = data.copy() if hasattr(data, 'copy') else dict(data)

        # Standard field aliases from camelCase to snake_case
        alias_map = {
            'formType': 'form_type',
            'inquiryType': 'inquiry_type',
            'programOfInterest': 'program_of_interest',
            'paymentStatus': 'payment_status',
            'aiScore': 'ai_score',
            'aiPath': 'ai_path',
            'aiActionPlan': 'ai_action_plan',
            'crmStatus': 'crm_status',
            'pipelineStage': 'pipeline_stage',
            'docStatus': 'doc_status',
            'counselorAssigned': 'counselor_assigned',
            'lastContactedAt': 'last_contacted_at',
            'dynamicData': 'dynamic_data',
        }

        for camel, snake in alias_map.items():
            if camel in data and snake not in data:
                data[snake] = data.pop(camel)

        # Sync course / program_of_interest
        if 'course' in data and not data.get('program_of_interest'):
            data['program_of_interest'] = data['course']
        elif 'program_of_interest' in data and not data.get('course'):
            data['course'] = data['program_of_interest']

        # Sync category / department
        if 'category' in data and not data.get('department'):
            data['department'] = data['category']
        elif 'department' in data and not data.get('category'):
            data['category'] = data['department']

        # Collect all model field names
        model_field_names = {f.name for f in DepartmentInquiry._meta.get_fields()}

        # Extract dynamic keys that aren't model columns
        dynamic_payload = data.get('dynamic_data', {})
        if not isinstance(dynamic_payload, dict):
            dynamic_payload = {}

        keys_to_remove = []
        for key, value in data.items():
            if key not in model_field_names:
                dynamic_payload[key] = value
                keys_to_remove.append(key)

        for key in keys_to_remove:
            data.pop(key, None)

        data['dynamic_data'] = dynamic_payload

        return super().to_internal_value(data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Surface dynamic_data keys at root for seamless access
        if isinstance(instance.dynamic_data, dict):
            for k, v in instance.dynamic_data.items():
                if k not in rep:
                    rep[k] = v
        return rep


class FollowUpAutoTriggerRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpAutoTriggerRule
        fields = "__all__"


class SocialMediaCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaCampaign
        fields = "__all__"

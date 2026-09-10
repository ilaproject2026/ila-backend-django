from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'model', 'assistant', 'system'])
    content = serializers.CharField(max_length=2000)


class ConsultantChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1500, required=True)
    topic = serializers.CharField(max_length=50, default='general')
    history = serializers.ListField(
        child=ChatMessageSerializer(),
        required=False,
        default=list
    )
    user_email = serializers.EmailField(required=False, allow_blank=True)
    user_phone = serializers.CharField(max_length=30, required=False, allow_blank=True)


class ConsultantChatResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    suggested_actions = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    topic = serializers.CharField()


from ..models import ConsultantSession, ConsultantChatMessage


class ConsultantChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultantChatMessage
        fields = ['id', 'role', 'content', 'suggested_actions', 'timestamp', 'total_tokens']


class ConsultantSessionSerializer(serializers.ModelSerializer):
    messages = ConsultantChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ConsultantSession
        fields = [
            'id', 'session_key', 'user', 'user_email', 'user_phone', 'user_name',
            'initial_topic', 'current_topic', 'status', 'total_messages',
            'total_tokens_used', 'inquiry', 'last_activity', 'created_at', 'messages'
        ]
        read_only_fields = ['id', 'total_messages', 'total_tokens_used', 'last_activity', 'created_at']


class ConsultantChatInputSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=128, required=False, allow_blank=True)
    message = serializers.CharField(required=True)
    topic = serializers.CharField(required=False, default='general')
    history = serializers.ListField(child=serializers.DictField(), required=False, default=list)
    user_email = serializers.EmailField(required=False, allow_blank=True)
    user_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    user_name = serializers.CharField(max_length=150, required=False, allow_blank=True)


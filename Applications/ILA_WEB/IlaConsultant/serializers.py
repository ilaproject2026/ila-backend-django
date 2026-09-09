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

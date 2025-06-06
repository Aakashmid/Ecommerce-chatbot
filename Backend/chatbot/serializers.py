
from rest_framework import serializers
from users.serializers import UserSerializer
from .models import ChatbotSession,ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'content', 'timestamp']
        read_only_fields = ['timestamp']


class ChatbotSessionSerializer(serializers.ModelSerializer):
    """Serializer for chatbot sessions"""
    user = UserSerializer(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    duration = serializers.DurationField(read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ChatbotSession
        fields = [
            'id', 'session_id', 'user', 'status', 'started_at', 
            'last_activity', 'ended_at', 'messages', 
            'duration', 'message_count'
        ]
        read_only_fields = ['started_at', 'last_activity', 'ended_at']

class ChatMessageCreateSerializer(serializers.ModelSerializer):
      """Serializer for creating new chat messages"""
    
      class Meta:
          model = ChatMessage
          fields = ['session', 'message_type', 'content']
    
      def validate_session(self, value):
          """Validate that the session is active"""
          if not value:
              raise serializers.ValidationError("Session is required")
          if value.status != 'active':
              raise serializers.ValidationError("Cannot add messages to an inactive or completed session")
          return value
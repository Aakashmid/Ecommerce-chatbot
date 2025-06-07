
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
    duration = serializers.DurationField(read_only=True)
    
    
    class Meta:
        model = ChatbotSession
        fields = [
            'id', 'session_id', 'user_id', 'status', 'started_at', 
            'last_activity', 'ended_at', 
            'duration'
        ]
        read_only_fields = ['started_at', 'last_activity', 'ended_at','session_id']

    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user_id'] = request.user.id
        return super().create(validated_data)

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
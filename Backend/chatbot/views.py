

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from .models import ChatbotSession, ChatMessage
from .serializers import (
    ChatbotSessionSerializer, 
    ChatMessageSerializer, 
    ChatMessageCreateSerializer
)


class ChatbotSessionViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for managing chatbot sessions.
    Provides full CRUD operations for chat sessions.
    """
    serializer_class = ChatbotSessionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'session_id'

    def get_queryset(self):
        """Return sessions for the current user only"""
        if self.request.user.is_authenticated:
            return ChatbotSession.objects.filter(user=self.request.user)
        return ChatbotSession.objects.none()

    def perform_create(self, serializer):
        """Set the user when creating a new session"""
        serializer.save(user=self.request.user)


class ChatMessageView(APIView):
    """
    API view for chat messages with GET (list) and POST methods
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        """Get all messages for a specific session"""
        session = get_object_or_404(
            ChatbotSession, 
            session_id=session_id, 
            user=request.user
        )
        
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        
        return Response(serializer.data)
    
    
    def post(self, request, session_id):
        """Send a message/query to a specific chat session"""
        # Get the session
        session = get_object_or_404(
            ChatbotSession, 
            session_id=session_id, 
            user=request.user
        )

        # Check if session is active
        if session.status != 'active':
            return Response(
                {'error': 'Cannot send messages to an inactive or completed session'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user message
        user_message_data = {
            'session': session.id,
            'message_type': 'user',
            'content': request.data.get('message', '')
        }

        user_serializer = ChatMessageCreateSerializer(data=user_message_data)
        if user_serializer.is_valid():
            user_message = user_serializer.save()
            
            # Update session last activity
            session.last_activity = timezone.now()
            session.save()

            # Generate bot response
            bot_response = self.generate_bot_response(user_message.content)
            
            # Create bot message
            bot_message_data = {
                'session': session.id,
                'message_type': 'bot',
                'content': bot_response
            }
            
            bot_serializer = ChatMessageCreateSerializer(data=bot_message_data)
            if bot_serializer.is_valid():
                bot_message = bot_serializer.save()
                
                return Response({
                    'session_id': session.session_id,
                    'user_message': ChatMessageSerializer(user_message).data,
                    'bot_response': ChatMessageSerializer(bot_message).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Failed to create bot response', 'details': bot_serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Invalid message data', 'details': user_serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def generate_bot_response(self, user_message):
        """
        Generate bot response based on user message.
        Replace this with your actual chatbot logic.
        """
        user_message_lower = user_message.lower()
        
        if 'hello' in user_message_lower or 'hi' in user_message_lower:
            return "Hello! How can I help you today?"
        elif 'product' in user_message_lower:
            return "I can help you find products. What are you looking for?"
        elif 'price' in user_message_lower:
            return "I can help you with pricing information. Which product are you interested in?"
        elif 'help' in user_message_lower:
            return "I'm here to help! You can ask me about products, prices, orders, or anything else."
        else:
            return "Thank you for your message. How can I assist you further?"
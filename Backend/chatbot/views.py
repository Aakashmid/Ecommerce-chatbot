from django.shortcuts import get_object_or_404
from decouple import config 
import json
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from .models import ChatbotSession, ChatMessage
from products.models import Product
from products.serializers import ProductSerializer
from .serializers import ChatbotSessionSerializer, ChatMessageSerializer, ChatMessageCreateSerializer






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


class ChatMessageView(APIView):
    """
    API view for chat messages with GET (list) and POST methods
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        """Get all messages for a specific session"""
        session = get_object_or_404(ChatbotSession, session_id=session_id, user=request.user)

        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)

        return Response(serializer.data)

    def post(self, request, session_id):
        """Send a message to chatbot and receive AI + optional data response"""
        session = get_object_or_404(ChatbotSession, session_id=session_id, user=request.user)

        if session.status != 'active':
            return Response({'error': 'Session is inactive or completed'}, status=status.HTTP_400_BAD_REQUEST)

        user_message_text = request.data.get('message', '').strip()
        if not user_message_text:
            return Response({'error': 'Empty message not allowed'}, status=status.HTTP_400_BAD_REQUEST)

        # Save user message
        user_data = {'session': session.id, 'message_type': 'user', 'content': user_message_text}
        user_serializer = ChatMessageCreateSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response({'error': 'Invalid user message', 'details': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user_message = user_serializer.save()
        session.last_activity = timezone.now()
        session.save()

        # AI Logic & Bot Reply
        bot_logic = self.get_bot_response(user_message_text)
        bot_text = bot_logic.get("message", "Sorry, I couldn't understand that.")
        bot_data = bot_logic.get("data")

        # Save bot message
        bot_serializer = ChatMessageCreateSerializer(data={
            'session': session.id,
            'message_type': 'bot',
            'content': bot_text
        })

        if not bot_serializer.is_valid():
            return Response({'error': 'Bot response creation failed', 'details': bot_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        bot_message = bot_serializer.save()

        return Response({
            'session_id': session.session_id,
            'user_message': ChatMessageSerializer(user_message).data,
            'bot_response': ChatMessageSerializer(bot_message).data,
            'data': bot_data if bot_data else None
        }, status=status.HTTP_201_CREATED)

    @staticmethod
    def get_bot_response(query: str) -> dict:
        """
        -  AI parses the query to structured JSON (intent + parameters)
        -  Perform database logic if applicable
        -  generate natural response based on query/result
        """
        try:
            # Get intent and parameters
            extract_intent_prompt = [
                SystemMessage("You are an intent extraction engine. Respond ONLY in JSON."),
                UserMessage(
                    f"""Extract 'intent' and optional 'parameters' like category, price_limit, or product_id from the message below.

    Message: '{query}'

    Respond with only a JSON like:
    {{"intent": "search_product", "parameters": {{"category": "phone", "price_limit": 15000}}}}"""
                )
            ]

            intent_response = client.complete(
                messages=extract_intent_prompt,
                temperature=0.3,
                top_p=1.0,
                model=model
            )

            intent_data = json.loads(intent_response.choices[0].message.content.strip())
            intent = intent_data.get("intent")
            params = intent_data.get("parameters", {})

            products_data = None

            # Step 2: Handle actionable intent
            if intent == "search_product":
                products = Product.objects.all()
                if "category" in params:
                    products = products.filter(category__name__icontains=params["category"])
                if "price_limit" in params:
                    products = products.filter(price__lte=params["price_limit"])
                products_data = ProductSerializer(products, many=True).data

            #   generate natural response message based on user query and intent
            summary_prompt = [
                SystemMessage("You are a helpful assistant that summarizes search results or replies conversationally."),
                UserMessage(
                    f"""User asked: '{query}'

    Here is the extracted intent: {intent}
    Parameters: {json.dumps(params)}
    Search Result: {'Found ' + str(len(products_data)) + ' products' if products_data else 'No products found' if intent == 'search_product' else 'Not applicable'}

    Now, generate a friendly reply for the user in simple language."""
                )
            ]

            summary_response = client.complete(
                messages=summary_prompt,
                temperature=0.5,
                top_p=1.0,
                model=model
            )

            ai_message = summary_response.choices[0].message.content.strip()

            return {
                "message": ai_message,
                "data": products_data if products_data else None
            }

        except Exception as e:
            return {
                "message": "Something went wrong while processing your request.",
                "data": f"Error: {str(e)}"
            }

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json
from decouple import config
from .models import ChatbotSession, ChatMessage
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam as SystemMessage, ChatCompletionUserMessageParam as UserMessage


endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4.1"
token = config("GITHUB_TOKEN")
client = OpenAI(
    base_url=endpoint,
    api_key=token,
)


session_history = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connection established")
        self.session_id = self.scope['url_route']['kwargs']['session_id']

        if self.is_error_exists():
            print(f"Error exists: {self.scope['error']}")
            await self.close()
            return

        self.user_id = self.scope.get('user_id', None)

        try:
            self.session = await self.get_session(self.session_id, self.user_id)
            # print(f"Session found: {self.session}") # causing error
            print(hasattr(self, 'session'))
            if session_history.get(self.session_id,None) is  None:
                messages =  await self.get_session_messages(self.session_id)
                session_history[self.session_id] = [
                    {"role": "user" if m["message_type"] == "user" else "system", "content": m["content"]}
                    for m in messages
                ]
            await self.accept()
        except ChatbotSession.DoesNotExist:
            print(f"No session found for session_id: {self.session_id} and user_id: {self.user_id}")
            await self.close()
            return
        



    async def get_response(self, message):
        # get bot response for the given message
        response = client.chat.completions.create(
            # messages=[
            #     {
            #         "role": "system",
            #         "content": "You are a helpful assistant.",
            #     },
            #     {
            #         "role": "user",
            #         "content": message,
            #     },
            # ],
            messages= session_history.get(self.session_id, []),
            temperature=1.0,
            top_p=1.0,
            model=model_name,
        )
        bot_response = response.choices[0].message.content
        return bot_response

        # return f"Bot response to: {message}"

    async def receive(self, text_data):
        if self.user_id is not None and hasattr(self, 'session'):
            text_data_json = json.loads(text_data)
            isBot = text_data_json.get('isBot', False)

            if not isBot:
                message = text_data_json.get('message')
                if message:
                    session_history[self.session_id].append({"role": "user", "content": message})
                    botresponse = await self.get_response(message)

                    # Send message to chat
                    await self.send_to_chat(message)

                    session_history[self.session_id].append({"role": "system", "content": botresponse})
                    # print(f"Bot response: {botresponse}")

                    await self.send_to_chat(botresponse, isBot=True)

                    try:
                        await self.save_message(self.session, message, isBot=False)
                        await self.save_message(self.session, botresponse, isBot=True)
                    except Exception as e:
                        print(f"Error saving message: {e}")
                        await self.send(text_data=json.dumps({"error": "Failed to save message"}))

    async def send_to_chat(self, message, isBot=False):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "isBot": isBot}))

    @database_sync_to_async
    def save_message(self, session, message, isBot):
        ChatMessage.objects.create(message_type='bot' if isBot else 'user', content=message, session=session)

    @database_sync_to_async
    def get_session(self, session_id, user_id):
        return ChatbotSession.objects.get(session_id=session_id, user_id=user_id)

    # check if any error exists in the scope
    def is_error_exists(self):
        """This checks if error exists during websockets"""

        return True if 'error' in self.scope else False
    
    @database_sync_to_async
    def get_session_messages(self, session_id):
        """
        Get all messages for a given session and add that in sesssion history according to type of message.
        """

        try:
            session = ChatbotSession.objects.get(session_id=session_id)
            return list(session.messages.values('message_type', 'content', 'timestamp'))
        except ChatbotSession.DoesNotExist:
            return []

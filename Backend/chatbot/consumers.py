from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from decouple import config
from .models import ChatbotSession, ChatMessage
from .ecommerce_tools import search_products, add_to_cart, show_cart, show_order_details, tools
from openai import OpenAI

endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4.1"
token = config("GITHUB_TOKEN")
client = OpenAI(base_url=endpoint, api_key=token)


session_history = {}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.user_id = self.scope.get('user_id')
        try:
            self.session = await self.get_session(self.session_id, self.user_id)
            if self.session_id not in session_history:
                # Add system prompt as the first message
                session_history[self.session_id] = [
                    {
                        "role": "system",
                        "content": (
                            "You are an e-commerce assistant chatbot. "
                            "You can help users search for products, add items to their cart, "
                            "show cart details, and provide order information. "
                            "Always be helpful and concise."
                        ),
                    }
                ]
                messages = await self.get_session_messages(self.session_id)
                session_history[self.session_id] = [{"role": "user" if m["message_type"] == "user" else "system", "content": m["content"]} for m in messages]
            await self.accept()
        except ChatbotSession.DoesNotExist:
            await self.close()

    async def receive(self, text_data):
        if self.user_id and hasattr(self, 'session'):
            data = json.loads(text_data)
            is_bot = data.get('isBot', False)
            message = data.get('message')
            if not is_bot and message:
                session_history[self.session_id].append({"role": "user", "content": message})
                try:
                    bot_response = await self.get_response()
                except Exception as e:
                    bot_response = "Sorry, there was an error processing your request."
                    print(f"OpenAI error: {e}")
                await self.send_to_chat(message)
                session_history[self.session_id].append({"role": "system", "content": bot_response})
                await self.send_to_chat(bot_response, isBot=True)
                await self.save_message(self.session, message, isBot=False)
                await self.save_message(self.session, bot_response, isBot=True)

    async def get_response(self):
        try:
            response = client.chat.completions.create(
                messages=session_history.get(self.session_id, []),
                tools=tools,
                tool_choice="auto",
                temperature=1.0,
                top_p=1.0,
                model=model_name,
            )
            choice = response.choices[0]
            # Handle function call if present
            if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    params = json.loads(tool_call.function.arguments)
                    try:
                        if tool_name == "search_products":
                            tool_result = await search_products(params)
                        elif tool_name == "add_to_cart":
                            tool_result = await add_to_cart(params)
                        elif tool_name == "show_cart":
                            tool_result = await show_cart(params)
                        elif tool_name == "show_order_details":
                            tool_result = await show_order_details(params)
                        else:
                            tool_result = "Unknown tool requested."
                    except Exception as e:
                        tool_result = f"Error running tool: {str(e)}"
                    # Add tool result to history and get final AI response
                    session_history[self.session_id].append({"role": "function", "name": tool_name, "content": json.dumps(tool_result)})
                    # Ask the model to summarize or respond with the tool result
                    followup = client.chat.completions.create(
                        messages=session_history.get(self.session_id, []),
                        temperature=1.0,
                        top_p=1.0,
                        model=model_name,
                    )
                    return followup.choices[0].message.content
            # No tool call, just return the model's message
            return choice.message.content
        except Exception as e:
            print(f"Error in get_response: {e}")
            return "Sorry, I couldn't process your request."

    async def send_to_chat(self, message, isBot=False):
        await self.send(text_data=json.dumps({"message": message, "isBot": isBot}))

    @database_sync_to_async
    def save_message(self, session, message, isBot):
        ChatMessage.objects.create(message_type='bot' if isBot else 'user', content=message, session=session)

    @database_sync_to_async
    def get_session(self, session_id, user_id):
        return ChatbotSession.objects.get(session_id=session_id, user_id=user_id)

    @database_sync_to_async
    def get_session_messages(self, session_id):
        try:
            session = ChatbotSession.objects.get(session_id=session_id)
            return list(session.messages.values('message_type', 'content', 'timestamp'))
        except ChatbotSession.DoesNotExist:
            return []

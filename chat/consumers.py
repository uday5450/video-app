import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
            
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]
        self.username = self.user.email  # Use email as username

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send chat history
        messages = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = data['message']
            
            # Save message to database
            await self.save_message(message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.username,
                    'timestamp': timezone.now().isoformat()
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def chat_history(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': event['messages']
        }))

    @database_sync_to_async
    def get_chat_history(self):
        room, _ = Room.objects.get_or_create(name=self.room_name)
        messages = Message.objects.filter(room=room).order_by('-timestamp')[:50]
        return [
            {
                'message': msg.content,
                'username': msg.username,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in reversed(messages)
        ]

    @database_sync_to_async
    def save_message(self, message):
        room, _ = Room.objects.get_or_create(name=self.room_name)
        Message.objects.create(
            room=room,
            username=self.username,
            content=message
        ) 
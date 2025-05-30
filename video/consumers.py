import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import VideoRoom, Participant

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove participant from room
        if hasattr(self, 'username'):
            await self.remove_participant()
            
            # Notify others about participant leaving
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'username': self.username
                }
            )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'join':
            self.username = data['username']
            await self.add_participant()
            
            # Notify others about new participant
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'username': self.username
                }
            )
        elif message_type == 'offer':
            # Forward offer to specific user
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_offer',
                    'offer': data['offer'],
                    'username': self.username,
                    'target': data['target']
                }
            )
        elif message_type == 'answer':
            # Forward answer to specific user
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_answer',
                    'answer': data['answer'],
                    'username': self.username,
                    'target': data['target']
                }
            )
        elif message_type == 'ice':
            # Forward ICE candidate to specific user
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_ice',
                    'ice': data['ice'],
                    'username': self.username,
                    'target': data['target']
                }
            )

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username']
        }))

    async def webrtc_offer(self, event):
        if hasattr(self, 'username') and event['target'] == self.username:
            await self.send(text_data=json.dumps({
                'type': 'offer',
                'offer': event['offer'],
                'username': event['username']
            }))

    async def webrtc_answer(self, event):
        if hasattr(self, 'username') and event['target'] == self.username:
            await self.send(text_data=json.dumps({
                'type': 'answer',
                'answer': event['answer'],
                'username': event['username']
            }))

    async def webrtc_ice(self, event):
        if hasattr(self, 'username') and event['target'] == self.username:
            await self.send(text_data=json.dumps({
                'type': 'ice',
                'ice': event['ice'],
                'username': event['username']
            }))

    @database_sync_to_async
    def add_participant(self):
        room, _ = VideoRoom.objects.get_or_create(name=self.room_name)
        Participant.objects.get_or_create(
            room=room,
            username=self.username
        )

    @database_sync_to_async
    def remove_participant(self):
        try:
            participant = Participant.objects.get(
                room__name=self.room_name,
                username=self.username
            )
            participant.delete()
        except Participant.DoesNotExist:
            pass 
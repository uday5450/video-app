import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import VideoRoom, Participant
from asgiref.sync import sync_to_async

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
            
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_{self.room_name}'
        self.user = self.scope["user"]
        self.username = self.user.email  # Use email as username

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Get current active users and send to the new participant
        active_users = await self.get_active_users()
        await self.send(text_data=json.dumps({
            'type': 'active_users_list',
            'users': active_users
        }))

        # Send join message automatically after connection
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.username,
                'hasVideo': True,
                'hasAudio': True,
                'users': active_users
            }
        )

    async def disconnect(self, close_code):
        # Remove participant from room
        if hasattr(self, 'username'):
            await self.remove_participant()
            
            # Get updated active users list
            active_users = await self.get_active_users()
            
            # Notify others about participant leaving and send updated list
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'username': self.username,
                    'users': active_users
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
            # Get media status from join message
            has_video = data.get('hasVideo', False)
            has_audio = data.get('hasAudio', False)
            
            # Add or update participant
            await self.add_participant(has_video, has_audio)
            
            # Get current active users
            active_users = await self.get_active_users()
            
            # Send active users list to all participants
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'active_users_list',
                    'users': active_users
                }
            )

        elif message_type == 'update_status':
            # Update participant status
            has_video = data.get('hasVideo', False)
            has_audio = data.get('hasAudio', False)
            await self.update_participant_status(has_video, has_audio)
            
            # Get updated active users list
            active_users = await self.get_active_users()
            
            # Notify all participants about the status update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'active_users_list',
                    'users': active_users
                }
            )

        elif message_type in ['video_offer', 'video_answer', 'ice_candidate']:
            # Forward WebRTC signaling messages to the target user
            target_username = data.get('target')
            if target_username:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': message_type,
                        'username': self.username,
                        'target': target_username,
                        'offer': data.get('offer'),
                        'answer': data.get('answer'),
                        'candidate': data.get('candidate')
                    }
                )

    async def video_offer(self, event):
        if event['target'] == self.username:
            await self.send(text_data=json.dumps({
                'type': 'video_offer',
                'username': event['username'],
                'offer': event['offer']
            }))

    async def video_answer(self, event):
        if event['target'] == self.username:
            await self.send(text_data=json.dumps({
                'type': 'video_answer',
                'username': event['username'],
                'answer': event['answer']
            }))

    async def ice_candidate(self, event):
        if event['target'] == self.username:
            await self.send(text_data=json.dumps({
                'type': 'ice_candidate',
                'username': event['username'],
                'candidate': event['candidate']
            }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'hasVideo': event.get('hasVideo', False),
            'hasAudio': event.get('hasAudio', False),
            'users': event.get('users', [])
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'users': event.get('users', [])
        }))

    async def active_users_list(self, event):
        await self.send(text_data=json.dumps({
            'type': 'active_users_list',
            'users': event['users']
        }))

    @database_sync_to_async
    def add_participant(self, has_video=False, has_audio=False):
        room, _ = VideoRoom.objects.get_or_create(name=self.room_name)
        
        # Update or create participant
        participant, created = Participant.objects.get_or_create(
            room=room,
            user=self.user,
            defaults={
                'has_video': has_video,
                'has_audio': has_audio,
                'is_active': True
            }
        )
        
        if not created:
            # Update existing participant's status
            participant.has_video = has_video
            participant.has_audio = has_audio
            participant.is_active = True
            participant.save()

    @database_sync_to_async
    def update_participant_status(self, has_video, has_audio):
        try:
            participant = Participant.objects.get(
                room__name=self.room_name,
                user=self.user
            )
            participant.has_video = has_video
            participant.has_audio = has_audio
            participant.save()
        except Participant.DoesNotExist:
            pass

    @database_sync_to_async
    def remove_participant(self):
        try:
            participant = Participant.objects.get(
                room__name=self.room_name,
                user=self.user
            )
            # Instead of just marking inactive, delete the participant
            participant.delete()
        except Participant.DoesNotExist:
            pass

    @database_sync_to_async
    def get_active_users(self):
        try:
            room = VideoRoom.objects.get(name=self.room_name)
            # Only get participants that are marked as active
            participants = Participant.objects.filter(
                room=room,
                is_active=True
            ).select_related('user')
            
            return [
                {
                    'username': p.user.email,
                    'hasVideo': p.has_video,
                    'hasAudio': p.has_audio,
                    'isActive': True
                }
                for p in participants
            ]
        except VideoRoom.DoesNotExist:
            return [] 
from rest_framework import serializers
from .models import VideoRoom, Participant

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'username', 'joined_at']

class VideoRoomSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = VideoRoom
        fields = ['id', 'name', 'created_at', 'participants'] 
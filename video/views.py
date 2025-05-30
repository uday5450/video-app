from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import VideoRoom, Participant
from .serializers import VideoRoomSerializer, ParticipantSerializer
from django.views.generic import TemplateView

# Create your views here.

class VideoRoomListCreateView(generics.ListCreateAPIView):
    queryset = VideoRoom.objects.all()
    serializer_class = VideoRoomSerializer

class VideoRoomDetailView(generics.RetrieveAPIView):
    queryset = VideoRoom.objects.all()
    serializer_class = VideoRoomSerializer
    lookup_field = 'name'

class ParticipantListView(generics.ListAPIView):
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        room_name = self.kwargs['room_name']
        return Participant.objects.filter(room__name=room_name)

class RoomView(TemplateView):
    template_name = 'room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_name'] = self.kwargs.get('room_name')
        return context

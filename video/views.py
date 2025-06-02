from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, LoginForm
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import VideoRoom, Participant
from .serializers import VideoRoomSerializer, ParticipantSerializer
from django.views.generic import TemplateView

# Create your views here.

class VideoRoomListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VideoRoom.objects.all()
    serializer_class = VideoRoomSerializer

    def perform_create(self, serializer):
        serializer.save()

class VideoRoomDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VideoRoom.objects.all()
    serializer_class = VideoRoomSerializer
    lookup_field = 'name'

class ParticipantListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        room_name = self.kwargs['room_name']
        return Participant.objects.filter(room__name=room_name, is_deleted=False)

    def perform_create(self, serializer):
        room_name = self.kwargs['room_name']
        room = VideoRoom.objects.get(name=room_name)
        serializer.save(room=room, user=self.request.user)

class RoomView(TemplateView):
    template_name = 'room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_name'] = self.kwargs.get('room_name')
        return context

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('video:index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            next_url = request.GET.get('next', 'video:index')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('video:login')

@login_required(login_url='video:login')
def index(request):
    return render(request, 'index.html')

@login_required(login_url='video:login')
def room(request, room_name):
    # Create or get room
    room, created = VideoRoom.objects.get_or_create(name=room_name)
    
    # Create or update participant
    participant, created = Participant.objects.get_or_create(
        room=room,
        user=request.user,
        is_deleted=False, 
        defaults={
            'is_active': True,
            'has_video': True,
            'has_audio': True
        }
    )
    
    if not created:
        participant.is_active = True
        participant.save()
    
    return render(request, 'room.html', {
        'room_name': room_name,
        'user_email': request.user.email
    })

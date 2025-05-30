from django.urls import path
from . import views

app_name = 'video'

urlpatterns = [
    path('rooms/', views.VideoRoomListCreateView.as_view(), name='room-list'),
    path('rooms/<str:name>/', views.VideoRoomDetailView.as_view(), name='room-detail'),
    path('rooms/<str:room_name>/participants/', views.ParticipantListView.as_view(), name='participant-list'),
] 
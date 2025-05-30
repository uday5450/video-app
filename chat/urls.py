from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('rooms/', views.RoomListCreateView.as_view(), name='room-list'),
    path('rooms/<str:name>/', views.RoomDetailView.as_view(), name='room-detail'),
    path('rooms/<str:room_name>/messages/', views.MessageListView.as_view(), name='message-list'),
] 
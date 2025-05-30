from django.urls import path
from . import views

app_name = 'video'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main application URLs
    path('', views.index, name='index'),
    path('room/<str:room_name>/', views.room, name='room'),
    
    # API URLs
    path('api/rooms/', views.VideoRoomListCreateView.as_view(), name='room-list'),
    path('api/rooms/<str:name>/', views.VideoRoomDetailView.as_view(), name='room-detail'),
    path('api/rooms/<str:room_name>/participants/', views.ParticipantListView.as_view(), name='participant-list'),
] 
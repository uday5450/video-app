from django.contrib import admin
from video.models import VideoRoom, Participant

@admin.register(VideoRoom)
class VideoRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('room', 'joined_at')
    search_fields = ('room__name',)

# Register your models here.

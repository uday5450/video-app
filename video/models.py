from django.db import models
from django.utils import timezone

class VideoRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Participant(models.Model):
    room = models.ForeignKey(VideoRoom, related_name='participants', on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['room', 'username']

    def __str__(self):
        return f'{self.username} in {self.room.name}'

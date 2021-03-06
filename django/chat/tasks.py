from django.contrib.auth import get_user_model
from celery import shared_task

from .models import (
    Room,
    Message,
)


@shared_task
def create_message(room_name, username, content):
    Message.objects.create(
        room=Room.objects.get(name=room_name),
        author=get_user_model().objects.get(username=username),
        content=content,
    )

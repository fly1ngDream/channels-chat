from django.utils import timezone
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from .models import (
    Room,
    Message,
)

from .tasks import (
    create_message,
)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope.get('url_route').get('kwargs').get('room_name')
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        room_name = text_data_json.get('room_name')
        username = text_data_json.get('username')
        message = text_data_json.get('message')

        create_message.delay(
            room_name=room_name,
            username=username,
            content=message,
        )

        timestamp = timezone.localtime(timezone.now()).strftime('%d.%m.%Y, %H:%M')

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'room_name': room_name,
                'username': username,
                'message': message,
                'timestamp': timestamp,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        username = event.get('username')
        message = event.get('message')
        room_name = event.get('room_name')
        timestamp = event.get('timestamp')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'room_name': room_name,
            'username': username,
            'message': message,
            'timestamp': timestamp,
        }))

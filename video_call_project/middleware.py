from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from urllib.parse import parse_qs

class WebSocketAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the user from the scope
        if "user" not in scope:
            scope["user"] = AnonymousUser()
            
        if scope["type"] == "websocket":
            # Check if user is authenticated
            if not scope["user"].is_authenticated:
                # Close the connection if user is not authenticated
                return None
                
        return await super().__call__(scope, receive, send) 
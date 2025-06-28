"""
ASGI config for video_call_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_call_project.settings')
# from django.core.asgi import get_asgi_application
# django_asgi_app = get_asgi_application()

# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator
# from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
# from video.routing import websocket_urlpatterns as video_websocket_urlpatterns
# from .middleware import WebSocketAuthMiddleware

# # Custom middleware to handle ngrok headers
# class NgrokWebSocketMiddleware:
#     def __init__(self, app):
#         self.app = app

#     async def __call__(self, scope, receive, send):
#         if scope["type"] == "websocket":
#             # Check for X-Forwarded-Proto header
#             headers = dict(scope.get("headers", []))
#             if b"x-forwarded-proto" in headers:
#                 if headers[b"x-forwarded-proto"] == b"https":
#                     scope["scheme"] = "wss"
#                 else:
#                     scope["scheme"] = "ws"
#         return await self.app(scope, receive, send)

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": NgrokWebSocketMiddleware(
#         AllowedHostsOriginValidator(
#             AuthMiddlewareStack(
#                 WebSocketAuthMiddleware(
#                     URLRouter(
#                         video_websocket_urlpatterns +
#                         chat_websocket_urlpatterns
#                     )
#                 )
#             )
#         )
#     ),
# })


import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from video.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "video_call_project.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

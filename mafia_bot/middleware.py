from aiogram import BaseMiddleware
from django.db import close_old_connections

class DjangoDBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Drop connections that have exceeded CONN_MAX_AGE / gone stale before and
        # after handling the update, instead of force-closing every connection on
        # every update (which kills connection reuse and adds reconnect latency).
        close_old_connections()
        try:
            return await handler(event, data)
        finally:
            close_old_connections()

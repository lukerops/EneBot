import re
import logging
import asyncio

from functools import wraps

log = logging.getLogger('discord')

def command(description="", usage=None):
    def actual_decorator(func):
        name = func.__name__
        @wraps(func)
        async def wrapper(self, message):
            args = message.content.split(' ')
            try:
                args.pop(args.index(usage))
            except:
                return

            await func(self, message, args)
        wrapper._is_command = True
        if usage:
            command_name = usage
        else:
            command_name = func.__name__
        wrapper.info = {"name": command_name,
                        "description": description}
        return wrapper
    return actual_decorator

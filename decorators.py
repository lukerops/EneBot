import re
import logging
import asyncio

from functools import wraps

log = logging.getLogger('discord')

def command(description="", usage=None):
    def actual_decorator(func):
        name = func.__name__
        
        if usage:
            command_name = usage
        else:
            command_name = name
            
        @wraps(func)
        async def wrapper(self, message):
            args = list()
            for arg in message.content.split(' '):
                if arg is not "" and len(arg) is not 0 and arg is not None:
                    args.append(arg)

            await func(self, message, args)
        
        wrapper._is_command = True
        wrapper.info = {"name": command_name,
                        "description": description}
        return wrapper
    return actual_decorator

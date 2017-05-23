import re
import logging
import asyncio

from functools import wraps

log = logging.getLogger('discord')

def command(description="", usage=None):
    def actual_decorator(func):
        name = func.__name__
        prog = re.compile(usage)
        @wraps(func)
        async def wrapper(self, message):
            match = prog.match(message.content)
            if not match:
                return

            args = match.groups()
            await func(self, message, args)
        wrapper._is_command = True
        if usage:
            command_name = usage
        else:
            command_name = "ene!" + func.__name__
        wrapper.info = {"name": command_name,
                        "description": description}
        return wrapper
    return actual_decorator

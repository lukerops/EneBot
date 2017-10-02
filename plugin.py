import inspect
import logging
import copy

log = logging.getLogger('discord')

class PluginMeta(type):
    def __init__(cls, name, bases, attrs):
        #é chamado quando uma subclasse é importada
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class Plugin(metaclass=PluginMeta):
    plugin_name = None
    plugin_version = ''
    plugin_description = ''
    is_global = False
    is_beta = False

    def __init__(self, ene):
        self.commands = {}
        self.ene = ene

        for name, member in inspect.getmembers(self):
            # registering commands
            if hasattr(member, '_is_command'):
                self.commands[member.__name__] = member
        log.info("Registered {} commands".format(
            len(self.commands)
        ))

    async def on_ready(self):
        pass

    async def _on_message(self, message):
        if self.ene.prefix == message.content[:len(self.ene.prefix)]:
            message_aux = copy.deepcopy(message)
            message_aux.content = message_aux.content[len(self.ene.prefix):]

            command = message_aux.content.split(" ")[0]
            message_aux.content = message_aux.content[len(command):]

            for command_name, func in self.commands.items():
                if command_name == command:
                    await func(message_aux)
                    await self.ene._delete_message(message, self.ene.wait_time)
                    break
        await self.on_message(message)

    async def on_message(self, message):
        pass

    async def on_message_edit(self, before, after):
        pass

    async def on_message_delete(self, message):
        pass

    async def on_channel_create(self, channel):
        pass

    async def on_channel_update(self, before, after):
        pass

    async def on_channel_delete(self, channel):
        pass

    async def on_member_join(self, member):
        pass

    async def on_member_remove(self, member):
        pass

    async def on_member_update(self, before, after):
        pass

    async def on_server_join(self, server):
        pass

    async def on_server_update(self, before, after):
        pass

    async def on_server_role_create(self, server, role):
        pass

    async def on_server_role_delete(self, server, role):
        pass

    async def on_server_role_update(self, server, role):
        pass

    async def on_voice_state_update(self, before, after):
        pass

    async def on_member_ban(self, member):
        pass

    async def on_member_unban(self, member):
        pass

    async def on_typing(self, channel, user, when):
        pass

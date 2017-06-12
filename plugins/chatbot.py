import logging
from cleverbot import Cleverbot

from plugin import Plugin

log = logging.getLogger('discord')

class ChatBot(Plugin):
    plugin_name = 'ChatBot'
    plugin_version = '0.0.1'
    plugin_description = 'Permite a interação com o bot.'
    is_global = True
    is_beta = False

    def __init__(self, ene):
        super(ChatBot, self).__init__(ene)
        self.cb = Cleverbot("Ene")

    async def _on_message(self, message):
        enabled_plugins = await self.ene.plugin_manager.get_plugins()
        enabled_plugins = sorted(enabled_plugins, key=lambda p: type(p).__name__)

        for plugin in enabled_plugins:
            plugins = await plugin.get_help_info()
            for command in plugins["commands"]:
                if message.content.find(command["name"]) >= 0:
                    return
        await self.ene.send_message(message.channel, self.cb.ask(message.content))
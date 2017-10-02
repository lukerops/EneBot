import logging

from plugin import Plugin
from decorators import command

log = logging.getLogger('discord')

async def get_help_info(self):
    if self.plugin_name is None:
        self.plugin_name = type(self).__name__

    commands = []
    for cmd in self.commands.values():
        commands.append(cmd.info)
    if hasattr(self, "get_commands"):
        commands += await self.get_commands()
    payload = {
        'plugin_name': self.plugin_name,
        'plugin_version': self.plugin_version,
        'plugin_description': self.plugin_description,
        'commands': commands
    }
    return payload

class Help(Plugin):
    plugin_name = 'Help'
    plugin_version = '0.0.1'
    plugin_description = 'Gera mensagem de ajuda.'
    is_global = True
    is_beta = False

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        # Patch the Plugin class
        Plugin.get_help_info = get_help_info

    async def generate_help(self):
        enabled_plugins = await self.ene.plugin_manager.get_plugins()
        enabled_plugins = sorted(enabled_plugins, key=lambda p: type(p).__name__)

        help_payload = []
        for plugin in enabled_plugins:
            '''if not isinstance(plugin, Help):
                help_info = await plugin.get_help_info()
                help_payload.append(help_info)'''

            help_info = await plugin.get_help_info()
            help_payload.append(help_info)

        return self.render_message(help_payload)

    def render_message(self, help_payload):
        message_batches = [""]
        for plugin_info in help_payload:
            if plugin_info['commands'] != []:
                message = "**{}** v{} {}\n".format(plugin_info['plugin_name'], plugin_info['plugin_version'], plugin_info['plugin_description'])
                if len(message_batches[-1] + message) > 2000:
                    message_batches.append(message)
                else:
                    message_batches[-1] += message
            for cmd in plugin_info['commands']:
                message = "    **{}** {}\n".format(self.ene.prefix + cmd['name'], cmd.get('description', ''))
                if len(message_batches[-1] + message) > 2000:
                    message_batches.append(message)
                else:
                    message_batches[-1] += message
        return message_batches

    @command(usage='show_plugins', description='Mostra todos os plugins carregados.')
    async def show_plugins(self, message, *args):
        plugins = await self.ene.plugin_manager.get_plugins()
        plugins = sorted(plugins, key=lambda p: type(p).__name__)
        messages = '**Plugins**\n'
        for plugin in plugins:
            messages += '    **{}** v{} - {}\n'.format(plugin.plugin_name, plugin.plugin_version, plugin.plugin_description)
        await self.ene._send_message(message.channel, messages)

    @command(usage='help', description='Mostra menssagem de ajuda.')
    async def help(self, message, *args):
        if message.author.bot or message.author.id == self.ene.user.id:
            return
        help_messages = await self.generate_help()
        if help_messages == [""]:
            help_messages = ["There's no command to show :cry:"]
        for msg in help_messages:
            await self.ene._send_message(message.channel, msg)

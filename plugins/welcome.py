import logging

from plugin import Plugin

log = logging.getLogger('discord')

class Welcome(Plugin):
    plugin_name = 'Welcome'
    plugin_version = '0.0.1'
    plugin_description = 'Gera menssagem de ajuda.'
    is_global = True
    is_beta = False

    async def on_member_join(self, member):
        message = 'Bem vindo ao server {} :wink:'.format(member.mention)
        destination = member.server
        await self.ene.send_message(destination, message)

    async def on_member_remove(self, member):
        message = 'Bye Bye {} :kissing_smiling_eyes:'.format(member.name)
        destination = member.server
        await self.ene.send_message(destination, message)

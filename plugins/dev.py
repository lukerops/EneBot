import logging
from decorators import command
from plugin import Plugin

log = logging.getLogger('discord')

class Dev(Plugin):
    plugin_name = 'Developer'
    plugin_version = '0.0.1'
    plugin_description = 'Comandos de Desenvolvedor'
    is_global = True
    is_beta = False

    @command(usage='shutdown', description="Desliga o bot")
    async def shutdown(self, message, *args):
        if message.author.id in self.ene.devs:
            for server in self.ene.servers:
                try:
                    await self.ene._send_message(server.default_channel, 'Estou indo dormir, até mais galera!! :wave:')
                except:
                    log.info('Error sent menssage to {}!'.format(server.name))
            self.ene.loop.create_task(self.ene._shutdown())
        else:
            await self.ene._send_message(message.channel, '{0.author.mention} Você não tem permissão para isso!'.format(message))

    @command(usage='restart', description="Reinicia o bot")
    async def restart(self, message, *args):
        if message.author.id in self.ene.devs:
            for server in self.ene.servers:
                try:
                    await self.ene._send_message(server.default_channel, 'Estou indo ali tomar um ar! Já volto galera!! ^^')
                except:
                    log.info('Error sent menssage to {}!'.format(server.name))
            self.ene.loop.create_task(self.ene._restart())
        else:
            await self.ene._send_message(message.channel, '{0.author.mention} Você não tem permissão para isso!'.format(message))

    @command(usage='advertisement', description="Envia uma mensagem para todos os servidores")
    async def advertisement(self, message, *args):
        if message.author.id in self.ene.devs:
            for server in self.ene.servers:
                try:
                    await self.ene._send_message(server.default_channel, '{0}'.format(message.content))
                except:
                    log.info('Error sent menssage to {}!'.format(server.name))

    @command(usage='server_list', description="Mostra a lista de todos os servidores")
    async def server_list(self, message, *args):
        if message.author.id in self.ene.devs:
            fmt = ''
            for server in self.ene.servers:
                fmt += 'Server: ' + server.name + '\tID: ' + server.id + '\n'
                await self.ene._send_message(message.channel, '```####	Lista de servers	####```\n{0}'.format(fmt))

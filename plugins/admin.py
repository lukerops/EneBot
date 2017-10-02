import logging
import os
import datetime
from decorators import command
from plugin import Plugin

log = logging.getLogger('discord')

class Admin(Plugin):
    plugin_name = 'Administration'
    plugin_version = '0.0.2'
    plugin_description = 'Comandos de Administrador'
    is_global = True
    is_beta = False

    @command(usage='status', description='Mostra os status do servidor')
    async def status(self, message, *args):
        tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
        music_plugin = await self.ene.plugin_manager.get_plugin("Music")
        voice_connections = len(music_plugin.voice_states)

        msg = "Status\n"
        msg += "Version: {}\n".format(self.ene.version)
        msg += "Ram: {}/{}\n".format(used_m, tot_m)
        msg += "Voice Connections: {}\n".format(voice_connections)

        await self.ene._send_message(message.channel, msg)

    @command(usage='kick', description="Kicka um usuário do servidor")
    async def kick(self, message, *args):
        if message.server.get_member(self.ene.user.id).permissions_in(message.channel).kick_members == True:
            if message.author.permissions_in(message.channel).kick_members == True or message.author.id in self.ene.devs:
                for member in message.mentions:
                    await self.ene.kick(member)
            else:
                await self.ene._send_message(message.channel, '{0.author.mention} Você não tem permissão para isso!'.format(message))
        else:
            await self.ene._send_message(message.channel, 'Eu não tenho permissão para isso!'.format(message))

    @command(usage='ban', description="Bane um usuário do servidor")
    async def ban(self, message, *args):
        if message.server.get_member(self.ene.user.id).permissions_in(message.channel).ban_members == True:
            if message.author.permissions_in(message.channel).ban_members == True or message.author.id in self.ene.devs:
                for member in message.mentions:
                    await self.ene.ban(member, delete_message_days=1)
            else:
                await self.ene._send_message(message.channel, '{0.author.mention} Você não tem permissão para isso!'.format(message))
        else:
            await self.ene._send_message(message.channel, 'Eu não tenho permissão para isso!'.format(message))

    @command(usage='clear_chat', description="Apaga todas as mensagens do chat")
    async def clear_chat(self, message, limit):
        if message.server.get_member(message.author.id).permissions_in(message.channel).manage_messages == True:
            if message.server.get_member(self.ene.user.id).permissions_in(message.channel).manage_messages == True:
                count = 0
                async for msg in self.ene.logs_from(message.channel, limit=int(limit[0]) if len(limit) > 0 and len(limit[0]) > 0 else 100):
                    try: #if (datetime.datetime.today() - msg.timestamp).days <= 14:
                        await self.ene.delete_message(msg)
                        count += 1
                    except: #else:
                        break
                await self.ene._send_message(message.channel, '{0} Menssagens apagadas!'.format(count))
            else:
                await self.ene._send_message(message.channel, '{0.author.mention} Desculpe, mas eu não tenho permissões para apagar as mensagens!'.format(message))
        else:
            await self.ene._send_message(message.channel, '{0.author.mention} Desculpe, mas você não pode apagar as mensagens!'.format(message))

    '''@command(usage='clear_user', description="Apaga todas as mensagens de um usuario no chat")
    async def clear_user(self, message, *args):
        if message.server.get_member(message.author.id).permissions_in(message.channel).manage_messages == True:
	    if message.server.get_member(self.ene.user.id).permissions_in(message.channel).manage_messages == True:
		num = await self.ene.purge_from(message.channel, limit=1000000000)
		message = await bot.send_message(msg.channel, '{0} Menssagens apagadas!'.format(num))
		time.sleep(20)
		await on_delete_message(message)
	    else:
		await bot.send_message(msg.channel, '{0.author.mention} Desculpe, mas eu não tenho permissões para apagar as mensagens!'.format(msg))
	else:
	    await bot.send_message(msg.channel, '{0.author.mention} Desculpe, mas você não pode apagar as mensagens!'.format(msg))'''

    @command(usage='show_devs', description="Mostra a lista dos desenvolvedores do bot")
    async def show_devs(self, message, *args):
        fmt = ''
        for dev in self.ene.devs_name:
            fmt += 'Nick: ' + dev[0] + ' Discord ID: ' + dev[1] + '\n'
        await self.ene._send_message(message.channel, '```####	Lista de Desenvolvedores	####```\n{0}'.format(fmt))

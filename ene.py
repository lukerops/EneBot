import discord
import asyncio
import logging
import time
import sys
import os

from plugin_manager import PluginManager
import plugins

log = logging.getLogger('discord')

class Ene(discord.Client):
    #Bot Version
    version = '0.0.2'
    
    def __init__(self, file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__file__ = file
        self.prefix = 'ene!' if kwargs.get('prefix') is None else kwargs.get('prefix')
        self.wait_time = 15 if kwargs.get('wait_time') is None else kwargs.get('wait_time')
        
        self.plugin_manager = PluginManager(self)
        self.plugin_manager.load_all()

        self.devs = ['201451679084838912', '323996712630878219']
        self.devs_name = [['Lusca', '3948'], ['dINH0', '4686']]

        self.set_bot_region('BR' if kwargs.get('region') is None else kwargs.get('region'))

    def set_bot_region(self, region):
        if region is 'BR':
            self.region = discord.ServerRegion.brazil

    def run(self, *args, **kwargs):
        if kwargs.get('token'):
            self.token = kwargs.get('token')
        elif len(args) == 1:
            self.token = args[0]
        super().run(*args, **kwargs)

    async def _shutdown(self):
        await asyncio.sleep(2*self.wait_time)
        await self.logout()

    async def _restart(self):
        await self._shutdown()
        time.sleep(15)
        os.execl(sys.executable, 'python', self.__file__, self.token)

    async def _send_message(self, channel, message, *args, **kwarg):
        if channel.server.get_member(self.user.id).permissions_in(channel).send_messages == True:
            response = await self.send_message(channel, message, *args, **kwarg)
            self.loop.create_task(self._delete_message(response, self.wait_time))
        else:
            pass

    async def _delete_message(self, message, t):
        await asyncio.sleep(t)
        try:
            await self.delete_message(message)
        except:
            pass

    async def on_ready(self):
        log.info('Connected')

        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_ready())

    async def add_all_servers(self):
        pass

    async def on_server_join(self, server):
        log.info('Joined {} server : {} !'.format(
            server.owner.name,
            server.name
        ))
        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            if plugin.is_global:
                self.loop.create_task(plugin.on_server_join(server))

    async def on_server_remove(self, server):
        log.info('Leaving {} server : {} !'.format(
            server.owner.name,
            server.name
        ))

    async def on_message(self, message):
        if message.author.__class__ != discord.Member and message.author.__class__ != discord.User :
            return

        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin._on_message(message))

    async def on_message_edit(self, before, after):
        if before.channel.is_private:
            return

        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_message_edit(before, after))

    async def on_message_delete(self, message):
        if message.channel.is_private:
            return

        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_message_delete(message))

    async def on_channel_create(self, channel):
        if channel.is_private:
            return

        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_channel_create(channel))

    async def on_channel_update(self, before, after):
        if before.is_private:
            return

        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_channel_update(before, after))

    async def on_channel_delete(self, channel):
        if channel.is_private:
            return

        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_channel_delete(channel))

    async def on_member_join(self, member):
        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_member_join(member))

    async def on_member_remove(self, member):
        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_member_remove(member))

    async def on_member_update(self, before, after):
        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_member_update(before, after))

    async def on_server_update(self, before, after):
        plugins = await self.plugin_manager.get_plugins()
        for plugin in plugins:
            self.loop.create_task(plugin.on_server_update(before, after))

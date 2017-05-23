import discord
import asyncio
import logging
from plugin_manager import PluginManager

log = logging.getLogger('discord')

class Ene(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = 'ene!' if kwargs.get('prefix') is None else kwargs.get('prefix')
        self.plugin_manager = PluginManager(self)
        self.plugin_manager.load_all()

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
        log.debug('Adding server {}\'s id to db'.format(server.id))
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
        '''if message.channel.is_private:
            return'''
        if message.author.__class__ != discord.Member and message.author.__class__ != discord.User :
            return

        message.content = message.content[len(self.prefix):]
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

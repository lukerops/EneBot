import logging
from plugin import Plugin

log = logging.getLogger('discord')

class PluginManager:
    def __init__(self, ene):
        self.plugins = []
        self.ene = ene

    def load(self, plugin):
        log.info('Loading plugin {}.'.format(plugin.__name__))
        plugin_instance = plugin(self.ene)
        self.plugins.append(plugin_instance)
        log.info('Plugin {} version {} loaded.'.format(plugin.__name__, plugin.plugin_version))

    def load_all(self):
        for plugin in Plugin.plugins:
            self.load(plugin)

    async def get_plugins(self):
        plugins = []
        for plugin in self.plugins:
            if plugin.is_global:
                plugins.append(plugin)
            if plugin.is_beta:
                pass
        return plugins

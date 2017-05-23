from ene import Ene
import sys
import logging
from plugins.help import Help
from plugins.welcome import Welcome

bot_debug = False

if bot_debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

if len(sys.argv) > 1:
    bot = Ene(prefix = 'ene!')
    bot.run(sys.argv[1])
else:
    print('O token é necessário como parametro!')
#https://discordapp.com/api/oauth2/authorize?client_id=286323989393965058&scope=bot&permissions=18222814

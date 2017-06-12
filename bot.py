from ene import Ene
import sys
import logging
from plugins.help import Help
from plugins.welcome import Welcome
from plugins.music import Music
#from plugins.chatbot import ChatBot

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
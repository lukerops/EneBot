from ene import Ene
import sys
import logging

bot_debug = False

if bot_debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

if len(sys.argv) > 1:
    bot = Ene(__file__)
    bot.run(sys.argv[1])
else:
    print('O token é necessário como parametro!')
#https://discordapp.com/api/oauth2/authorize?client_id=286323989393965058&scope=bot&permissions=18222814

#teste
#https://discordapp.com/api/oauth2/authorize?client_id=359134319324954624&scope=bot&permissions=18222814

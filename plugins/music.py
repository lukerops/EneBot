import logging
from plugin import Plugin
from decorators import command
import functools
import re
import urllib.request
import urllib.error
import discord
import asyncio
import youtube_dl

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

class PlayList:
    def __init__(self, ydl, msg, download_url, url, duration, uploader, title):
        self.ydl = ydl
        self.msg = msg
        self.download_url = download_url
        self.url = url
        self.duration = duration
        self.uploader = uploader
        self.title = title

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '`{0.title}` upado por `{0.uploader}` e requisitado por `{1.display_name}`'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' **[duração: {0[0]}m {0[1]}s]**'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, ene, server, music):
        self.current = None
        self.voice = None
        self.vol = 0.6
        self.ene = ene
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.ene.loop.create_task(self.audio_player_task())
        self.server = server
        self.music = music

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        queue_size = self.songs.qsize()
        if queue_size == 0:
            #self.ene.loop.create_task(self.voice.disconnect())
            #self.voice = None
            self.ene.loop.create_task(self.music.disconnect(self.server))
        self.skip_votes.clear()
        self.ene.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        opts = {
            'format': 'webm[abr>0]/bestaudio/best',
            'noplaylist': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'logtostderr': False,
            'quiet': True,
            'default_search': 'auto',
            'prefer_ffmpeg': True
        }
        while True:
            self.play_next_song.clear()
            entry = await self.songs.get()
            entry.player = await self.voice.create_ytdl_player(entry.player.url, ytdl_options=opts, after=self.toggle_next)
            self.current = entry
            await self.ene._send_message(self.current.channel, '**[Musica]** Tocando ' + str(self.current))
            self.current.player.start()
            self.current.player.volume = self.vol
            await self.play_next_song.wait()

class Music(Plugin):
    plugin_name = 'Music'
    plugin_version = '0.0.2'
    plugin_description = 'Toca musicas.'
    is_global = True
    is_beta = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.ene, server, self)
            self.voice_states[server.id] = state

        return state


    async def create_voice_client(self, channel):
        voice = await self.ene.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice


    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.ene.loop.create_task(state.voice.disconnect())
            except:
                pass


    async def join(self, msg, channel: discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.ene._send_message(msg.channel, 'Already in a voice channel...')
        except discord.InvalidArgument:
            await self.ene._send_message(msg.channel, 'This is not a voice channel...')
        else:
            await self.ene._send_message(msg.channel, 'Ready to play audio in ' + channel.name)


    async def summon(self, msg):
        """Summons the bot to join your voice channel."""
        summoned_channel = msg.author.voice_channel
        if summoned_channel is None:
            await self.ene._send_message(msg.channel, 'Você não está em um canal de voz.')
            return False

        state = self.get_voice_state(msg.server)
        if state.voice is None:
            state.voice = await self.ene.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @command(usage='play', description='Adiciona um link a playlist')
    async def play(self, message, url):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(message.server)

        if state.voice is None:
            success = await self.summon(message)
            if not success:
                return

        if len(url) > 1:
            for i in range(len(url) - 1):
                message.content = url[i]
                await self.play(message)
            url = url[-1]
        else:
            url = url[0]

        if not 'watch?v=' in url and 'list=' in url and 'youtube' in url:
            nlist = url.find('list=')
            elist = url.find('&', nlist)
            if elist != -1:
                url = url[:elist]

            sTUBE = ''
            cPL = ''
            amp = 0
            final_url = []

            eq = url.rfind('=') + 1
            cPL = url[eq:]

            try:
                yTUBE = urllib.request.urlopen(url).read()
                sTUBE = str(yTUBE)
            except urllib.error.URLError as e:
                print(e.reason)
                return

            tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
            mat = re.findall(tmp_mat, sTUBE)

            if mat:
                await self.ene._send_message(message.channel, '**Adicionando Playlist...**')

                for PL in mat:
                    yPL = str(PL)
                    if '&' in yPL:
                        yPL_amp = yPL.index('&')
                    final_url.append('http://www.youtube.com/' + yPL[:yPL_amp])

                all_url = list(set(final_url))

                for i in range(len(all_url) - 1):
                    message.content = all_url[i]
                    await self.play(message)
                    '''await self.play(message, all_url[i])'''

                url = all_url[-1]

            else:
                await self.ene._send_message(message.channel, 'Nenhum video encontrado nesse link')
                return

        try:
            playlist = await self.get_video_data(message, url, state.voice.loop)

        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.ene._send_message(message.channel, fmt.format(type(e).__name__, e))
        else:
            entry = VoiceEntry(message, playlist)
            await self.ene._send_message(message.channel, '**[Musica]** Adicionado ' + str(entry))
            await state.songs.put(entry)

    @command(usage='volume', description='Muda o volume da musica.')
    async def volume(self, msg, value):
        """Sets the volume of the currently playing song."""

        value = float(value[0])/100

        state = self.get_voice_state(msg.server)
        if state.is_playing():
            player = state.player
            player.volume = state.vol = value
            await self.ene._send_message(msg.channel, 'Mudando volume para {:.0%}'.format(player.volume))

    @command(usage='pause', description='Pausa a musica.')
    async def pause(self, msg, *args):
        """Pauses the currently played song."""
        state = self.get_voice_state(msg.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @command(usage='resume', description='Volta a tocar a musica pausada.')
    async def resume(self, msg, *args):
        """Resumes the currently played song."""
        state = self.get_voice_state(msg.server)
        if state.is_playing():
            player = state.player
            player.resume()


    async def disconnect(self, server):
        state = self.get_voice_state(server)

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @command(usage='stop', description='Para a playlist atual.')
    async def stop(self, msg, *args):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = msg.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @command(usage='skip', description='Muda para a próxima música da playlist.')
    async def skip(self, msg, *args):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(msg.server)
        if not state.is_playing():
            await self.ene._send_message(msg.channel, 'Não estou tocando nenhuma musica.')
            return

        voter = msg.author
        if voter == state.current.requester:
            await self.ene._send_message(msg.channel, 'Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.ene._send_message(msg.channel, 'Já que vários querem, estou trocando de musica...')
                state.skip()
            else:
                await self.ene._send_message(msg.channel,
                                            'Seu voto foi adicionado a contagem, agora temos [{0}/3]'.format(total_votes))
        else:
            await self.ene._send_message(msg.channel, 'Você já votou.')

    @command(usage='playing', description='Mostra os dados da musica atual.')
    async def playing(self, msg, *args):
        """Shows info about the currently played song."""

        state = self.get_voice_state(msg.server)
        if state.current is None:
            await self.ene._send_message(msg.channel, 'Não estou tocando nada.')
        else:
            skip_count = len(state.skip_votes)
            await self.ene._send_message(msg.channel,
                                        'Estou tocando {0} [skips: {1}/3]\n**{0.player.url}**'.format(state.current,
                                                                                                      skip_count))

    @command(usage='playlist', description='Mostra a Playlist atual.')
    async def playlist(self, msg, *args):
        state = self.get_voice_state(msg.server)

        if state.is_playing():
            qnt = state.songs.qsize()
            if qnt > 0:
                if qnt > 10:
                    numMax = 10
                else:
                    numMax = qnt
                playlist = list(state.songs._queue)
                num = 0
                fmt = '```##  PLAYLIST  ##```\n'
                while (num < numMax):
                    fmt += '    **[Musica: {0}/{1}]** '.format(num + 1, qnt) + str(playlist[num]) + '\n'
                    num += 1
                await self.ene._send_message(msg.channel, fmt)

    async def get_video_data(self, msg, url, loop, **kwargs):
        use_avconv = kwargs.get('use_avconv', False)
        opts = {
            # 'format': 'bestaudio/best',
            'format': 'webm[abr>0]/bestaudio/best',
            'noplaylist': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'logtostderr': False,
            'quiet': True,
            'default_search': 'auto',
            'prefer_ffmpeg': not use_avconv
        }

        ydl = youtube_dl.YoutubeDL(opts)
        func = functools.partial(ydl.extract_info, url, download=False)
        info = await loop.run_in_executor(None, func)

        if "entries" in info:
            info = info['entries'][0]

        is_twitch = 'twitch' in url
        if is_twitch:
            title = info.get('description')
        else:
            title = info.get('title')

        playlist = PlayList(msg, ydl, info['url'], url, info.get('duration'), info.get('uploader'), title)

        return playlist

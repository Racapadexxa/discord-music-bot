import discord
from discord.ext import commands
import youtube_dl
from youtube_dl import YoutubeDL

TOKEN = 'MTA1NDc1ODMzNzcwMDQzMzkzMA.GSjSkQ.M2AlMvkWOV5MBtcSZyZcE10VvHLzhga0R2eWG8'
bot = commands.Bot(command_prefix = '/', intents = discord.Intents.all())
vc = None
message = None

db = {}

def get_url(item):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try: 
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        except Exception: 
            return False
    return {'source': info['formats'][0]['url'], 'title': info['title']}

@bot.command()
async def stop(ctx):
    global db
    vc = db[ctx.guild.id][0]
    if vc:
        vc.stop()
        voice_c = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        await voice_c.disconnect()

@bot.command()
async def play(ctx, *args):
    global vc
    global message
    global db
    url = ' '.join(args)
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    m_url = get_url(url)['source']    
    m_title = get_url(url)['title']
    voice_c = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_c:
        if voice_c.is_connected():
            await voice_c.disconnect()
    if not discord.utils.get(bot.voice_clients, guild=ctx.guild):
        try:
            vc = await ctx.author.voice.channel.connect()
            db[ctx.guild.id] = [vc , 1.0]
        except:
            await ctx.send('> **Error: you must join a voice channel first**')
            return
    if vc.is_playing():
        vc.stop()
    vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS))
    vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)
    msg = await ctx.send(f'> currently playing ***{m_title}***\n')
    message = msg
    await msg.add_reaction('▶️')
    await msg.add_reaction('⏸️')
    await msg.add_reaction('🔉')
    await msg.add_reaction('🔊')
    
def pause(guild):
    global db
    vc = db[guild][0]
    if vc:
        vc.pause()

def resume(guild):
    global db
    vc = db[guild][0]
    if vc:
        vc.resume()
       
def vol_up(guild):
    global db
    vc = db[guild][0]
    if db[guild][1] <= 0.8:
        db[guild][1] = db[guild][1] + 0.2
        vc.source.volume = db[guild][1]
        
    print(db[guild][1])
    
def vol_down(guild):
    global db
    vc = db[guild][0]
    if db[guild][1] >= 0.4:
        db[guild][1] = db[guild][1] - 0.2
        vc.source.volume = db[guild][1]
    elif db[guild][1] >= 0.2 and db[guild][1] <= 0.4:
        db[guild][1] = 0
        vc.source.volume = db[guild][1]
        
        
    print(db[guild][1])
    
@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if message.author == bot.user:
        if user != bot.user:
            if reaction.emoji == '▶️':
                await reaction.remove(user)
                resume(reaction.message.guild.id)
            elif reaction.emoji == '⏸️':
                pause(reaction.message.guild.id)
                await reaction.remove(user)
            if reaction.emoji == '🔉':
                await reaction.remove(user)
                vol_down(reaction.message.guild.id)
            elif reaction.emoji == '🔊':
                vol_up(reaction.message.guild.id)
                await reaction.remove(user) 

bot.run(TOKEN)


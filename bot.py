import discord
from discord.ext import commands
import youtube_dl
from youtube_dl import YoutubeDL


#commands:
#   /play <song nome>
#   /play <song-url>
#   /stop  -it disconnects the bot and stops music, pause and resume are implemented using reaction
#   - it should work on multiple servers, but I haven't tested it

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
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
    return {'source': info['formats'][0]['url'], 'title': info['title'], 'id': info['id'], 'description': info['description']}

@bot.command()
async def stop(ctx):
    global db
    
    try:
        vc = db[ctx.guild.id][0]
        if vc:
            vc.stop()
            voice_c = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            await voice_c.disconnect()
    except:
        pass

@bot.command()
async def play(ctx, *args):
    global vc
    global message
    global db
    url = ' '.join(args)
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    m_url = get_url(url)['source']    
    m_title = get_url(url)['title']
    m_id = get_url(url)['id']
    m_description = get_url(url)['description']
    
    img_link = f'https://i.ytimg.com/vi/{m_id}/hq720.jpg'
    
    
    voice_c = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_c:
        if voice_c.is_connected():
            await voice_c.disconnect()
    if not discord.utils.get(bot.voice_clients, guild=ctx.guild):
        try:
            vc = await ctx.author.voice.channel.connect()
            db[ctx.guild.id] = [vc , 1.0]
        except:
            embed = discord.Embed(title=f'**Error: you must join a voice channel first !  **\n', color=0x000000)
            await ctx.send(embed=embed)
            return
    if vc.is_playing():
        vc.stop()
    vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS))
    vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)
    
    embed = discord.Embed(title=f' currently playing ***{m_title}***\n', description=m_description[0:50], color=0xffffff)
    try:
        embed.set_image(url=img_link)
    except:
        pass
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('▶️')
    await msg.add_reaction('⏸️')
    await msg.add_reaction('🔉')
    await msg.add_reaction('🔊')
    
def pause(guild):
    global db
    
    try:
        vc = db[guild][0]
        if vc:
            vc.pause()
    except:
        pass

def resume(guild):
    global db
    
    try:
        vc = db[guild][0]
        if vc:
            vc.resume()
    except:
        pass
       
def vol_up(guild):
    global db
    
    try:
        vc = db[guild][0]
        if db[guild][1] <= 0.8:
            db[guild][1] = db[guild][1] + 0.2
            vc.source.volume = db[guild][1]
    except:
        pass
    
def vol_down(guild):
    global db
    
    try:
        vc = db[guild][0]
        if db[guild][1] >= 0.4:
            db[guild][1] = db[guild][1] - 0.2
            vc.source.volume = db[guild][1]
        elif db[guild][1] >= 0.2 and db[guild][1] <= 0.4:
            db[guild][1] = 0
            vc.source.volume = db[guild][1]
    except:
        pass
    
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


import discord
from discord.ext import commands
from discord.utils import get
import yt_dlp
import time

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'

bot = commands.Bot(command_prefix = '/', intents = discord.Intents.all())
bot.remove_command('help')

vc = None
message = None
index = 0
db = {}

class MusicPlayerPlaying(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.v = None
        self.ctx = ctx
    
    @discord.ui.button(label = "⏪", style = discord.ButtonStyle.grey)
    async def player0(self, button:discord.ui.Button, interaction: discord.Interaction):
        try:
            if index > 0:
                await before(self.ctx, button)
            await button.response.edit_message(view=MusicPlayerPlaying(self.ctx))
        except discord.errors.NotFound:
            None

    @discord.ui.button(label = "⏸️", style = discord.ButtonStyle.grey)
    async def player2(self, button:discord.ui.Button, interaction: discord.Interaction):
        pause(self.ctx.guild.id)
        await button.response.edit_message(view=MusicPlayerStopped(self.ctx))

    @discord.ui.button(label = "⏩", style = discord.ButtonStyle.grey)
    async def player69(self, button:discord.ui.Button, interaction: discord.Interaction):
        try:
            if index < db[self.ctx.guild.id][5]:
                await afterq(self.ctx, button)
            await button.response.edit_message(view=MusicPlayerPlaying(self.ctx))
        except discord.errors.NotFound:
            None

class MusicPlayerStopped(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.v = None
        self.ctx = ctx
    @discord.ui.button(label = "⏪", style = discord.ButtonStyle.grey)
    async def player0(self, button:discord.ui.Button, interaction: discord.Interaction):
        try:
            if index > 0:
                await before(self.ctx, button)
            await button.response.edit_message(view=MusicPlayerPlaying(self.ctx))
        except discord.errors.NotFound:
            None

        
    @discord.ui.button(label = "▶️", style = discord.ButtonStyle.grey)
    async def player1(self, button:discord.ui.Button, interaction: discord.Interaction):
        resume(self.ctx.guild.id)
        await button.response.edit_message(view=MusicPlayerPlaying(self.ctx))
        
    @discord.ui.button(label = "⏩", style = discord.ButtonStyle.grey)
    async def player69(self, button:discord.ui.Button, interaction: discord.Interaction):
        try:
            if index < db[self.ctx.guild.id][5]:
                await afterq(self.ctx, button)
            await button.response.edit_message(view=MusicPlayerPlaying(self.ctx))
        except discord.errors.NotFound:
            None
            

            
def get_url(item):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
    return {'source': info['url'], 'title': info['title'], 'id': info['id'], 'description': info['description']}

@bot.command()
async def leave(ctx):
        if vc:
            if vc.is_playing():
                vc.stop()
        voice_c = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        await voice_c.disconnect()

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
async def soundboard(ctx):
    embed = discord.Embed(title='''**Succhiami la soundboard! **\n''', color=0xffffff)
    view = SoundboardUi(ctx)
    await ctx.send(embed=embed,view=view) 

    
@bot.command(aliases=['q'])
async def queue(ctx, *args):
    url = ' '.join(args)
    try:
        db[ctx.guild.id][4].append("https://www.youtube.com/watch?v=" + get_url(url)['id'])
        db[ctx.guild.id][5] = db[ctx.guild.id][5] + 1
    except:
        embed = discord.Embed(title=f'**Song was not added to the playlist**\n', color=0x000000)
        await ctx.send(embed=embed)
        return        
    
    embed = discord.Embed(title=f'**Song added successfully to the playlist**\n', color=0x000000)
    await ctx.send(embed=embed)
    return

@bot.command(aliases=['p', 'x'])
async def play(ctx, *args):
    global vc
    global message
    global db
    global index
    
    url = ' '.join(args)
    
    voice_c = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    
    index=0
    try:
        db.pop(ctx.guild.id)
    except:
        None
    
    if voice_c:
        if voice_c.is_connected():
            await voice_c.disconnect()
    
    if discord.utils.get(bot.voice_clients, guild=ctx.guild) == None:
        try:
            vc = await ctx.author.voice.channel.connect()
            
        except:
            embed = discord.Embed(title=f'**Error: you must join a voice channel first !  **\n', color=0x000000)
            await ctx.send(embed=embed)
            return
     
    if vc.is_playing():
        vc.stop()
        
    await play_song(ctx, url)
    
async def play_song(ctx,url1):
    global vc
    global message
    global db
    global index
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    if url1 == ">":
        vc.stop()
        url = db[ctx.guild.id][4][index + 1]
        index += 1
    elif url1 == "<":
        vc.stop()
        url = db[ctx.guild.id][4][index - 1]
        index -= 1
    else:
        url = url1

    try:
        x = get_url(url)
    except:
        embed = discord.Embed(title='''**Error: the video is not accessible and may have restrictions ! **\n''', color=0x000000)
        await ctx.send(embed=embed)
        return
    
    m_url = x['source']    
    m_title = x['title']
    m_id = x['id']
    m_description = x['description']
    
    img_link = f'https://i.ytimg.com/vi/{m_id}/hqdefault.jpg'
    
    vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: bot.loop.create_task(afterq(ctx)))
    vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)
    
    if url1 != ">" and url1 != "<":
        db[ctx.guild.id] = [vc , 1.0, m_url, "https://www.youtube.com/watch?v=" + m_id,["https://www.youtube.com/watch?v=" + m_id], 0] 
    
    embed = discord.Embed(title=f' currently playing ***{m_title}***\n', description=m_description[0:50], color=0xffffff)
    
    try:
        embed.set_image(url=img_link)
    except:
        pass
    
    view = MusicPlayerPlaying(ctx)
    await ctx.send(embed=embed,view=view)
           
async def afterq(ctx, button=""):
    global db
    global index

    if db[ctx.guild.id][5] > 0 and index < db[ctx.guild.id][5]:
        await play_song(ctx, url1=">")
    if button != "":
        await button.message.edit(view=None)

        
async def before(ctx, button):
    global db
    global index

    if db[ctx.guild.id][5] > 0 and index <= db[ctx.guild.id][5] and index > 0:
        
        await play_song(ctx, url1="<")
    await button.message.edit(view=None)


    
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
    
async def play_file(user, ctx, path):
    global vc
    voice_c = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    
    if voice_c:
        await voice_c.disconnect()
        try:
            vc = await user.voice.channel.connect()
        except:
            embed = discord.Embed(title='''**Error: Join a voice channel first ! **\n''', color=0x000000)
            await ctx.send(embed=embed)
            return
    else:
        try:
            vc = await user.voice.channel.connect()
        except:
            embed = discord.Embed(title='''**Error: Join a voice channel first ! **\n''', color=0x000000)
            await ctx.send(embed=embed)
            return        
                
        
    if vc:
        if vc.is_playing():
            vc.stop()
    
    
    vc.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path)), after=lambda e: bot.loop.create_task(getOut(ctx)))
    
async def getOut(ctx):
    await discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild).disconnect()              
                
class SoundboardUi(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
    
    @discord.ui.button(label = "🐶", style = discord.ButtonStyle.grey)
    async def player0(self, button:discord.ui.Button, interaction: discord.Interaction):
        await play_file(button.user, self.ctx,"PATH-TO-SOUND.mp3")
        
    @discord.ui.button(label = "👅", style = discord.ButtonStyle.grey)
    async def player1(self, button:discord.ui.Button, interaction: discord.Interaction):
        await play_file(button.user, self.ctx,"PATH-TO-SOUND.mp3")
        
    @discord.ui.button(label = "👼", style = discord.ButtonStyle.grey)
    async def player2(self, button:discord.ui.Button, interaction: discord.Interaction):
        await play_file(button.user, self.ctx, "PATH-TO-SOUND.mp3")
        
    @discord.ui.button(label = "🤨", style = discord.ButtonStyle.grey)
    async def player3(self, button:discord.ui.Button, interaction: discord.Interaction):
        await play_file(button.user, self.ctx, "PATH-TO-SOUND.mp3")
        
    @discord.ui.button(label = "💩", style = discord.ButtonStyle.grey)
    async def player4(self, button:discord.ui.Button, interaction: discord.Interaction):
        await play_file(button.user, self.ctx, "PATH-TO-SOUND.mp3")
        
    @discord.ui.button(label = "🇦", style = discord.ButtonStyle.grey)
    async def player5(self, button:discord.ui.Button, interaction: discord.Interaction):
        await play_file(button.user, self.ctx, "PATH-TO-SOUND.mp3")
        
    @discord.ui.button(label = "🌋", style = discord.ButtonStyle.grey)
    async def player6(self, button:discord.ui.Button, interaction: discord.Interaction):
        await play_file(button.user, self.ctx, "PATH-TO-SOUND.mp3")
        
    @discord.ui.button(label = "🚙", style = discord.ButtonStyle.grey)
    async def player7(self, button:discord.ui.Button, interaction: discord.Interaction):
        await play_file(button.user, self.ctx, "PATH-TO-SOUND.mp3")
        

                
@bot.command()
async def help(ctx):
    embed = discord.Embed(title=f'**You can use the following commands: **\n', color=0xffffff)
    embed.add_field(name="/play or /p", value="plays a song by its title or YouTube url")
    embed.add_field(name="/queue or /q", value="adds a YT video to the queue")
    embed.add_field(name="/stop or /s", value="stops the song and makes the bot quit")
    embed.add_field(name="/help", value="This command displays a list of all the commands available (not much)")
    embed.add_field(name="/soundboard", value="This command displays a soundboard with custom sounds")
    embed.add_field(name="NEWS!", value="Buttons integration & queue added :). With love by Racapadexxa")
    
    await ctx.send(embed = embed)

bot.run(TOKEN)

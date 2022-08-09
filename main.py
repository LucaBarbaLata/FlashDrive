import discord
from discord.ext import commands
import os
import random
from discord.ext.commands import has_permissions
from discord.ext.commands import has_permissions, CheckFailure
from discord.ext.commands import has_permissions, MissingPermissions
import json
from requests import get
import keep_alive


client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('I have logged in as {0.user} '.format(client))
    await client.change_presence(status=discord.Status.dnd, activity = discord.Game(name=f'.help for a list of commands! 🥳 🎉 Currently in {len(client.guilds)} servers! 🎉'))
  


@client.command(brief="Used to display the server's stats")
async def serverstats(ctx):
    embed=discord.Embed(title=f"Server Info for: {ctx.guild.name}")
    embed.add_field(name="Users:", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Channels:", value=len(ctx.guild.channels), inline=False)
    await ctx.send(embed=embed)
@client.command(brief="A calculator")
async def calculate(ctx, operation, *nums):
    if operation not in ['+', '-', '*', '/']:
        await ctx.send('Please type a valid operation type.')
    var = f' {operation} '.join(nums)
    await ctx.send(f'{var} = {eval(var)}')
@client.command(brief='A command that shows you the bot info')
async def botinfo(ctx):
  embed=discord.Embed()
  embed.add_field(name="❗ - Support Server", value="https://discord.gg/2k6PCxAMtK"    , inline=True)
  embed.add_field(name="🧑‍💻 - Bot Owners", value="Luca-rickrolled-himself#1228", inline=True)
  embed.add_field(name="🌎Website", value="morache.go.ro/wordpress/FlashDrive/home", inline=True)
  embed.add_field(name="📩 - Bot Join Date", value="1/7/2022", inline=True)
  embed.add_field(name="👋 - Invite Me", value="https://bit.ly/3P6ejzN", inline=True)
  embed.add_field(name="🖨️ - Total Guilds", value=len(client.guilds), inline=True)
  embed.add_field(name="📂 - Bot Version", value="1.0.0", inline=True)
  embed.add_field(name="🏓 - Bot Ping", value=f'{round(client.latency * 1000)}ms', inline=True)
  await ctx.send(embed=embed)

@client.command(brief="Make a small donation to the creator of this bot")
async def donate(ctx):
  link = "https://www.patreon.com/flashdrive"
  await ctx.send(link)
  
@client.command(brief="A simple clear command")
@commands.has_permissions(administrator=True)
async def clear(ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        await ctx.send(f'Cleared {limit} messages')
        await ctx.message.delete()

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You cant do that!")

@client.command(aliases=['8ball'])
async def _8ball(ctx, *, q):
  responses = ['yes', 'no', 'maybe', '...', 'problably not', 'ok']
  await ctx.send(f'Question: {q}\n Answer: {random.choice(responses)}')

@client.command(brief="Used to ban a member from the server")
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url
    await member.ban(reason=reason)
    embed=discord.Embed(title=f'User {member} has been kick')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)

@client.command(brief="Used to send you a funny meme")
async def meme(ctx):
    content = get("https://meme-api.herokuapp.com/gimme").text
    data = json.loads(content,)
    meme = discord.Embed(title=f"{data['title']}", Color = discord.Color.random()).set_image(url=f"{data['url']}")
    await ctx.reply(embed=meme)
  

@client.command(brief="Used to unbanned banned users")
@has_permissions(administrator=True)
async def unban(ctx, *, member):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url
    
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")
    
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed=discord.Embed(title=f'Unbanned {user.mention}')
            embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
            await ctx.send(embed=embed)
            return

@client.command(brief="Used to kick members from this server")
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url
    await member.kick(reason=reason)
    embed=discord.Embed(title=f'User {member} has been kicked out from this server!')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)














  
keep_alive.keep_alive()
client.run(os.environ['TOKEN'])


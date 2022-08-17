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
import asyncio
import random
import datetime
import youtube_dl
import time
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

@client.command(brief="The github page of FlashDrive")
async def source(ctx):
  link = "https://github.com/LucaBarbaLata/FlashDrive"
  await ctx.send(link)

@client.command(brief="Used to kick members from this server")
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url
    await member.kick(reason=reason)
    embed=discord.Embed(title=f'User {member} has been kicked out from this server!')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)

# Giveway part

@client.command(brief="A giveaway command", description="Say .giveaway and follow the steps")
@has_permissions(administrator=True)
async def giveaway(ctx):
    # Giveaway command requires the user to have a "Giveaway Host" role to function properly

    # Stores the questions that the bot will ask the user to answer in the channel that the command was made
    # Stores the answers for those questions in a different list
    giveaway_questions = ['Which channel will I host the giveaway in?', 'What is the prize?', 'How long should the giveaway run for (in seconds)?',]
    giveaway_answers = []

    # Checking to be sure the author is the one who answered and in which channel
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    # Askes the questions from the giveaway_questions list 1 by 1
    # Times out if the host doesn't answer within 30 seconds
    for question in giveaway_questions:
        await ctx.send(question)
        try:
            message = await client.wait_for('message', timeout= 30.0, check= check)
        except asyncio.TimeoutError:
            await ctx.send('You didn\'t answer in time.  Please try again and be sure to send your answer within 30 seconds of the question.')
            return
        else:
            giveaway_answers.append(message.content)

    # Grabbing the channel id from the giveaway_questions list and formatting is properly
    # Displays an exception message if the host fails to mention the channel correctly
    try:
        c_id = int(giveaway_answers[0][2:-1])
    except:
        await ctx.send(f'You failed to mention the channel correctly.  Please do it like this: {ctx.channel.mention}')
        return
    
    # Storing the variables needed to run the rest of the commands
    channel = client.get_channel(c_id)
    prize = str(giveaway_answers[1])
    time = int(giveaway_answers[2])

    # Sends a message to let the host know that the giveaway was started properly
    await ctx.send(f'The giveaway for {prize} will begin shortly.\nPlease direct your attention to {channel.mention}, this giveaway will end in {time} seconds.')

    # Giveaway embed message
    give = discord.Embed(color = 0x2ecc71)
    give.set_author(name = f'GIVEAWAY TIME!', icon_url = 'https://i.imgur.com/VaX0pfM.png')
    give.add_field(name= f'{ctx.author.name} is giving away: {prize}!', value = f'React with 🎉 to enter!\n Ends in {round(time/60, 2)} minutes!', inline = False)
    end = datetime.datetime.utcnow() + datetime.timedelta(seconds = time)
    give.set_footer(text = f'Giveaway ends at {end} UTC!')
    my_message = await channel.send(embed = give)
    
    # Reacts to the message
    await my_message.add_reaction("🎉")
    await asyncio.sleep(time)

    new_message = await channel.fetch_message(my_message.id)

    # Picks a winner
    users = await new_message.reactions[0].users().flatten()
    users.pop(users.index(client.user))
    winner = random.choice(users)

    # Announces the winner
    winning_announcement = discord.Embed(color = 0xff2424)
    winning_announcement.set_author(name = f'THE GIVEAWAY HAS ENDED!', icon_url= 'https://i.imgur.com/DDric14.png')
    winning_announcement.add_field(name = f'🎉 Prize: {prize}', value = f'🥳 **Winner**: {winner.mention}\n 🎫 **Number of Entrants**: {len(users)}', inline = False)
    winning_announcement.set_footer(text = 'Thanks for entering!')
    await channel.send(embed = winning_announcement)



@client.command(brief="Re roll the giveaway", description="You must enter like this: .reroll #your-channel (channel-id)")
@has_permissions(administrator=True)
async def reroll(ctx, channel: discord.TextChannel, id_ : int):
    # Reroll command requires the user to have a "Giveaway Host" role to function properly
    try:
        new_message = await channel.fetch_message(id_)
    except:
        await ctx.send("Incorrect id.")
        return
    
    # Picks a new winner
    users = await new_message.reactions[0].users().flatten()
    users.pop(users.index(client.user))
    winner = random.choice(users)

    # Announces the new winner to the server
    reroll_announcement = discord.Embed(color = 0xff2424)
    reroll_announcement.set_author(name = f'The giveaway was re-rolled by the host!', icon_url = 'https://i.imgur.com/DDric14.png')
    reroll_announcement.add_field(name = f'🥳 New Winner:', value = f'{winner.mention}', inline = False)
    await channel.send(embed = reroll_announcement)



#qr code creator

@client.command(brief="Make a qr code")
async def qr(ctx, *, data):
  import qrcode
  import image
 

  img = qrcode.make(data)
  img.save('QR_code.png')
  await ctx.reply(file=discord.File('QR_code.png'))
  

#notepad

@client.command(brief="Create a txt file")
async def create(ctx, name):
  with open(f"TXT files/{name}.txt", "w"):
    return
  await ctx.send(str(f"Txt file created with the name: {name}"))
    

@client.command(brief="Write to a txt file")
async def write(ctx, name, *, text):
  with open(f"TXT files/{name}.txt", "w") as f:
    f.write(text)
    await ctx.send(str("Saved. Type .view (file name) to view to content"))

@client.command(brief="View the content of a txt file")
async def view(ctx, name):
  with open(f"TXT files/{name}.txt", "r") as f:
    content = f.readlines()
  await ctx.send(str(f"{name}:"))
  await ctx.send(content)

@client.command(brief="Delete a txt file")
async def delete(ctx, name):
  if os.path.exists(f"TXT files/{name}.txt"):
    os.remove(f"TXT files/{name}.txt")




  
keep_alive.keep_alive()
client.run(os.environ['TOKEN'])


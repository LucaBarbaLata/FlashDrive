import discord
from discord.ext import commands
import os
import random
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


client = commands.Bot(intents=discord.Intents.all(), command_prefix='.')


@client.event
async def on_ready():
    for guild in client.guilds:
        for channel in guild.text_channels:
            if str(channel) == "general":
                print("hi")
        print('Active in {}\n Member Count : {}'.format(
            guild.name, guild.member_count))
    print('I have logged in as {0.user} '.format(client))
    await client.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(
            name=
            f'.help for a list of commands! 🥳 🎉 Currently in {len(client.guilds)} servers! 🎉'
        ))


@client.command(brief="Used to display the server's stats")
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
                    value="https://discord.gg/2k6PCxAMtK",
                    inline=True)
    embed.add_field(name="🧑‍💻 - Bot Owners",
                    value="Luca-rickrolled-himself#1228",
                    inline=True)
    embed.add_field(name="🌎Website",
                    value="morache.go.ro/wordpress/FlashDrive/home",
                    inline=True)
    embed.add_field(name="📩 - Bot Join Date", value="1/7/2022", inline=True)
    embed.add_field(name="👋 - Invite Me",
                    value="https://bit.ly/3P6ejzN",
                    inline=True)
    embed.add_field(name="🖨️ - Total Guilds",
                    value=len(client.guilds),
                    inline=True)
    embed.add_field(name="📂 - Bot Version", value="1.0.0", inline=True)
    embed.add_field(name="🏓 - Bot Ping",
                    value=f'{round(client.latency * 1000)}ms',
                    inline=True)
    await ctx.send(embed=embed)



@client.command(brief="Make a small donation to the creator of this bot")
async def donate(ctx):
    link = "https://www.patreon.com/flashdrive"
    await ctx.send(link)

@client.command()
async def fact(ctx):
  with open("facts.txt", "r") as f:
      v = f.readlines()
      await ctx.send(random.choice(v))
      return

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
    embed = discord.Embed(title=f'User {member} has been kick')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)


@client.command(brief="Used to send you a funny meme")
async def meme(ctx):
    content = get("https://meme-api.herokuapp.com/gimme").text
    data = json.loads(content, )
    meme = discord.Embed(
        title=f"{data['title']}",
        Color=discord.Color.random()).set_image(url=f"{data['url']}")
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

        if (user.name, user.discriminator) == (member_name,
                                               member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(title=f'Unbanned {user.mention}')
            embed.set_author(name=f"requested by {username_1}",
                             icon_url=avatar_1)
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
    embed = discord.Embed(
        title=f'User {member} has been kicked out from this server!')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)


# Giveway part


@client.command(brief="A giveaway command",
                description="Say .giveaway and follow the steps")
@has_permissions(administrator=True)
async def giveaway(ctx):
    # Giveaway command requires the user to have a "Giveaway Host" role to function properly

    # Stores the questions that the bot will ask the user to answer in the channel that the command was made
    # Stores the answers for those questions in a different list
    giveaway_questions = [
        'Which channel will I host the giveaway in?',
        'What is the prize?',
        'How long should the giveaway run for (in seconds)?',
    ]
    giveaway_answers = []

    # Checking to be sure the author is the one who answered and in which channel
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # Askes the questions from the giveaway_questions list 1 by 1
    # Times out if the host doesn't answer within 30 seconds
    for question in giveaway_questions:
        await ctx.send(question)
        try:
            message = await client.wait_for('message',
                                            timeout=30.0,
                                            check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                'You didn\'t answer in time.  Please try again and be sure to send your answer within 30 seconds of the question.'
            )
            return
        else:
            giveaway_answers.append(message.content)

    # Grabbing the channel id from the giveaway_questions list and formatting is properly
    # Displays an exception message if the host fails to mention the channel correctly
    try:
        c_id = int(giveaway_answers[0][2:-1])
    except:
        await ctx.send(
            f'You failed to mention the channel correctly.  Please do it like this: {ctx.channel.mention}'
        )
        return

    # Storing the variables needed to run the rest of the commands
    channel = client.get_channel(c_id)
    prize = str(giveaway_answers[1])
    time = int(giveaway_answers[2])

    # Sends a message to let the host know that the giveaway was started properly
    await ctx.send(
        f'The giveaway for {prize} will begin shortly.\nPlease direct your attention to {channel.mention}, this giveaway will end in {time} seconds.'
    )

    # Giveaway embed message
    give = discord.Embed(color=0x2ecc71)
    give.set_author(name=f'GIVEAWAY TIME!',
                    icon_url='https://i.imgur.com/VaX0pfM.png')
    give.add_field(
        name=f'{ctx.author.name} is giving away: {prize}!',
        value=f'React with 🎉 to enter!\n Ends in {round(time/60, 2)} minutes!',
        inline=False)
    end = datetime.datetime.utcnow() + datetime.timedelta(seconds=time)
    give.set_footer(text=f'Giveaway ends at {end} UTC!')
    my_message = await channel.send(embed=give)

    # Reacts to the message
    await my_message.add_reaction("🎉")
    await asyncio.sleep(time)

    new_message = await channel.fetch_message(my_message.id)

    # Picks a winner
    users = await new_message.reactions[0].users().flatten()
    users.pop(users.index(client.user))
    winner = random.choice(users)

    # Announces the winner
    winning_announcement = discord.Embed(color=0xff2424)
    winning_announcement.set_author(name=f'THE GIVEAWAY HAS ENDED!',
                                    icon_url='https://i.imgur.com/DDric14.png')
    winning_announcement.add_field(
        name=f'🎉 Prize: {prize}',
        value=
        f'🥳 **Winner**: {winner.mention}\n 🎫 **Number of Entrants**: {len(users)}',
        inline=False)
    winning_announcement.set_footer(text='Thanks for entering!')
    await channel.send(embed=winning_announcement)


@client.command(
    brief="Re roll the giveaway",
    description="You must enter like this: .reroll #your-channel (channel-id)")
@has_permissions(administrator=True)
async def reroll(ctx, channel: discord.TextChannel, id_: int):
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
    reroll_announcement = discord.Embed(color=0xff2424)
    reroll_announcement.set_author(
        name=f'The giveaway was re-rolled by the host!',
        icon_url='https://i.imgur.com/DDric14.png')
    reroll_announcement.add_field(name=f'🥳 New Winner:',
                                  value=f'{winner.mention}',
                                  inline=False)
    await channel.send(embed=reroll_announcement)


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
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title=f"{ctx.author.name}'s balance",
                       color=discord.Color.red())
    em.add_field(name="Wallet balance", value=wallet_amt)
    em.add_field(name="Bank balance", value=bank_amt)
    await ctx.send(embed=em)


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

  
#useless


@client.command(brief="Join vc.")
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()



client.run("MTAwMzYyODU3NjIyNDA3MTY4Mg.Gm57xE.xkpz5IprhDoWSwJIHcBqPIxCR2kBCE0y7UyfkU")

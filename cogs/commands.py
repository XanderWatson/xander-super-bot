import discord
from discord.ext import commands
import datetime
import random
import time
import aiohttp
import mongo_setup
from prefixes import Prefix
from googlesearch import search

mongo_setup.global_init()

def getprefix(msg) -> Prefix:
    for pref in Prefix.objects:
        if pref._guild_id == str(msg.guild.id):
            return pref._prefix

class Greetings(commands.Cog):
    '''
        Commands to greet you
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild) -> Prefix:
        pref = Prefix()
        pref._guild_name = guild.name
        pref._guild_id = str(guild.id)
        pref._prefix = "$"
        pref.save()

        channel = guild.system_channel

        if channel is not None:
            await channel.send(f"Hola! I'm Xander! Thanks for inviting me to {guild.name}.")
            await channel.send("My default prefix is $.\nUse ```$setprefix <prefix>``` to change the prefix.")

    @commands.command()
    async def hello(self, ctx):
        '''
            Says hello

            Required arguments: None
        '''
        await ctx.send(f"Hello, {ctx.author.mention}! I'm Xander, nice to meet you :smile:")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild) -> Prefix:
        Prefix.objects(_guild_id = str(guild.id)).delete()

class Moderation(commands.Cog):
    '''
        Some moderation commands
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['c', 'clr'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=2):
        '''
            Clears the specified amount of messages

            Required arguments: <amount_of_messages_to_be_deleted>

            Note: Can be used only by the members having the permission to manage messages
        '''
        if amount == 0:
            await ctx.channel.purge()
        elif amount > 0:
            await ctx.channel.purge(limit=amount)
        else:
            await ctx.send("Invalid amount specified.")

    @commands.command(aliases=['rmc'])
    @commands.has_permissions(manage_channels=True)
    async def rmchannel(self, ctx):
        '''
            Removes the current channel

            Required arguments: None

            Note: Can be used only by the moderators
        '''
        await ctx.channel.delete()

    @commands.command(aliases=['k'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason was provided."):
        '''
            Kicks the specified member from the server

            Required arguments: <mention_the_member_to_be_kicked>

            Note: Can be used only by the moderators
        '''
        await member.send(f"You've been kicked from {ctx.guild.name}. Reason - {reason}")

        channel = ctx.guild.system_channel
        await channel.send(f"{member.mention} has been kicked from this server. Reason - {reason}")

        await member.kick(reason=reason)

    @commands.command(aliases=['b'])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason was provided"):
        '''
            Bans the specified member from the server

            Required arguments: <mention_the_member_to_be_banned>

            Note: Can be used only by the moderators
        '''
        await member.send(f"You've been banned from {ctx.guild.name}. Reason - {reason}.")

        channel = ctx.guild.system_channel
        await channel.send(f"{member.mention} has been banned from this server. Reason - {reason}.")

        await member.ban(reason=reason)

    @commands.command(aliases=['bl'])
    async def banlist(self, ctx):
        '''
            Retrieves and sends the list of banned members of the server

            Required arguments: None
        '''
        banned_users = await ctx.guild.bans()

        Users = []
        for banned_entry in banned_users:
            User = str(banned_entry.user.name) + '#' + \
                str(banned_entry.user.discriminator)
            Users.append(User)

        await ctx.send('\n'.join(bannedUser for bannedUser in Users))

    @commands.command(aliases=['ub'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        '''
            Unbans the specified member from the server

            Required arguments: <username>#<discriminator>

            Note: Can be used only by the moderators
        '''
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split("#")

        channel = ctx.guild.system_channel
        for banned_entry in banned_users:
            user = banned_entry.user

            if (user.name, user.discriminator) == (member_name, member_disc):
                await ctx.guild.unban(user)
                await channel.send(f"{member_name} has been unbanned!")
                return

        await ctx.send(f"{member} not found.")


class Settings(commands.Cog):
    '''
        Some bot settings
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.content.split()[0] == "prefix":
            if msg.mentions[0] == self.bot.user:
                await msg.channel.send(f"My prefix is {getprefix(msg)}")

    @commands.command()
    async def setprefix(self, ctx, *, prefix) -> Prefix:
        '''
            Sets the specified bot prefix for the server. 

            Optional parameters: <new_prefix>
        '''
        
        for pref in Prefix.objects:
            if pref._guild_id == str(ctx.guild.id):
                pref._prefix = prefix
                pref.save()
                
        await ctx.send("Prefix successfully changed to {}".format(prefix))

    @commands.command()
    async def ping(self, ctx):
        '''
            Tells the latency or ping of the bot

            Required arguments: None
        '''
        await ctx.send(f"My ping time is: {round(self.bot.latency * 1000)} ms")

    @commands.command()
    async def dob(self, ctx):
        '''
            Tells the date of birth of Xander

            Required arguments: None
        '''
        await ctx.send("I was born on Christmas' Day, 2020")

    @commands.command(aliases=['dt'])
    async def datetime(self, ctx):
        '''
            Tells the current date and time of the server where the bot is hosted

            Required arguments: None
        '''
        await ctx.send(datetime.datetime.now())

    @commands.command(aliases = ['git'])
    async def github(self, ctx):
        await ctx.send("https://github.com/XanderWatson/xander-bot")

class Fun(commands.Cog):
    '''
        Just for fun commands
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dp(self, ctx, member: discord.Member):
        '''
            Displays the display picture of the tagged member

            Required arguments: <mention>
        '''
        if not member:
            member = ctx.author

        await ctx.send(member.avatar_url)

    @commands.command()
    async def meme(self, ctx, *, subreddit="memes"):
        '''
            Sends a random meme from the specified subreddit. Defaults to "memes"

            Optional parameters: <desired_subreddit>
        '''
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://www.reddit.com/r/{subreddit}.json") as r:
                memes = await r.json()
                embed = discord.Embed(
                    color = discord.Color.blue(),
                )
                embed.set_image(url=memes["data"]["children"][random.randint(1, 25)]["data"]["url"])
                embed.set_footer(text=f"Meme requested by {ctx.author}")
                await ctx.send(embed=embed)

    @commands.command()
    async def spam(self, ctx, amount=100, *, msg="This is a spam"):
        '''
            Spams the given message specified number of times. Defaults to 100 times "This is a spam"

            Optional parameters: <amount> <message>
        '''
        for i in range(amount):
            await ctx.send(msg)
            time.sleep(0.2)

    @commands.command(aliases=['flip', 'coin'])
    async def coinflip(self, ctx):
        '''
            Flips a coin

            Required arguments: None
        '''
        choices = ['Heads', 'Tails']

        await ctx.send(f'{choices[random.randint(0, 1)]}')

    @commands.command(aliases=['die'])
    async def dieroll(self, ctx):
        '''
            Rolls a die

            Required arguments: None
        '''
        await ctx.send(f'{random.randint(1, 6)}')

    @commands.command(aliases = ['google'])
    async def search(self, ctx, *, query):
        for s in search(query, tld='co.in', lang='en', safe='off', num=20, start=0, stop=None, pause=2):
            await ctx.send(s)

def setup(bot):
    bot.add_cog(Greetings(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(Settings(bot))
    bot.add_cog(Fun(bot))
